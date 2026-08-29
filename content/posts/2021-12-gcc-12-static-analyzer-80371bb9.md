---
title: "GCC 12 static analyzer 大致原理"
date: "2021-12-26T20:42:00.002+08:00"
updated: "2021-12-26T20:42:27.667+08:00"
permalink: "/2021/12/gcc-12-static-analyzer.html"
original_url: "https://x8795278.blogspot.com/2021/12/gcc-12-static-analyzer.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1907368215658250072"
tags: ["GCC", "static analyzer"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/GNU_Compiler_Collection_logo.svg/640px-GNU_Compiler_Collection_logo.svg.png?1606591693910")

# GCC 12 static analyzer
靜態分析器檢測流程，分析一下gcc12 目前檢測流程
# Analyzer Internals
https://gcc.gnu.org/onlinedocs/gccint/Analyzer-Internals.html

# debug gcc compiler

![](https://i.imgur.com/p6GHnq1.png)
```bash
sudo apt install gcc-multilib
sudo make -j 16 STAGE1_CXXFLAGS="-g3"
```
需要編譯 cc1 記得-g
# gdb command
```
 gdb --args cc1 test.c   -fanalyzer -Wanalyzer-double-free
```

# gcc/cgraphunit.c

```c
void
symbol_table::finalize_compilation_unit (void)
{
  timevar_push (TV_CGRAPH);

  /* If we're here there's no current function anymore.  Some frontends
     are lazy in clearing these.  */
  current_function_decl = NULL;
  set_cfun (NULL);

  /* Do not skip analyzing the functions if there were errors, we
     miss diagnostics for following functions otherwise.  */

  /* Emit size functions we didn't inline.  */
  finalize_size_functions ();

  /* Mark alias targets necessary and emit diagnostics.  */
  handle_alias_pairs ();

  if (!quiet_flag)
    {
      fprintf (stderr, "\nAnalyzing compilation unit\n");
      fflush (stderr);
    }

  if (flag_dump_passes)
    dump_passes ();

  /* Gimplify and lower all functions, compute reachability and
     remove unreachable nodes.  */
  analyze_functions (/*first_time=*/true);

  /* Mark alias targets necessary and emit diagnostics.  */
  handle_alias_pairs ();

  /* Gimplify and lower thunks.  */
  analyze_functions (/*first_time=*/false);

  /* All nested functions should be lowered now.  */
  nested_function_info::release ();

  /* Offloading requires LTO infrastructure.  */
  if (!in_lto_p && g->have_offload)
    flag_generate_offload = 1;

  if (!seen_error ())
    {
      /* Give the frontends the chance to emit early debug based on
	 what is still reachable in the TU.  */
      (*lang_hooks.finalize_early_debug) ();

      /* Clean up anything that needs cleaning up after initial debug
	 generation.  */
      debuginfo_early_start ();
      (*debug_hooks->early_finish) (main_input_filename);
      debuginfo_early_stop ();
    }

  /* Finally drive the pass manager.  */
  compile ();

  timevar_pop (TV_CGRAPH);
}
```

/mnt/c/Users/hpclab/gcc/gcc/cgraphunit.c

```c
  /* Don't run the IPA passes if there was any error or sorry messages.  */
  if (!seen_error ())
  {
    timevar_start (TV_CGRAPH_IPA_PASSES);
    ipa_passes ();
    timevar_stop (TV_CGRAPH_IPA_PASSES);
  }
```

定位至double free
# main
```bash
b /gcc/main.c:36
```

# do_compile (no_backend)
到這邊屬於前置處理器前端檢測規則部分，這行程式碼後
開始進行gimple pass流程檢查
```bash
/gcc/toplev.c:2308
```
![](https://i.imgur.com/EGqLWug.png)

# ipa_passes ()
開始處理ipa_passes
```bash
/gcc/cgraphunit.c:2529
/gcc/cgraphunit.c:2267
```
![](https://i.imgur.com/KXt7DV2.png)
![](https://i.imgur.com/az4Y7rG.png)

# execute_ipa_pass_list (opt_pass *pass)
走 Lto流程，開始遍歷所有Pass,發現 pass_analyzer 分析器
![](https://i.imgur.com/KoE4XI2.png)

# (anonymous namespace)::pass_analyzer::gate

```bash
b /gcc/analyzer/analyzer-pass.cc:78
```
![](https://i.imgur.com/DzGRWsJ.png)

# (anonymous namespace)::pass_analyzer::execute

```bash
/gcc/analyzer/analyzer-pass.cc:87
```
![](https://i.imgur.com/gjZPzKG.png)

# ana::run_checkers ();
可以看到這邊在建立supergraph
We can identify problems directly when processing a <point, state> instance. For example, if we’re finding the successors of

   <point: before-stmt: "free (ptr);",
    state: {"ptr": freed}>
```bash
/gcc/analyzer/engine.cc:5436
```
![](https://i.imgur.com/qfKa79F.png)

# ana::make_malloc_state_machine
狀態機，
state: {"ptr": freed}>
ptr可能是 malloc
假設更新兩次就是double-free
```bash
/gcc/analyzer/sm-malloc.cc:2067
```

# make_checkers
```bash
/gcc/analyzer/sm.cc:169
```
![](https://i.imgur.com/xnlDTBN.png)

# process_worklist
/* The main loop of the analysis.
   Take freshly-created exploded_nodes from the worklist, calling
   process_node on them to explore the <point, state> graph.
   Add edges to their successors, potentially creating new successors
   (which are also added to the worklist).  */
```bash
/gcc/analyzer/engine.cc:2825
```

![](https://i.imgur.com/KfUfz2N.png)

# malloc_state_machine::on_stmt
從process_worklist 觀察callstack
可以發現這邊是每個stmt都會觸發這個on_stmt function

```bash
(gdb) bt
#0  ana::(anonymous namespace)::malloc_state_machine::on_stmt (this=0x2589950, sm_ctxt=0x7ffffffeceb0, node=0x2567d30,
    stmt=0x7ffffed51090) at ../../gcc/analyzer/sm-malloc.cc:1574
#1  0x0000000000ef26b0 in ana::exploded_node::on_stmt (this=<optimized out>, eg=..., snode=0x2567d30,
    stmt=0x7ffffed51090, state=0x7ffffffecfb0, uncertainty=<optimized out>, path_ctxt=0x7ffffffed030)
    at ../../gcc/analyzer/engine.cc:1310
#2  0x0000000000ef4e2c in ana::exploded_graph::process_node (this=0x7ffffffed370, node=0x25d6530)
    at ../../gcc/analyzer/engine.cc:3366
#3  0x0000000000ef5be3 in ana::exploded_graph::process_worklist (this=0x7ffffffed370)
```

![](https://i.imgur.com/dYw6iLm.png)
# dump gimple stmt
```bahs
 p debug(stmt)
```
![](https://i.imgur.com/YSsqmJT.png)
c

可以看到on_stmt這個fucntion
有看到已經開始整合c++的部分
根據 function name

# c++
```c
	if (is_named_call_p (callee_fndecl, "operator new", call, 1))
	  on_allocator_call (sm_ctxt, call, &m_scalar_delete);
	else if (is_named_call_p (callee_fndecl, "operator new []", call, 1))
	  on_allocator_call (sm_ctxt, call, &m_vector_delete);
	else if (is_named_call_p (callee_fndecl, "operator delete", call, 1)
		 || is_named_call_p (callee_fndecl, "operator delete", call, 2))
```

# c
```c
	if (is_named_call_p (callee_fndecl, "free", call, 1)
	    || is_std_named_call_p (callee_fndecl, "free", call, 1)
	    || is_named_call_p (callee_fndecl, "__builtin_free", call, 1))
	  {
	    on_deallocator_call (sm_ctxt, node, call,
				 &m_free.m_deallocator, 0);
	    return true;
	  }

	if (is_named_call_p (callee_fndecl, "realloc", call, 2)
	    || is_named_call_p (callee_fndecl, "__builtin_realloc", call, 2))
	  {
	    on_realloc_call (sm_ctxt, node, call);
	    return true;
	  }

```
![](https://i.imgur.com/J1xOugW.png)
![](https://i.imgur.com/yBDz4jz.png)

# malloc_state_machine::on_deallocator_call
```c
b malloc_state_machine::on_deallocator_call
```
可以看到每次on_stmt 後就會更新一次節點，假設是free function 就on_deallocator_call 檢查一次看

state: {"ptr": freed}> 是否已經 m_freed 有則觸發 double-free檢測規則
```c

  else if (state == d->m_freed)
    {
      /* freed -> stop, with warning.  */
      tree diag_arg = sm_ctxt->get_diagnostic_tree (arg);
      sm_ctxt->warn (node, call, arg,
		     new double_free (*this, diag_arg, d->m_name));
      sm_ctxt->set_next_state (call, arg, m_stop);
    }
```

#  double_free
```c
b double_free
```
到這邊已經可以看到假設在on_deallocator_call 檢查發生有double-free問題則新增cwe漏洞 415 double free
```c
  bool emit (rich_location *rich_loc) FINAL OVERRIDE
  {
    auto_diagnostic_group d;
    diagnostic_metadata m;
    m.add_cwe (415); /* CWE-415: Double Free.  */
    return warning_meta (rich_loc, m, OPT_Wanalyzer_double_free,
			 "double-%qs of %qE", m_funcname, m_arg);
  }
```

顯示報錯

warning_meta (rich_loc, m, OPT_Wanalyzer_double_free,
			 "double-%qs of %qE", m_funcname, m_arg);
![](https://i.imgur.com/Vw3YChn.png)

![](https://i.imgur.com/36YeRpA.png)
![](https://i.imgur.com/V9qeARi.png)
![](https://i.imgur.com/BU36IZz.png)

