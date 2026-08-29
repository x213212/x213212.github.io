---
title: "custom gcc plugin rtl unroll loop ,inline pass"
date: "2022-12-07T22:02:00.004+08:00"
updated: "2022-12-08T23:30:36.714+08:00"
permalink: "/2022/12/gcc-plugin-rtl-unroll-loop-inline-pass.html"
original_url: "https://x8795278.blogspot.com/2022/12/gcc-plugin-rtl-unroll-loop-inline-pass.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8905873189315242106"
tags: ["GCC", "inline", "pass", "rtl", "unroll loop"]
layout: post
---

![](https://i.imgur.com/bHz8ih9.png)

# gcc plugin
![](https://i.imgur.com/bHz8ih9.png)

補足之前，影響fucntion 是否inline 版本，額外新增了可以影響unroll loop rtl層 pass的撰寫，這邊一併附上
這次比較特別趕上了chatgtp,rtl pass 這部分語法都是透過chatgpt幫助下進行撰寫，基本上不當機的情況下都快變成google 2.0了，包括這個文章都是用chatgpt產生，但是要注意除非你是領域上的專家，否則對chatgpt要進行提問的時候要用引導的方式，否則他有可能會湊答案.

在研究gcc 和 clang optcion 中其實在程式碼分析中，其時候都可以個別下
```
-fsave-optimization-record
```
將優化結果重新存成檔案，像是
clang 是一個yaml 檔案,gcc 是 json.gz壓縮起來

這邊以gcc來介紹，我們來下這個option
`-fopt-info-all=test`，優化結果會重定向到test檔案
以下test檔案的輸出結果
```
test.c:29:3: optimized:   Inlining test/22 into main/23 (always_inline).
test2.c:14:13: optimized:   Inlining foo2/0 into foo/1 (always_inline).
test2.c:12:13: optimized:   Inlining foo2/0 into foo/1 (always_inline).
missed:   not inlinable: main/23 -> __builtin_puts/24, function body not available
Unit growth for small function inlining: 9->9 (0%)

Inlined 0 calls, eliminated 0 functions

test.c:26:8: optimized: considering unrolling loop 1 at BB 3
test.c:26:8: note: considering unrolling loop 1 at BB 3
test.c:26:8: note: considering unrolling loop 1 at BB 3
considering unrolling loop with constant number of iterations
considering unrolling loop with runtime-computable number of iterations
test.c:26:8: optimized: loop unrolled 7 times
test.c:26:8: note: considering unrolling loop 1 at BB 3
considering unrolling loop with constant number of iterations
considering unrolling loop with runtime-computable number of iterations
test.c:26:8: optimized: loop unrolled 1 times

```
可以看到上方的資訊，在看一些unroll loop asm 就不用再仔細去看指令，只要透過觀察log中的 unroll loop 幾次即可知道。

下方為gcc 和 clang 相關的option 的網站
https://gcc.gnu.org/onlinedocs/gcc/Developer-Options.html
https://gist.github.com/aqjune/b984d4984f9325c1d5f02f322c87a00d
,剛剛的log裡面的關鍵字其實可以拿去gcc的 source code進行搜尋.
```
Inlining
considering unrolling
```
https://codebrowser.dev/gcc/gcc/loop-unroll.cc.html#_Z12unroll_loopsi
觀察gcc的 source code的程式碼片段也可以發現unroll loop 的原理，即可以完成重寫unroll loops部分

```c
/* Unroll LOOPS.  */
void
unroll_loops (int flags)
{
  bool changed = false;
  /* Now decide rest of unrolling.  */
  decide_unrolling (flags);
  /* Scan the loops, inner ones first.  */
  for (auto loop : loops_list (cfun, LI_FROM_INNERMOST))
    {
      /* And perform the appropriate transformations.  */
      switch (loop->lpt_decision.decision)
        {
        case LPT_UNROLL_CONSTANT:
          unroll_loop_constant_iterations (loop);
          changed = true;
          break;
        case LPT_UNROLL_RUNTIME:
          unroll_loop_runtime_iterations (loop);
          changed = true;
          break;
        case LPT_UNROLL_STUPID:
          unroll_loop_stupid (loop);
          changed = true;
          break;
        case LPT_NONE:
          break;
        default:
          gcc_unreachable ();
        }
    }
    if (changed)
      {
        calculate_dominance_info (CDI_DOMINATORS);
        fix_loop_structure (NULL);
      }
  iv_analysis_done ();
}
```
當然inline 的部分，也可以找到
https://github.com/gcc-mirror/gcc/blob/master/gcc/ipa-inline.cc
```c

  if (!optimize
      || flag_no_inline
      || !flag_early_inlining
      /* Never inline regular functions into always-inline functions
	 during incremental inlining.  This sucks as functions calling
	 always inline functions will get less optimized, but at the
	 same time inlining of functions calling always inline
	 function into an always inline function might introduce
	 cycles of edges to be always inlined in the callgraph.
	 We might want to be smarter and just avoid this type of inlining.  */
      || (DECL_DISREGARD_INLINE_LIMITS (node->decl)
	  && lookup_attribute ("always_inline",
			       DECL_ATTRIBUTES (node->decl))))
    ;
  else if (lookup_attribute ("flatten",
			     DECL_ATTRIBUTES (node->decl)) != NULL)
    {
      /* When the function is marked to be flattened, recursively inline
	 all calls in it.  */
      if (dump_enabled_p ())
	dump_printf (MSG_OPTIMIZED_LOCATIONS,
		     "Flattening %C\n", node);
      flatten_function (node, true, true);
      inlined = true;
    }
```
所以找到相對應的pass就可以理所當然畫葫蘆，產生相對應的pass

```c
#include "gcc-plugin.h"
#include "plugin-version.h"
#include <coretypes.h>
#include "tm.h"
#include <tree.h>
#include <tree-pass.h>
#include <tree-core.h>
#include <print-tree.h>
#include <tree-ssa-alias.h>
#include "gimple.h"
#include "gimple-iterator.h"
#include "tree-inline.h"
#include "cgraph.h"
#include "gimple-walk.h"
#include "gimple-pretty-print.h"
#include "gimple-ssa.h"
#include "context.h"
#include "tree-dfa.h"
#include "config.h"
#include "system.h"
#include <coretypes.h>
#include "insn-constants.h"
#include "options.h"
#include "backend.h"
#include "rtl.h"
#include "alloc-pool.h"
#include "ssa.h"
#include "diagnostic-core.h"
#include "fold-const.h"
#include "stor-layout.h"
#include "stmt.h"
#include "ssa-iterators.h"
#include "attribs.h"
// #include "timevar.h"
//#include "DFS.h"
#include <iostream>
#include <list>
#include "tree-pass.h"
#include "hash-map.h"
#include "gimple-predict.h"
#include "system.h"
#include "config.h"
#include "cfgloop.h"
#include <vector>
#include <time.h>
#include <sys/time.h>
#include <fstream>
#include <stack>
#include <string.h>
#include <math.h>
#include <rtl.h>
#include "tree-cfg.h"
#include "pretty-print.h"
#include "dumpfile.h"
#include "print-rtl.h"
#include <unistd.h>
#include <set>
#include "loop-unroll.h"
#include "tree-ssa-loop-niter.h"
#include <tree-ssa-loop-manip.h>
// #include "tree-flow.h"
#include "Algorithm.h"

using namespace std;

int plugin_is_GPL_compatible;

struct register_pass_info inline_passinfo;
struct register_pass_info detect_passinfo;
struct plugin_argument *argv;
int argc = 0;

const pass_data detect_pass_data =
    {
        .type = RTL_PASS, // SIMPLE_IPA_PASS,GIMPLE_PASS
        .name = "static_analyzer",
        .optinfo_flags = OPTGROUP_NONE,
        .tv_id = TV_PLUGIN_RUN,
        .properties_required = PROP_ssa,
        .properties_provided = 0,
        .properties_destroyed = 0,
        .todo_flags_start = 0,
        .todo_flags_finish = 0};

static int execute_detect(void)
{

  detect(argv, argc);

  return 0;
}
namespace
{
  class pass_ipa_detect : public ipa_opt_pass_d
  {
  public:
    pass_ipa_detect(gcc::context *ctxt)
        : ipa_opt_pass_d(detect_pass_data, ctxt,
                         NULL, /* generate_summary */
                         NULL, /* write_summary */
                         NULL, /* read_summary */
                         NULL, /* write_optimization_summary */
                         NULL, /* read_optimization_summary */
                         NULL, /* stmt_fixup */
                         0,    /* function_transform_todo_flags_start */
                         0,    /* function_transform */
                         NULL) /* variable_transform */
    {
    }
    /* opt_pass methods: */
    virtual unsigned int execute(function *) { return execute_detect(); }
    virtual pass_ipa_detect *clone() override { return this; }
  }; // class pass_ipa_inline
}
ipa_opt_pass_d *
make_pass_detect(gcc::context *ctxt)
{
  return new pass_ipa_detect(ctxt);
}

const pass_data inline_pass_data =
{
  GIMPLE_PASS, 			/* type */
  "inline_pass", 			/* name */
  OPTGROUP_INLINE, 		/* optinfo_flags */
  TV_NONE, 				/* tv_id */
  0, 					/* properties_required */
  0, 					/* properties_provided */
  0, 					/* properties_destroyed */
  0, 					/* todo_flags_start */
  0, 					/* todo_flags_finish */
};
static int test_always(void){
			insert_always_inline();
			//fprintf(stderr,"=======end=========\n");
			return false;
}
namespace {
class pass_ipa_always : public ipa_opt_pass_d
{
public:
  pass_ipa_always (gcc::context *ctxt)
    : ipa_opt_pass_d (inline_pass_data, ctxt,
                      NULL, /* generate_summary */
                      NULL, /* write_summary */
                      NULL, /* read_summary */
                      NULL, /* write_optimization_summary */
                      NULL, /* read_optimization_summary */
                      NULL, /* stmt_fixup */
                      0, /* function_transform_todo_flags_start */
                      0, /* function_transform */
                      NULL) /* variable_transform */
  {}
  /* opt_pass methods: */
  virtual unsigned int execute (function *) { return test_always (); }
  virtual pass_ipa_always* clone() override { return this; }
}; // class pass_ipa_inline
}
ipa_opt_pass_d *
make_pass_ipa_always (gcc::context *ctxt)
{
  return new pass_ipa_always (ctxt);
}

int plugin_init(struct plugin_name_args *plugin_info, struct plugin_gcc_version *version)
{

  if (!plugin_default_version_check(version, &gcc_version))
  {
    printf("incompatible gcc/plugin versions\n");
    return 1;
  }

  fprintf(stderr, "%s %s %s\n", plugin_info->full_name, version->basever, version->devphase);

  detect_passinfo.pass = make_pass_detect(g);
  detect_passinfo.reference_pass_name = "loop2_unroll";
  detect_passinfo.ref_pass_instance_number = 0;
  detect_passinfo.pos_op = PASS_POS_INSERT_BEFORE;

  inline_passinfo.pass=make_pass_ipa_always(g);
	inline_passinfo.reference_pass_name="einline";
	inline_passinfo.ref_pass_instance_number=0;
	inline_passinfo.pos_op=PASS_POS_INSERT_BEFORE;
  
  argv = plugin_info->argv;
  argc = plugin_info->argc;
  /* For now, tell the dc to expect ranges and thus to colorize the source
     lines, not just the carets/underlines.  This will be redundant
     once the C frontend generates ranges.  */

  // struct plugin_argument *argv = plugin_info->argv;
  // for (int i = 0; i <  plugin_info->argc; i++)
  // {
  //   printf("-------------------\n");
  //   printf("%s %s\n",argv[i].key,argv[i].value);
  // }

  register_callback("static_analyzer", PLUGIN_PASS_MANAGER_SETUP, NULL, &detect_passinfo);
  register_callback("exinline", PLUGIN_PASS_MANAGER_SETUP, NULL, &inline_passinfo);
  return 0;
}

```

```c
int gimplestmt_count;
/* For iterating over insns in basic block when we might remove the
   current insn.  */
/* For iterating over insns in basic block.  */
#define FOR_BB_INSNS(BB, INSN)                                            \
	for ((INSN) = BB_HEAD(BB); (INSN) && (INSN) != NEXT_INSN(BB_END(BB)); \
		 (INSN) = NEXT_INSN(INSN))

bool bb_in_loop_p(basic_block bb)
{
	return bb->loop_father->header->index != 0;
}

/* Counts number of insns inside LOOP.  */
int num_loop_insns_self(const class loop *loop)
{
	basic_block *bbs, bb;
	unsigned i, ninsns = 0;
	rtx_insn *insn;
	bbs = get_loop_body(loop);
	fprintf(stderr, "unroll once loop ===============\n");
	for (i = 0; i < loop->num_nodes; i++)
	{
		bb = bbs[i];

		FOR_BB_INSNS(bb, insn)
		if (NONDEBUG_INSN_P(insn))
		{

			rtx body = PATTERN(insn);
			int code = INSN_CODE(insn);
			fprintf(stderr, "Opcode of insn: %d\n", (code));
			const char *opcode_name2 = get_insn_name(code);
			if (opcode_name2 && code > 0)
				fprintf(stderr, "Opcode of insn: %s\n", opcode_name2);

			fprintf(stderr, "inst print ===============\n");
			fprintf(stderr, "===== of insn: %s\n", get_insn_name(GET_CODE((insn))));

			if (GET_CODE(body) == PARALLEL)
			{
				// 取得平行操作中的rtx數組的指針
				rtx *rtxs = XVEC(body, 0)->elem;
				fprintf(stderr, "===== of insn: %s\n", get_insn_name(GET_CODE(body)));
				// 遍歷rtx數組
				for (int i = 0; i < XVECLEN(body, 0); i++)
				{
					// 取得第i個rtx
					rtx x = rtxs[i];

					fprintf(stderr, "===== of insn: %s\n", get_insn_name(GET_CODE(x)));
					// 在這裡對rtx進行展開...
				}
			}
			fprintf(stderr, "inst print ===============\n");
				debug(insn);
			ninsns++;
		}
		fprintf(stderr, "unroll once loop ==============\n");
		// break;
	}
	free(bbs);
	if (!ninsns)
		ninsns = 1; /* To avoid division by zero.  */
	return ninsns;
}
void printfBasicblock()
{

	basic_block bb;
	struct cgraph_node *node;
	const char *name;
	class loop *loop;

	/* Scan the loops, inner ones first.  */
	FOR_EACH_LOOP(loop, LI_FROM_INNERMOST)
	{
		dump_flags_t report_flags = MSG_OPTIMIZED_LOCATIONS | TDF_DETAILS;
		dump_user_location_t locus = get_loop_location(loop);

		fprintf(stderr, "<loop info>:\n");
		if (dump_enabled_p())
		{
		
  
			edge exit = loop_latch_edge(loop);
			// find_loop_niter(loop, my_edge);
			// class control_edge *edge = get_loop_control_edge (loop);
			loop->ninsns = num_loop_insns(loop);
			loop->av_ninsns = average_num_loop_insns(loop);
			loop->lpt_decision.decision = LPT_UNROLL_CONSTANT;
			loop->lpt_decision.times = 15;
			// loop in
			loop->unroll =16;
			// class tree_niter_desc *desc = (tree_niter_desc *)get_simple_loop_desc(loop);
			// tree_unroll_loop (loop,2, exit,desc);
			// unroll_loops(0);
			dump_printf_loc(MSG_OPTIMIZED_LOCATIONS | TDF_DETAILS, locus,
							"considering unrolling loop %d at BB %d\n", loop->num,
							loop->header->index);
			fprintf(stderr, "possiable unroll times  %d\n", loop->lpt_decision.times);
			fprintf(stderr, "loop->unroll  %d\n", loop->unroll);	
			
		}
		fprintf(stderr, "loop type: ");
	
		switch (loop->lpt_decision.decision)
		{
		case LPT_UNROLL_CONSTANT:
			fprintf(stderr, "LPT_UNROLL_CONSTANT\n");
			break;
		case LPT_UNROLL_RUNTIME:
			fprintf(stderr, "LPT_UNROLL_RUNTIME\n");
			break;
		case LPT_UNROLL_STUPID:
			fprintf(stderr, "LPT_UNROLL_STUPID\n");
			break;
		case LPT_NONE:
			fprintf(stderr, "LPT_NONE\n");
			break;
		default:
			gcc_unreachable();
			//  class niter_desc *desc = get_simple_loop_desc (loop);
			//  class tree_niter_desc desc;
		}

		fprintf(stderr, "total unroll loop inst: %d\n", num_loop_insns_self(loop));
		//   rtx_insn *insn, *orig_insn, *next;
				// loop->unroll = 1;
			// unroll_loops(0);
		fprintf(stderr, "=====================================================\n");
		unroll_loops(0);
	}
	// unroll_loops(0);
// 
	// /* Scan the loops, inner ones first.  */
	// FOR_EACH_LOOP(loop, LI_FROM_INNERMOST)
	// {
	// 	dump_flags_t report_flags = MSG_OPTIMIZED_LOCATIONS | TDF_DETAILS;
	// 	dump_user_location_t locus = get_loop_location(loop);

	// 	fprintf(stderr, "<loop info>:\n");
	// 	if (dump_enabled_p())
	// 	{
			
	// 		edge exit = loop_latch_edge(loop);
	// 		// find_loop_niter(loop, my_edge);
	// 		// class control_edge *edge = get_loop_control_edge (loop);
	// 		// loop->lpt_decision.times=3;
	// 		loop->ninsns = num_loop_insns(loop);
	// 		loop->av_ninsns = average_num_loop_insns(loop);
	// 		loop->lpt_decision.decision = LPT_UNROLL_STUPID;
	// 		loop->unroll = 1;
	// 		class tree_niter_desc *desc = (tree_niter_desc *)get_simple_loop_desc(loop);
	// 		// tree_unroll_loop (loop,2, exit,desc);
	// 		// unroll_loops(0);
	// 		dump_printf_loc(MSG_OPTIMIZED_LOCATIONS | TDF_DETAILS, locus,
	// 						"considering unrolling loop %d at BB %d\n", loop->num,
	// 						loop->header->index);
	// 		fprintf(stderr, "possiable unroll times  %d\n", loop->lpt_decision.times);
	// 	}
	// 	fprintf(stderr, "loop type: ");
	// 	switch (loop->lpt_decision.decision)
	// 	{
	// 	case LPT_UNROLL_CONSTANT:
	// 		fprintf(stderr, "LPT_UNROLL_CONSTANT\n");
	// 		break;
	// 	case LPT_UNROLL_RUNTIME:
	// 		fprintf(stderr, "LPT_UNROLL_RUNTIME\n");
	// 		break;
	// 	case LPT_UNROLL_STUPID:
	// 		fprintf(stderr, "LPT_UNROLL_STUPID\n");
	// 		break;
	// 	case LPT_NONE:
	// 		fprintf(stderr, "LPT_NONE\n");
	// 		break;
	// 	default:
	// 		gcc_unreachable();
	// 		//  class niter_desc *desc = get_simple_loop_desc (loop);
	// 		//  class tree_niter_desc desc;
	// 	}

	// 	fprintf(stderr, "total unroll loop inst: %d\n", num_loop_insns_self(loop));
	// 	//   rtx_insn *insn, *orig_insn, *next;
	// 	fprintf(stderr, "=====================================================\n");
	// }
	fprintf(stderr, "\n===============Print ALL GIMPLE IR=================\n");
	FOR_EACH_FUNCTION(node)
	{
		if (!gimple_has_body_p(node->decl))
			continue;
		push_cfun(node->get_fun());

		if (cfun == NULL)
		{
			pop_cfun();
			continue;
		}
		name = get_name(cfun->decl);

		if (name != NULL)
		{
			fprintf(stderr, "=======Mapping node_fun:%s=========\n", name);
		}

		calculate_dominance_info(CDI_DOMINATORS);

		FOR_EACH_BB_FN(bb, cfun)
		{
			fprintf(stderr, "\n bb index %d \n", bb->index);
			fprintf(stderr, "=======is loop:%d=========\n", bb_in_loop_p(bb));
			// fprintf(stderr, "possiable unroll times %d\n",
			// 		bb->loop_father->lpt_decision.times);
			rtx_insn *insn;
				FOR_BB_INSNS(bb,insn)
					debug(insn);
		}

		pop_cfun();
	}
	fprintf(stderr, "\n===============Print ALL GIMPLE IR=================\n");
}

void detect(struct plugin_argument *argv, int argc) { printfBasicblock(); }

void insert_always_inline()
{
	cgraph_node *node;
	const char *name;
	bool always_inline;
	// fprintf(stderr,"=======inline=========\n");

	FOR_EACH_DEFINED_FUNCTION(node)
	{
		basic_block bb;
		cgraph_edge *e;
		fprintf(stderr, "=======caller:%s=========\n", get_name(cfun->decl));

		tree attr;
		enum availability avail;
		// name = get_name(cfun->decl);
		// 	if (name == NULL)
		// 		continue;
		// if (DECL_ATTRIBUTES(cfun->decl) == NULL)
		// 	{

		// 	}else
		// if(!strcmp(name, "MUL")){
		// 	DECL_ATTRIBUTES(cfun->decl) = tree_cons(get_identifier("always_inline"), NULL, DECL_ATTRIBUTES(cfun->decl));
		// 	DECL_DISREGARD_INLINE_LIMITS(cfun->decl) = 1;
		// }
		// for (e = node->callees; e; e = e->next_callee)
		// {

		// 	cgraph_node *caller = e->caller->inlined_to ? e->caller->inlined_to : e->caller;
		// 	cgraph_node *callee = e->callee->ultimate_alias_target(&avail, caller);
		// 	tree callee_tree = callee ? DECL_FUNCTION_SPECIFIC_OPTIMIZATION(callee->decl) : NULL;
		// 	//DECL_DISREGARD_INLINE_LIMITS (callee->decl)=1;
		// 	if (DECL_ATTRIBUTES(callee->decl) != NULL)
		// 	{
		// 		attr = get_attribute_name(DECL_ATTRIBUTES(callee->decl));
		// 		debug_tree(attr);
		// 	}
		// 	// else
		// 	// {
		// 	// 	fprintf(stderr, "=======callee:%s=========\n", get_name(callee->decl));
		// 	// 	name = get_name(caller->decl);
		// 	// 		if (name == NULL)
		// 	// 			continue;

		// 	// 	if(!strcmp(name, "MUL")){
		// 	// 		DECL_ATTRIBUTES(callee->decl) = tree_cons(get_identifier("always_inline"), NULL, DECL_ATTRIBUTES(callee->decl));
		// 	// 		DECL_DISREGARD_INLINE_LIMITS(callee->decl) = 1;
		// 	// 	}
		// 	// }
		// 	// always_inline = (DECL_DISREGARD_INLINE_LIMITS(callee->decl) && lookup_attribute("noinline", DECL_ATTRIBUTES(callee->decl)));
		// 	//fprintf(stderr,"=======%s 's address:%d %d=========\n",get_name(callee->decl),callee->decl,always_inline);
		// }

		push_cfun(DECL_STRUCT_FUNCTION(node->decl));
		if (cfun == NULL)
		{
			continue;
		}

		FOR_EACH_BB_FN(bb, cfun)
		{
			// debug_bb(bb);
			for (gimple_stmt_iterator gsi = gsi_start_bb(bb); !gsi_end_p(gsi); gsi_next(&gsi))
			{
				gimple *gc = gsi_stmt(gsi);
				// debug_gimple_stmt(gc);
				if (is_gimple_call(gc))
				{
					if (gimple_call_fn(gc) == NULL)
						continue;
					name = get_name(gimple_call_fn(gc));
					if (name == NULL)
						continue;

					fprintf(stderr, "calee fucntion %s\n", name);
					if (!strcmp(name, "free") ||
						!strcmp(name, "xfree") ||
						!strcmp(name, "malloc") ||
						!strcmp(name, "realloc") ||
						!strcmp(name, "xmalloc") ||
						!strcmp(name, "calloc") ||
						!strcmp(name, "xcalloc") ||
						!strcmp(name, "strdup") ||
						!strcmp(name, "MUL"))
					{
						always_inline = (DECL_DISREGARD_INLINE_LIMITS(node->decl) && lookup_attribute("always_inline", DECL_ATTRIBUTES(node->decl)));
						if (DECL_ATTRIBUTES(node->decl) == NULL)
							if (!always_inline)
							{
								DECL_ATTRIBUTES(node->decl) = tree_cons(get_identifier("always_inline"), NULL, DECL_ATTRIBUTES(node->decl));
								DECL_DISREGARD_INLINE_LIMITS(node->decl) = 1;
								fprintf(stderr, "calee fucntion %s will\n", name);
								fprintf(stderr, "alwayssssssssssss_inline");
								attr = get_attribute_name(DECL_ATTRIBUTES(node->decl));
								debug_tree(attr);
							}
					}
				}
			}
		}
		pop_cfun();
	}
};
```

# 重寫loop unroll loop time
經過修改大概要展開想要的次數，並不是隨心所欲，還需要先通過  decide_unrolling (flags);
這邊改起來簡單，只要設為0他就不會吃預設的次數，幫你reset
unroll_loops(0);
再來是隨你自己的意思展開某個loop次數，
```
case LPT_UNROLL_CONSTANT:
          unroll_loop_constant_iterations (loop);
     
        case LPT_UNROLL_RUNTIME:
          unroll_loop_runtime_iterations (loop);
     
        case LPT_UNROLL_STUPID:
          unroll_loop_stupid (loop);
```

```

			edge exit = loop_latch_edge(loop);
			// find_loop_niter(loop, my_edge);
			// class control_edge *edge = get_loop_control_edge (loop);
			loop->ninsns = num_loop_insns(loop);
			loop->av_ninsns = average_num_loop_insns(loop);
			loop->lpt_decision.decision = LPT_UNROLL_CONSTANT;
			loop->lpt_decision.times = 15;
			// loop in
			loop->unroll =16;
			// class tree_niter_desc *desc = (tree_niter_desc *)get_simple_loop_desc(loop);
			// tree_unroll_loop (loop,2, exit,desc);
			// unroll_loops(0);
			dump_printf_loc(MSG_OPTIMIZED_LOCATIONS | TDF_DETAILS, locus,
							"considering unrolling loop %d at BB %d\n", loop->num,
							loop->header->index);
			fprintf(stderr, "possiable unroll times  %d\n", loop->lpt_decision.times);
			fprintf(stderr, "loop->unroll  %d\n", loop->unroll);	
```
```bash
test.c:29:3: optimized:   Inlining test/22 into main/23 (always_inline).
test2.c:14:13: optimized:   Inlining foo2/0 into foo/1 (always_inline).
test2.c:12:13: optimized:   Inlining foo2/0 into foo/1 (always_inline).
missed:   not inlinable: main/23 -> __builtin_puts/24, function body not available
Unit growth for small function inlining: 11->11 (0%)

Inlined 0 calls, eliminated 0 functions

test.c:26:8: optimized: considering unrolling loop 1 at BB 3
test.c:26:8: note: considering unrolling loop 1 at BB 3
considering unrolling loop with constant number of iterations
considering unrolling loop with runtime-computable number of iterations
test.c:26:8: optimized: loop unrolled 15 times

```

