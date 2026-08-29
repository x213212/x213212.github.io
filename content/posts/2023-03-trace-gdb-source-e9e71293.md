---
title: "trace gdb source code"
date: "2023-03-07T06:26:00.002+08:00"
updated: "2023-03-07T07:11:58.761+08:00"
permalink: "/2023/03/trace-gdb-source.html"
original_url: "https://x8795278.blogspot.com/2023/03/trace-gdb-source.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7743023673305472901"
tags: ["trace gdb"]
layout: post
---

![](https://i.imgur.com/zMdFGMb.png)

# trace gdb
![](https://i.imgur.com/zMdFGMb.png)

最近在看能不能在gdb攔截一些有關於runtime的程式的pc address
,gdb背後底層原理是ptrace,大概從各個檔案裏面去埋print(printf_unfiltered (("hello\n"));)，來稍微紀錄一下
## arch
arch
資料夾存放的是有關於指令架構的一些function也就是當觸發斷點時候可以透過不同的arch將不同的register範圍讀入或讀出
例如
i386.c
```c

target_desc *
i386_create_target_description (uint64_t xcr0, bool is_linux, bool segments)
{
  target_desc_up tdesc = allocate_target_description ();

#ifndef IN_PROCESS_AGENT
  set_tdesc_architecture (tdesc.get (), "i386");
  if (is_linux)
    set_tdesc_osabi (tdesc.get (), "GNU/Linux");
#endif

  long regnum = 0;

  if (xcr0 & X86_XSTATE_X87)
    regnum = create_feature_i386_32bit_core (tdesc.get (), regnum);

  if (xcr0 & X86_XSTATE_SSE)
    regnum = create_feature_i386_32bit_sse (tdesc.get (), regnum);

  if (is_linux)
    regnum = create_feature_i386_32bit_linux (tdesc.get (), regnum);

  if (segments)
    regnum = create_feature_i386_32bit_segments (tdesc.get (), regnum);

  if (xcr0 & X86_XSTATE_AVX)
    regnum = create_feature_i386_32bit_avx (tdesc.get (), regnum);

  if (xcr0 & X86_XSTATE_MPX)
    regnum = create_feature_i386_32bit_mpx (tdesc.get (), regnum);

  if (xcr0 & X86_XSTATE_AVX512)
    regnum = create_feature_i386_32bit_avx512 (tdesc.get (), regnum);

  if (xcr0 & X86_XSTATE_PKRU)
    regnum = create_feature_i386_pkeys (tdesc.get (), regnum);

  return tdesc.release ();
}
```
...
這部分可以看到在arch資料夾根目錄可以找到相對應指令架構的描述
依我的了解debug 可以remote target 和 local端 不論如何，當發生中斷 SIGTRAP,SIGINT,、、 都會將當前的程式控制權交還給gdb,也就是程式的一些pc register都存到一個gdbarch 的結構
而arch 就算一層封裝對應到不同的arch 而讓gdb可以根據當前的使用的gdb裝置的arch更方便的存入和讀出gdbarch
然後
### amd64-linux-tdep.c
```c

void _initialize_amd64_linux_tdep ();
void
_initialize_amd64_linux_tdep ()
{
  gdbarch_register_osabi (bfd_arch_i386, bfd_mach_x86_64,
			  GDB_OSABI_LINUX, amd64_linux_init_abi);
  gdbarch_register_osabi (bfd_arch_i386, bfd_mach_x64_32,
			  GDB_OSABI_LINUX, amd64_x32_linux_init_abi);
}

```
```c
 struct gdbarch *gdbarch;
  const gdb_byte *sigtramp_code;
  CORE_ADDR pc = get_frame_pc (this_frame);
  gdb_byte buf[LINUX_SIGTRAMP_LEN];
```

```c
  gdbarch = get_frame_arch (this_frame);
  if (gdbarch_ptr_bit (gdbarch) == 32)
    sigtramp_code = amd64_x32_linux_sigtramp_code;
  else
    sigtramp_code = amd64_linux_sigtramp_code;
  if (memcmp (buf, sigtramp_code, LINUX_SIGTRAMP_LEN) != 0)
    return 0;

```
可以在某些片段發現都是再透過get_frame_pc,get_frame_arch 去取得被中斷的程式 fream 以便可以得到對應arch 程式當下的register狀態.

```c
/* From <asm/sigcontext.h>.  */
static int amd64_linux_sc_reg_offset[] =
{
  13 * 8,			/* %rax */
  11 * 8,			/* %rbx */
  14 * 8,			/* %rcx */
  12 * 8,			/* %rdx */
  9 * 8,			/* %rsi */
  8 * 8,			/* %rdi */
  10 * 8,			/* %rbp */
  15 * 8,			/* %rsp */
  0 * 8,			/* %r8 */
  1 * 8,			/* %r9 */
  2 * 8,			/* %r10 */
  3 * 8,			/* %r11 */
  4 * 8,			/* %r12 */
  5 * 8,			/* %r13 */
  6 * 8,			/* %r14 */
  7 * 8,			/* %r15 */
  16 * 8,			/* %rip */
  17 * 8,			/* %eflags */

  /* FIXME: kettenis/2002030531: The registers %cs, %fs and %gs are
     available in `struct sigcontext'.  However, they only occupy two
     bytes instead of four, which makes using them here rather
     difficult.  Leave them out for now.  */
  -1,				/* %cs */
  -1,				/* %ss */
  -1,				/* %ds */
  -1,				/* %es */
  -1,				/* %fs */
  -1				/* %gs */
};

```
socket init
```c
  amd64_x32_linux_record_tdep.size_statfs64 = 120;
  amd64_x32_linux_record_tdep.size_sockaddr = 16;
  amd64_x32_linux_record_tdep.size_int
    = gdbarch_int_bit (gdbarch) / TARGET_CHAR_BIT;
```
### amd64-linux-nat.c
net 像是一個interface ,因為amd64不只有對應linux 還有fsd ,bsd...
```c
void _initialize_amd64_linux_nat ();
void
_initialize_amd64_linux_nat ()
{
  amd64_native_gregset32_reg_offset = amd64_linux_gregset32_reg_offset;
  amd64_native_gregset32_num_regs = I386_LINUX_NUM_REGS;
  amd64_native_gregset64_reg_offset = amd64_linux_gregset_reg_offset;
  amd64_native_gregset64_num_regs = AMD64_LINUX_NUM_REGS;

  gdb_assert (ARRAY_SIZE (amd64_linux_gregset32_reg_offset)
	      == amd64_native_gregset32_num_regs);

  linux_target = &the_amd64_linux_nat_target;

  /* Add the target.  */
  add_inf_child_target (linux_target);
}
```

# debug gdb using gdb
熟悉後，可以再用gdb在去debug gdb
![](https://i.imgur.com/Ywsdq8i.png)
如果你是最上層的gdb你的cli 會顯示你是top
![](https://i.imgur.com/CML6nwI.png)

```bahs
#3  0x000000000098df7e in gdb_wait_for_event (block=1) at event-loop.cc:594
#4  gdb_do_one_event (mstimeout=mstimeout@entry=-1) at event-loop.cc:264
#5  0x00000000006af19a in start_event_loop () at main.c:412
#6  captured_command_loop () at main.c:476
#7  0x00000000006b0a65 in captured_main (data=data@entry=0x7ffc5a3546c0) at main.c:1320
#8  gdb_main (args=args@entry=0x7ffc5a3546f0) at main.c:1339
#9  0x0000000000432d95 in main (argc=<optimized out>, argv=<optimized out>) at gdb.c:32
```
```bash
Starting program: /root/x21321219/functionpro/a.out 

signal-name

signal-name

signal-name

Breakpoint 1, main () at test.c:32
32        int counter = 0;
(gdb) 
```
只要在想要觀看gdb的部分就直接在top gdb直接ctrl+c就可以暫停觀看call stack了
以剛剛的輸出也就是觸發中斷後其實gdb會一直掛在gdb_wait_for_event等待下一次指令或者中斷發生，

# cli-interp.c

```c
/* Observer for the signal_received notification.  */

static void
cli_base_on_signal_received (enum gdb_signal siggnal)
{
  SWITCH_THRU_ALL_UIS ()
    {
      cli_interp_base *cli = as_cli_interp_base (top_level_interpreter ());
      if (cli == nullptr)
	continue;

      print_signal_received_reason (cli->interp_ui_out (), siggnal);
    }
}

```
當gdb檢測到中斷觸發的時候，例如使用者ctrl+c
程式會立刻中斷，然後我們會看到
Program received signal SIGINT, Interrupt.
或者SIGTRAP等等,
## print_signal_received_reason
在後半部可以看到，這邊又是根據regcache->arch () 去得到 gdbarch，大概可以猜想的到
gdbarch假設發生中斷，一些資訊就是往這個結構做填充.    
,還有一些程式碼跑完阿一些中斷處理function 都在這個檔案內
```C
struct regcache *regcache = get_current_regcache ();
      struct gdbarch *gdbarch = regcache->arch ();
      if (gdbarch_report_signal_info_p (gdbarch)){
	gdbarch_report_signal_info (gdbarch, uiout, siggnal);
```
```C

void
print_signal_received_reason (struct ui_out *uiout, enum gdb_signal siggnal)
{
  struct thread_info *thr = inferior_thread ();

  infrun_debug_printf ("signal = %s", gdb_signal_to_string (siggnal));

  annotate_signal ();

  if (uiout->is_mi_like_p ())
    ;
  else if (show_thread_that_caused_stop ())
    {
      uiout->text ("\nThread ");
      uiout->field_string ("thread-id", print_thread_id (thr));

      const char *name = thread_name (thr);
      if (name != nullptr)
	{
	  uiout->text (" \"");
	  uiout->field_string ("name", name);
	  uiout->text ("\"");
	}
    }
  else
    uiout->text ("\nProgram");

  if (siggnal == GDB_SIGNAL_0 && !uiout->is_mi_like_p ())
    uiout->text (" stopped");
  else
    {

      uiout->text (" received signal ");
      annotate_signal_name ();
      if (uiout->is_mi_like_p ())
	uiout->field_string
	  ("reason", async_reason_lookup (EXEC_ASYNC_SIGNAL_RECEIVED));
      uiout->field_string ("signal-name", gdb_signal_to_name (siggnal));
      annotate_signal_name_end ();
      uiout->text (", ");
      annotate_signal_string ();
      uiout->field_string ("signal-meaning", gdb_signal_to_string (siggnal));

      struct regcache *regcache = get_current_regcache ();
      struct gdbarch *gdbarch = regcache->arch ();
      if (gdbarch_report_signal_info_p (gdbarch)){
	gdbarch_report_signal_info (gdbarch, uiout, siggnal);

  }

      annotate_signal_string_end ();
    }

  uiout->text (".\n");
}
```

# frame.c
剛剛有看到get_frame_pc等等fucntion 都是從gdbarch結構拿
```
CORE_ADDR
get_frame_pc (frame_info_ptr frame)
{
  gdb_assert (frame->next != NULL);
  return frame_unwind_pc (frame_info_ptr (frame->next));
}    

static CORE_ADDR
frame_unwind_pc (frame_info_ptr this_frame)
{
  
  if (this_frame->prev_pc.status == CC_UNKNOWN)
    {
      struct gdbarch *prev_gdbarch;
      CORE_ADDR pc = 0;
      bool pc_p = false;

      /* The right way.  The `pure' way.  The one true way.  This
	 method depends solely on the register-unwind code to
	 determine the value of registers in THIS frame, and hence
	 the value of this frame's PC (resume address).  A typical
	 implementation is no more than:

	 frame_unwind_register (this_frame, ISA_PC_REGNUM, buf);
	 return extract_unsigned_integer (buf, size of ISA_PC_REGNUM);

	 Note: this method is very heavily dependent on a correct
	 register-unwind implementation, it pays to fix that
	 method first; this method is frame type agnostic, since
	 it only deals with register values, it works with any
	 frame.  This is all in stark contrast to the old
	 FRAME_SAVED_PC which would try to directly handle all the
	 different ways that a PC could be unwound.  */
      prev_gdbarch = frame_unwind_arch (this_frame);

      try
	{
	  pc = gdbarch_unwind_pc (prev_gdbarch, this_frame);
	  pc_p = true;
	}
      catch (const gdb_exception_error &ex)
	{
	  if (ex.error == NOT_AVAILABLE_ERROR)
	    {
	      this_frame->prev_pc.status = CC_UNAVAILABLE;

	      frame_debug_printf ("this_frame=%d -> <unavailable>",
				  this_frame->level);
	    }
	  else if (ex.error == OPTIMIZED_OUT_ERROR)
	    {
	      this_frame->prev_pc.status = CC_NOT_SAVED;

	      frame_debug_printf ("this_frame=%d -> <not saved>",
				  this_frame->level);
	    }
	  else
	    throw;
	}

      if (pc_p)
	{
	  this_frame->prev_pc.value = pc;
	  this_frame->prev_pc.status = CC_VALUE;

	  frame_debug_printf ("this_frame=%d -> %s",
			      this_frame->level,
			      hex_string (this_frame->prev_pc.value));
	}
    }

  if (this_frame->prev_pc.status == CC_VALUE)
    return this_frame->prev_pc.value;
  else if (this_frame->prev_pc.status == CC_UNAVAILABLE)
    throw_error (NOT_AVAILABLE_ERROR, _("PC not available"));
  else if (this_frame->prev_pc.status == CC_NOT_SAVED)
    throw_error (OPTIMIZED_OUT_ERROR, _("PC not saved"));
  else
    internal_error ("unexpected prev_pc status: %d",
		    (int) this_frame->prev_pc.status);
}

```
# gdbarch
```c

CORE_ADDR
gdbarch_unwind_pc (struct gdbarch *gdbarch, frame_info_ptr next_frame)
{
  gdb_assert (gdbarch != NULL);
  gdb_assert (gdbarch->unwind_pc != NULL);
  if (gdbarch_debug >= 2)
    gdb_printf (gdb_stdlog, "gdbarch_unwind_pc called\n");
  return gdbarch->unwind_pc (gdbarch, next_frame);
}

  gdbarch_unwind_pc_ftype *unwind_pc = default_unwind_pc;
```

```c
/* See frame-unwind.h.  */

CORE_ADDR
default_unwind_pc (struct gdbarch *gdbarch, frame_info_ptr next_frame)
{
  int pc_regnum = gdbarch_pc_regnum (gdbarch);
  CORE_ADDR pc = frame_unwind_register_unsigned (next_frame, pc_regnum);
  pc = gdbarch_addr_bits_remove (gdbarch, pc);
  return pc;
}
```
```c
ULONGEST
frame_unwind_register_unsigned (frame_info_ptr next_frame, int regnum)
{
  struct gdbarch *gdbarch = frame_unwind_arch (next_frame);
  enum bfd_endian byte_order = gdbarch_byte_order (gdbarch);
  int size = register_size (gdbarch, regnum);
  struct value *value = frame_unwind_register_value (next_frame, regnum);

  gdb_assert (value != NULL);

  if (value->optimized_out ())
    {
      throw_error (OPTIMIZED_OUT_ERROR,
		   _("Register %d was not saved"), regnum);
    }
  if (!value->entirely_available ())
    {
      throw_error (NOT_AVAILABLE_ERROR,
		   _("Register %d is not available"), regnum);
    }

  ULONGEST r = extract_unsigned_integer (value->contents_all ().data (),
					 size, byte_order);

  release_value (value);
  return r;
}
```

```c

struct gdbarch *
frame_unwind_arch (frame_info_ptr next_frame)
{
  if (!next_frame->prev_arch.p)
    {
      struct gdbarch *arch;

      if (next_frame->unwind == NULL)
	frame_unwind_find_by_frame (next_frame, &next_frame->prologue_cache);

      if (next_frame->unwind->prev_arch != NULL)
	arch = next_frame->unwind->prev_arch (next_frame,
					      &next_frame->prologue_cache);
      else
	arch = get_frame_arch (next_frame);

      next_frame->prev_arch.arch = arch;
      next_frame->prev_arch.p = true;
      frame_debug_printf ("next_frame=%d -> %s",
			  next_frame->level,
			  gdbarch_bfd_arch_info (arch)->printable_name);
    }

  return next_frame->prev_arch.arch;
}
```
可以發現這邊要取得pc address，根據上面的順序還是要先找到對應的arch 才能得到相對應的arch register結構，

假設想在gdb各處取得pc address結構可不可以?
```c
  frame_info_ptr frame;
  struct gdbarch *gdbarch;
  gdbarch = get_frame_arch (frame);
      gdbarch_print_registers_info (gdbarch, gdb_stdout,
				    frame, -1, fpregs);
```
答案是不行，get_frame_arch 這個function就有做攔截
# get_frame_arch
要拿到frame還要看你在何時你的gdb 處在哪一個 level，當你不處在commad環節就會出錯
gdb_assert (m_cached_level >= -1);
或者 gdb_assert (frame_id_p (m_cached_id));
根本拿不到frame
```c

/* See frame-info-ptr.h.  */

frame_info *
frame_info_ptr::reinflate () const
{
  /* Ensure we have a valid frame level (sentinel frame or above).  */
  gdb_assert (m_cached_level >= -1);

  if (m_ptr != nullptr)
    {
      /* The frame_info wasn't invalidated, no need to reinflate.  */
      return m_ptr;
    }

  if (m_cached_id.user_created_p)
    m_ptr = create_new_frame (m_cached_id).get ();
  else
    {
      /* Frame #0 needs special handling, see comment in select_frame.  */
      if (m_cached_level == 0)
	m_ptr = get_current_frame ().get ();
      else
	{
	  /* If we reach here without a valid frame id, it means we are trying
	     to reinflate a frame whose id was not know at construction time.
	     We're probably trying to reinflate a frame while computing its id
	     which is not possible, and would indicate a problem with GDB.  */
	  gdb_assert (frame_id_p (m_cached_id));
	  m_ptr = frame_find_by_id (m_cached_id).get ();
	}
    }

  gdb_assert (m_ptr != nullptr);
  return m_ptr;
}
```
假設你在gdb合理的情況下取得frame那麼就可以來print register info結構

# gdbarch_print_registers_info
```c
  gdbarch_print_registers_info (gdbarch, gdb_stdout,
				    frame, -1, fpregs);
```

```c

/* Print out the machine register regnum.  If regnum is -1, print all
   registers (print_all == 1) or all non-float and non-vector
   registers (print_all == 0).

   For most machines, having all_registers_info() print the
   register(s) one per line is good enough.  If a different format is
   required, (eg, for MIPS or Pyramid 90x, which both have lots of
   regs), or there is an existing convention for showing all the
   registers, define the architecture method PRINT_REGISTERS_INFO to
   provide that format.  */

void
default_print_registers_info (struct gdbarch *gdbarch,
			      struct ui_file *file,
			      frame_info_ptr frame,
			      int regnum, int print_all)
{
  int i;
  const int numregs = gdbarch_num_cooked_regs (gdbarch);

  for (i = 0; i < numregs; i++)
    {
      /* Decide between printing all regs, non-float / vector regs, or
	 specific reg.  */
      if (regnum == -1)
	{
	  if (print_all)
	    {
	      if (!gdbarch_register_reggroup_p (gdbarch, i, all_reggroup))
		continue;
	    }
	  else
	    {
	      if (!gdbarch_register_reggroup_p (gdbarch, i, general_reggroup))
		continue;
	    }
	}
      else
	{
	  if (i != regnum)
	    continue;
	}

      /* If the register name is empty, it is undefined for this
	 processor, so don't display anything.  */
      if (*(gdbarch_register_name (gdbarch, i)) == '\0')
	continue;

      default_print_one_register_info (file,
				       gdbarch_register_name (gdbarch, i),
				       value_of_register (i, frame));
    }
}
```
其實這邊可以看到gdbarch_register_name 去拿一開始架構的register name做dump而已，
```c
static inline int
gdbarch_num_cooked_regs (gdbarch *arch)
{
  return gdbarch_num_regs (arch) + gdbarch_num_pseudo_regs (arch);
}
```
看你有幾個register
```c
  const int numregs = gdbarch_num_cooked_regs (gdbarch);

  for (i = 0; i < numregs; i++)
  {
      
  }
```
```c
const char *
gdbarch_register_name (struct gdbarch *gdbarch, int regnr)
{
  gdb_assert (gdbarch != NULL);
  gdb_assert (gdbarch->register_name != NULL);
  gdb_assert (regnr >= 0);
  gdb_assert (regnr < gdbarch_num_cooked_regs (gdbarch));
  if (gdbarch_debug >= 2)
    gdb_printf (gdb_stdlog, "gdbarch_register_name called\n");
  auto result = gdbarch->register_name (gdbarch, regnr);
  gdb_assert (result != nullptr);
  return result;
}
```

# breakpoint
breakpoint init
```c

void _initialize_breakpoint ();
void
_initialize_breakpoint ()
{
  struct cmd_list_element *c;

  gdb::observers::solib_unloaded.attach (disable_breakpoints_in_unloaded_shlib,
					 "breakpoint");
  gdb::observers::free_objfile.attach (disable_breakpoints_in_freed_objfile,
				       "breakpoint");
  gdb::observers::memory_changed.attach (invalidate_bp_value_on_memory_change,
					 "breakpoint");

  breakpoint_chain = 0;
  /* Don't bother to call set_breakpoint_count.  $bpnum isn't useful
     before a breakpoint is set.  */
  breakpoint_count = 0;

  tracepoint_count = 0;

  add_com ("ignore", class_breakpoint, ignore_command, _("\
Set ignore-count of breakpoint number N to COUNT.\n\
Usage is `ignore N COUNT'."));

  commands_cmd_element = add_com ("commands", class_breakpoint,
				  commands_command, _("\
Set commands to be executed when the given breakpoints are hit.\n\
Give a space-separated breakpoint list as argument after \"commands\".\n\
A list element can be a breakpoint number (e.g. `5') or a range of numbers\n\
(e.g. `5-7').\n\
With no argument, the targeted breakpoint is the last one set.\n\
The commands themselves follow starting on the next line.\n\
Type a line containing \"end\" to indicate the end of them.\n\
Give \"silent\" as the first line to make the breakpoint silent;\n\
then no output is printed when it is hit, except what the commands print."));

  const auto cc_opts = make_condition_command_options_def_group (nullptr);
  static std::string condition_command_help
    = gdb::option::build_help (_("\
Specify breakpoint number N to break only if COND is true.\n\
Usage is `condition [OPTION] N COND', where N is an integer and COND\n\
is an expression to be evaluated whenever breakpoint N is reached.\n\
\n\
Options:\n\
%OPTIONS%"), cc_opts);

  c = add_com ("condition", class_breakpoint, condition_command,
	       condition_command_help.c_str ());
  set_cmd_completer_handle_brkchars (c, condition_completer);

  c = add_com ("tbreak", class_breakpoint, tbreak_command, _("\
Set a temporary breakpoint.\n\
Like \"break\" except the breakpoint is only temporary,\n\
so it will be deleted when hit.  Equivalent to \"break\" followed\n\
by using \"enable delete\" on the breakpoint number.\n\
\n"
BREAK_ARGS_HELP ("tbreak")));
  set_cmd_completer (c, location_completer);

  c = add_com ("hbreak", class_breakpoint, hbreak_command, _("\
Set a hardware assisted breakpoint.\n\
Like \"break\" except the breakpoint requires hardware support,\n\
some target hardware may not have this support.\n\
\n"
BREAK_ARGS_HELP ("hbreak")));
  set_cmd_completer (c, location_completer);

  c = add_com ("thbreak", class_breakpoint, thbreak_command, _("\
Set a temporary hardware assisted breakpoint.\n\
Like \"hbreak\" except the breakpoint is only temporary,\n\
so it will be deleted when hit.\n\
\n"
BREAK_ARGS_HELP ("thbreak")));
  set_cmd_completer (c, location_completer);

  cmd_list_element *enable_cmd
    = add_prefix_cmd ("enable", class_breakpoint, enable_command, _("\
Enable all or some breakpoints.\n\
Usage: enable [BREAKPOINTNUM]...\n\
Give breakpoint numbers (separated by spaces) as arguments.\n\
With no subcommand, breakpoints are enabled until you command otherwise.\n\
This is used to cancel the effect of the \"disable\" command.\n\
With a subcommand you can enable temporarily."),
		      &enablelist, 1, &cmdlist);

  add_com_alias ("en", enable_cmd, class_breakpoint, 1);

  add_prefix_cmd ("breakpoints", class_breakpoint, enable_command, _("\
Enable all or some breakpoints.\n\
Usage: enable breakpoints [BREAKPOINTNUM]...\n\
Give breakpoint numbers (separated by spaces) as arguments.\n\
This is used to cancel the effect of the \"disable\" command.\n\
May be abbreviated to simply \"enable\"."),
		   &enablebreaklist, 1, &enablelist);

  add_cmd ("once", no_class, enable_once_command, _("\
Enable some breakpoints for one hit.\n\
Usage: enable breakpoints once BREAKPOINTNUM...\n\
If a breakpoint is hit while enabled in this fashion, it becomes disabled."),
	   &enablebreaklist);

  add_cmd ("delete", no_class, enable_delete_command, _("\
Enable some breakpoints and delete when hit.\n\
Usage: enable breakpoints delete BREAKPOINTNUM...\n\
If a breakpoint is hit while enabled in this fashion, it is deleted."),
	   &enablebreaklist);

  add_cmd ("count", no_class, enable_count_command, _("\
Enable some breakpoints for COUNT hits.\n\
Usage: enable breakpoints count COUNT BREAKPOINTNUM...\n\
If a breakpoint is hit while enabled in this fashion,\n\
the count is decremented; when it reaches zero, the breakpoint is disabled."),
	   &enablebreaklist);

  add_cmd ("delete", no_class, enable_delete_command, _("\
Enable some breakpoints and delete when hit.\n\
Usage: enable delete BREAKPOINTNUM...\n\
If a breakpoint is hit while enabled in this fashion, it is deleted."),
	   &enablelist);

  add_cmd ("once", no_class, enable_once_command, _("\
Enable some breakpoints for one hit.\n\
Usage: enable once BREAKPOINTNUM...\n\
If a breakpoint is hit while enabled in this fashion, it becomes disabled."),
	   &enablelist);

  add_cmd ("count", no_class, enable_count_command, _("\
Enable some breakpoints for COUNT hits.\n\
Usage: enable count COUNT BREAKPOINTNUM...\n\
If a breakpoint is hit while enabled in this fashion,\n\
the count is decremented; when it reaches zero, the breakpoint is disabled."),
	   &enablelist);

  cmd_list_element *disable_cmd
    = add_prefix_cmd ("disable", class_breakpoint, disable_command, _("\
Disable all or some breakpoints.\n\
Usage: disable [BREAKPOINTNUM]...\n\
Arguments are breakpoint numbers with spaces in between.\n\
To disable all breakpoints, give no argument.\n\
A disabled breakpoint is not forgotten, but has no effect until re-enabled."),
		      &disablelist, 1, &cmdlist);
  add_com_alias ("dis", disable_cmd, class_breakpoint, 1);
  add_com_alias ("disa", disable_cmd, class_breakpoint, 1);

  add_cmd ("breakpoints", class_breakpoint, disable_command, _("\
Disable all or some breakpoints.\n\
Usage: disable breakpoints [BREAKPOINTNUM]...\n\
Arguments are breakpoint numbers with spaces in between.\n\
To disable all breakpoints, give no argument.\n\
A disabled breakpoint is not forgotten, but has no effect until re-enabled.\n\
This command may be abbreviated \"disable\"."),
	   &disablelist);

  cmd_list_element *delete_cmd
    = add_prefix_cmd ("delete", class_breakpoint, delete_command, _("\
Delete all or some breakpoints.\n\
Usage: delete [BREAKPOINTNUM]...\n\
Arguments are breakpoint numbers with spaces in between.\n\
...
```
插入斷點
```c
int
code_breakpoint::insert_location (struct bp_location *bl)
{
  CORE_ADDR addr = bl->target_info.reqstd_address;

  bl->target_info.kind = breakpoint_kind (bl, &addr);
  bl->target_info.placed_address = addr;

  int result;
  if (bl->loc_type == bp_loc_hardware_breakpoint)
    result = target_insert_hw_breakpoint (bl->gdbarch, &bl->target_info);
  else
    result = target_insert_breakpoint (bl->gdbarch, &bl->target_info);

  if (result == 0 && bl->probe.prob != nullptr)
    {
      /* The insertion was successful, now let's set the probe's semaphore
	 if needed.  */
      bl->probe.prob->set_semaphore (bl->probe.objfile, bl->gdbarch);
    }

  return result;
}
```
看是hardware breakpoint還是 普通斷點
```c
   result = target_insert_hw_breakpoint (bl->gdbarch, &bl->target_info);
  else
    result = target_insert_breakpoint (bl->gdbarch, &bl->target_info);
```

觸發斷點，可以看到觸發斷點當然要檢查相對應的address是否對應
```c
int
code_breakpoint::breakpoint_hit (const struct bp_location *bl,
				 const address_space *aspace,
				 CORE_ADDR bp_addr,
				 const target_waitstatus &ws)
{
  
  if (ws.kind () != TARGET_WAITKIND_STOPPED
      || ws.sig () != GDB_SIGNAL_TRAP)
    return 0;

  if (!breakpoint_address_match (bl->pspace->aspace, bl->address,
				 aspace, bp_addr))
    return 0;

  if (overlay_debugging		/* unmapped overlay section */
      && section_is_overlay (bl->section)
      && !section_is_mapped (bl->section))
    return 0;

  return 1;
}

int
dprintf_breakpoint::breakpoint_hit (const struct bp_location *bl,
				    const address_space *aspace,
				    CORE_ADDR bp_addr,
				    const target_waitstatus &ws)
{
  if (dprintf_style == dprintf_style_agent
      && target_can_run_breakpoint_commands ())
    {
      /* An agent-style dprintf never causes a stop.  If we see a trap
	 for this address it must be for a breakpoint that happens to
	 be set at the same address.  */
      return 0;
    }

  return this->ordinary_breakpoint::breakpoint_hit (bl, aspace, bp_addr, ws);
}
```
比較有趣的是觸發竟然不是相對應的pc address
```c

static bool
breakpoint_address_match_range (const address_space *aspace1,
				CORE_ADDR addr1,
				int len1, const address_space *aspace2,
				CORE_ADDR addr2)
{
  return ((gdbarch_has_global_breakpoints (target_gdbarch ())
	   || aspace1 == aspace2)
	  && addr2 >= addr1 && addr2 < addr1 + len1);
}

```
再往上追bpstat_check_location
```c

/* Return true if it looks like target has stopped due to hitting
   breakpoint location BL.  This function does not check if we should
   stop, only if BL explains the stop.  */

static bool
bpstat_check_location (const struct bp_location *bl,
		       const address_space *aspace, CORE_ADDR bp_addr,
		       const target_waitstatus &ws)
{
  struct breakpoint *b = bl->owner;

  /* BL is from an existing breakpoint.  */
  gdb_assert (b != NULL);

  return b->breakpoint_hit (bl, aspace, bp_addr, ws);
}

```
這邊是程式看來已經停下來了，這邊會再檢查一次address是否正確，看來還有一層

build_bpstat_chain這邊看來就是還有一個地方是存放所有breakpoints,在這邊就可以看到一些比較常看到的指令set_breakpoint_condition,delete_breakpoint等等
```c

/* See breakpoint.h.  */

bpstat *
build_bpstat_chain (const address_space *aspace, CORE_ADDR bp_addr,
		    const target_waitstatus &ws)
{
  bpstat *bs_head = nullptr, **bs_link = &bs_head;

  for (breakpoint *b : all_breakpoints ())
    {
      if (!breakpoint_enabled (b))
	continue;

      for (bp_location *bl : b->locations ())
	{
	  /* For hardware watchpoints, we look only at the first
	     location.  The watchpoint_check function will work on the
	     entire expression, not the individual locations.  For
	     read watchpoints, the watchpoints_triggered function has
	     checked all locations already.  */
	  if (b->type == bp_hardware_watchpoint && bl != b->loc)
	    break;

	  if (!bl->enabled || bl->disabled_by_cond || bl->shlib_disabled)
	    continue;

	  if (!bpstat_check_location (bl, aspace, bp_addr, ws))
	    continue;

	  /* Come here if it's a watchpoint, or if the break address
	     matches.  */

	  bpstat *bs = new bpstat (bl, &bs_link);	/* Alloc a bpstat to
							   explain stop.  */

	  /* Assume we stop.  Should we find a watchpoint that is not
	     actually triggered, or if the condition of the breakpoint
	     evaluates as false, we'll reset 'stop' to 0.  */
	  bs->stop = true;
	  bs->print = true;

	  /* If this is a scope breakpoint, mark the associated
	     watchpoint as triggered so that we will handle the
	     out-of-scope event.  We'll get to the watchpoint next
	     iteration.  */
	  if (b->type == bp_watchpoint_scope && b->related_breakpoint != b)
	    {
	      struct watchpoint *w = (struct watchpoint *) b->related_breakpoint;

	      w->watchpoint_triggered = watch_triggered_yes;
	    }
	}
    }

  /* Check if a moribund breakpoint explains the stop.  */
  if (!target_supports_stopped_by_sw_breakpoint ()
      || !target_supports_stopped_by_hw_breakpoint ())
    {
      for (bp_location *loc : moribund_locations)
	{
	  if (breakpoint_location_address_match (loc, aspace, bp_addr)
	      && need_moribund_for_location_type (loc))
	    {
	      bpstat *bs = new bpstat (loc, &bs_link);
	      /* For hits of moribund locations, we should just proceed.  */
	      bs->stop = false;
	      bs->print = false;
	      bs->print_it = print_it_noop;
	    }
	}
    }

  return bs_head;
}

```

# infrun.c
當觸發SINGNAL時候應該會由這裡來判斷是什麼SINGNAL再決定做什麼事
```c

/* Come here when the program has stopped with a signal.  */

static void
handle_signal_stop (struct execution_control_state *ecs)
{
  
  frame_info_ptr frame;
  struct gdbarch *gdbarch;
  int stopped_by_watchpoint;
  enum stop_kind stop_soon;
  int random_signal;

  gdb_assert (ecs->ws.kind () == TARGET_WAITKIND_STOPPED);

  ecs->event_thread->set_stop_signal (ecs->ws.sig ());

  /* Do we need to clean up the state of a thread that has
     completed a displaced single-step?  (Doing so usually affects
     the PC, so do it here, before we set stop_pc.)  */
  if (finish_step_over (ecs))
    return;

  /* If we either finished a single-step or hit a breakpoint, but
     the user wanted this thread to be stopped, pretend we got a
     SIG0 (generic unsignaled stop).  */
  if (ecs->event_thread->stop_requested
      && ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP)
    ecs->event_thread->set_stop_signal (GDB_SIGNAL_0);

  ecs->event_thread->set_stop_pc
    (regcache_read_pc (get_thread_regcache (ecs->event_thread)));

  context_switch (ecs);

  if (deprecated_context_hook)
    deprecated_context_hook (ecs->event_thread->global_num);

  if (debug_infrun)
    {
      struct regcache *regcache = get_thread_regcache (ecs->event_thread);
      struct gdbarch *reg_gdbarch = regcache->arch ();

      infrun_debug_printf
	("stop_pc=%s", paddress (reg_gdbarch, ecs->event_thread->stop_pc ()));
      if (target_stopped_by_watchpoint ())
	{
	  CORE_ADDR addr;

	  infrun_debug_printf ("stopped by watchpoint");

	  if (target_stopped_data_address (current_inferior ()->top_target (),
					   &addr))
	    infrun_debug_printf ("stopped data address=%s",
				 paddress (reg_gdbarch, addr));
	  else
	    infrun_debug_printf ("(no data address available)");
	}
    }

  /* This is originated from start_remote(), start_inferior() and
     shared libraries hook functions.  */
  stop_soon = get_inferior_stop_soon (ecs);
  if (stop_soon == STOP_QUIETLY || stop_soon == STOP_QUIETLY_REMOTE)
    {
      infrun_debug_printf ("quietly stopped");
      stop_print_frame = true;
      stop_waiting (ecs);
      return;
    }

  /* This originates from attach_command().  We need to overwrite
     the stop_signal here, because some kernels don't ignore a
     SIGSTOP in a subsequent ptrace(PTRACE_CONT,SIGSTOP) call.
     See more comments in inferior.h.  On the other hand, if we
     get a non-SIGSTOP, report it to the user - assume the backend
     will handle the SIGSTOP if it should show up later.

     Also consider that the attach is complete when we see a
     SIGTRAP.  Some systems (e.g. Windows), and stubs supporting
     target extended-remote report it instead of a SIGSTOP
     (e.g. gdbserver).  We already rely on SIGTRAP being our
     signal, so this is no exception.

     Also consider that the attach is complete when we see a
     GDB_SIGNAL_0.  In non-stop mode, GDB will explicitly tell
     the target to stop all threads of the inferior, in case the
     low level attach operation doesn't stop them implicitly.  If
     they weren't stopped implicitly, then the stub will report a
     GDB_SIGNAL_0, meaning: stopped for no particular reason
     other than GDB's request.  */
  if (stop_soon == STOP_QUIETLY_NO_SIGSTOP
      && (ecs->event_thread->stop_signal () == GDB_SIGNAL_STOP
	  || ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP
	  || ecs->event_thread->stop_signal () == GDB_SIGNAL_0))
    {
      stop_print_frame = true;
      stop_waiting (ecs);
      ecs->event_thread->set_stop_signal (GDB_SIGNAL_0);
      return;
    }

  /* At this point, get hold of the now-current thread's frame.  */
  frame = get_current_frame ();
  gdbarch = get_frame_arch (frame);

  /* Pull the single step breakpoints out of the target.  */
  if (ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP)
    {
      struct regcache *regcache;
      CORE_ADDR pc;

      regcache = get_thread_regcache (ecs->event_thread);
      const address_space *aspace = regcache->aspace ();

      pc = regcache_read_pc (regcache);

      /* However, before doing so, if this single-step breakpoint was
	 actually for another thread, set this thread up for moving
	 past it.  */
      if (!thread_has_single_step_breakpoint_here (ecs->event_thread,
						   aspace, pc))
	{
	  if (single_step_breakpoint_inserted_here_p (aspace, pc))
	    {
	      infrun_debug_printf ("[%s] hit another thread's single-step "
				   "breakpoint",
				   ecs->ptid.to_string ().c_str ());
	      ecs->hit_singlestep_breakpoint = 1;
	    }
	}
      else
	{
	  infrun_debug_printf ("[%s] hit its single-step breakpoint",
			       ecs->ptid.to_string ().c_str ());
	}
    }
  delete_just_stopped_threads_single_step_breakpoints ();

  if (ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP
      && ecs->event_thread->control.trap_expected
      && ecs->event_thread->stepping_over_watchpoint)
    stopped_by_watchpoint = 0;
  else
    stopped_by_watchpoint = watchpoints_triggered (ecs->ws);

  /* If necessary, step over this watchpoint.  We'll be back to display
     it in a moment.  */
  if (stopped_by_watchpoint
      && (target_have_steppable_watchpoint ()
	  || gdbarch_have_nonsteppable_watchpoint (gdbarch)))
    {
      /* At this point, we are stopped at an instruction which has
	 attempted to write to a piece of memory under control of
	 a watchpoint.  The instruction hasn't actually executed
	 yet.  If we were to evaluate the watchpoint expression
	 now, we would get the old value, and therefore no change
	 would seem to have occurred.

	 In order to make watchpoints work `right', we really need
	 to complete the memory write, and then evaluate the
	 watchpoint expression.  We do this by single-stepping the
	 target.

	 It may not be necessary to disable the watchpoint to step over
	 it.  For example, the PA can (with some kernel cooperation)
	 single step over a watchpoint without disabling the watchpoint.

	 It is far more common to need to disable a watchpoint to step
	 the inferior over it.  If we have non-steppable watchpoints,
	 we must disable the current watchpoint; it's simplest to
	 disable all watchpoints.

	 Any breakpoint at PC must also be stepped over -- if there's
	 one, it will have already triggered before the watchpoint
	 triggered, and we either already reported it to the user, or
	 it didn't cause a stop and we called keep_going.  In either
	 case, if there was a breakpoint at PC, we must be trying to
	 step past it.  */
      ecs->event_thread->stepping_over_watchpoint = 1;
      keep_going (ecs);
      return;
    }

  ecs->event_thread->stepping_over_breakpoint = 0;
  ecs->event_thread->stepping_over_watchpoint = 0;
  bpstat_clear (&ecs->event_thread->control.stop_bpstat);
  ecs->event_thread->control.stop_step = 0;
  stop_print_frame = true;
  stopped_by_random_signal = 0;
  bpstat *stop_chain = nullptr;

  /* Hide inlined functions starting here, unless we just performed stepi or
     nexti.  After stepi and nexti, always show the innermost frame (not any
     inline function call sites).  */
  if (ecs->event_thread->control.step_range_end != 1)
    {
      const address_space *aspace
	= get_thread_regcache (ecs->event_thread)->aspace ();

      /* skip_inline_frames is expensive, so we avoid it if we can
	 determine that the address is one where functions cannot have
	 been inlined.  This improves performance with inferiors that
	 load a lot of shared libraries, because the solib event
	 breakpoint is defined as the address of a function (i.e. not
	 inline).  Note that we have to check the previous PC as well
	 as the current one to catch cases when we have just
	 single-stepped off a breakpoint prior to reinstating it.
	 Note that we're assuming that the code we single-step to is
	 not inline, but that's not definitive: there's nothing
	 preventing the event breakpoint function from containing
	 inlined code, and the single-step ending up there.  If the
	 user had set a breakpoint on that inlined code, the missing
	 skip_inline_frames call would break things.  Fortunately
	 that's an extremely unlikely scenario.  */
      if (!pc_at_non_inline_function (aspace,
				      ecs->event_thread->stop_pc (),
				      ecs->ws)
	  && !(ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP
	       && ecs->event_thread->control.trap_expected
	       && pc_at_non_inline_function (aspace,
					     ecs->event_thread->prev_pc,
					     ecs->ws)))
	{
	  stop_chain = build_bpstat_chain (aspace,
					   ecs->event_thread->stop_pc (),
					   ecs->ws);
	  skip_inline_frames (ecs->event_thread, stop_chain);

	  /* Re-fetch current thread's frame in case that invalidated
	     the frame cache.  */
	  frame = get_current_frame ();
	  gdbarch = get_frame_arch (frame);
	}
    }

  if (ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP
      && ecs->event_thread->control.trap_expected
      && gdbarch_single_step_through_delay_p (gdbarch)
      && currently_stepping (ecs->event_thread))
    {
      /* We're trying to step off a breakpoint.  Turns out that we're
	 also on an instruction that needs to be stepped multiple
	 times before it's been fully executing.  E.g., architectures
	 with a delay slot.  It needs to be stepped twice, once for
	 the instruction and once for the delay slot.  */
      int step_through_delay
	= gdbarch_single_step_through_delay (gdbarch, frame);

      if (step_through_delay)
	infrun_debug_printf ("step through delay");

      if (ecs->event_thread->control.step_range_end == 0
	  && step_through_delay)
	{
	  /* The user issued a continue when stopped at a breakpoint.
	     Set up for another trap and get out of here.  */
	 ecs->event_thread->stepping_over_breakpoint = 1;
	 keep_going (ecs);
	 return;
	}
      else if (step_through_delay)
	{
	  /* The user issued a step when stopped at a breakpoint.
	     Maybe we should stop, maybe we should not - the delay
	     slot *might* correspond to a line of source.  In any
	     case, don't decide that here, just set 
	     ecs->stepping_over_breakpoint, making sure we 
	     single-step again before breakpoints are re-inserted.  */
	  ecs->event_thread->stepping_over_breakpoint = 1;
	}
    }

  /* See if there is a breakpoint/watchpoint/catchpoint/etc. that
     handles this event.  */
  ecs->event_thread->control.stop_bpstat
    = bpstat_stop_status (get_current_regcache ()->aspace (),
			  ecs->event_thread->stop_pc (),
			  ecs->event_thread, ecs->ws, stop_chain);

  /* Following in case break condition called a
     function.  */
  stop_print_frame = true;

  /* This is where we handle "moribund" watchpoints.  Unlike
     software breakpoints traps, hardware watchpoint traps are
     always distinguishable from random traps.  If no high-level
     watchpoint is associated with the reported stop data address
     anymore, then the bpstat does not explain the signal ---
     simply make sure to ignore it if `stopped_by_watchpoint' is
     set.  */

  if (ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP
      && !bpstat_explains_signal (ecs->event_thread->control.stop_bpstat,
				  GDB_SIGNAL_TRAP)
      && stopped_by_watchpoint)
    {
      infrun_debug_printf ("no user watchpoint explains watchpoint SIGTRAP, "
			   "ignoring");
    }

  /* NOTE: cagney/2003-03-29: These checks for a random signal
     at one stage in the past included checks for an inferior
     function call's call dummy's return breakpoint.  The original
     comment, that went with the test, read:

     ``End of a stack dummy.  Some systems (e.g. Sony news) give
     another signal besides SIGTRAP, so check here as well as
     above.''

     If someone ever tries to get call dummys on a
     non-executable stack to work (where the target would stop
     with something like a SIGSEGV), then those tests might need
     to be re-instated.  Given, however, that the tests were only
     enabled when momentary breakpoints were not being used, I
     suspect that it won't be the case.

     NOTE: kettenis/2004-02-05: Indeed such checks don't seem to
     be necessary for call dummies on a non-executable stack on
     SPARC.  */

  /* See if the breakpoints module can explain the signal.  */
  random_signal
    = !bpstat_explains_signal (ecs->event_thread->control.stop_bpstat,
			       ecs->event_thread->stop_signal ());

  /* Maybe this was a trap for a software breakpoint that has since
     been removed.  */
  if (random_signal && target_stopped_by_sw_breakpoint ())
    {
      if (gdbarch_program_breakpoint_here_p (gdbarch,
					     ecs->event_thread->stop_pc ()))
	{
	  struct regcache *regcache;
	  int decr_pc;

	  /* Re-adjust PC to what the program would see if GDB was not
	     debugging it.  */
	  regcache = get_thread_regcache (ecs->event_thread);
	  decr_pc = gdbarch_decr_pc_after_break (gdbarch);
	  if (decr_pc != 0)
	    {
	      gdb::optional<scoped_restore_tmpl<int>>
		restore_operation_disable;

	      if (record_full_is_used ())
		restore_operation_disable.emplace
		  (record_full_gdb_operation_disable_set ());

	      regcache_write_pc (regcache,
				 ecs->event_thread->stop_pc () + decr_pc);
	    }
	}
      else
	{
	  /* A delayed software breakpoint event.  Ignore the trap.  */
	  infrun_debug_printf ("delayed software breakpoint trap, ignoring");
	  random_signal = 0;
	}
    }

  /* Maybe this was a trap for a hardware breakpoint/watchpoint that
     has since been removed.  */
  if (random_signal && target_stopped_by_hw_breakpoint ())
    {
      /* A delayed hardware breakpoint event.  Ignore the trap.  */
      infrun_debug_printf ("delayed hardware breakpoint/watchpoint "
			   "trap, ignoring");
      random_signal = 0;
    }

  /* If not, perhaps stepping/nexting can.  */
  if (random_signal)
    random_signal = !(ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP
		      && currently_stepping (ecs->event_thread));

  /* Perhaps the thread hit a single-step breakpoint of _another_
     thread.  Single-step breakpoints are transparent to the
     breakpoints module.  */
  if (random_signal)
    random_signal = !ecs->hit_singlestep_breakpoint;

  /* No?  Perhaps we got a moribund watchpoint.  */
  if (random_signal)
    random_signal = !stopped_by_watchpoint;

  /* Always stop if the user explicitly requested this thread to
     remain stopped.  */
  if (ecs->event_thread->stop_requested)
    {
      random_signal = 1;
      infrun_debug_printf ("user-requested stop");
    }

  /* For the program's own signals, act according to
     the signal handling tables.  */

  if (random_signal)
    {
      /* Signal not for debugging purposes.  */
      enum gdb_signal stop_signal = ecs->event_thread->stop_signal ();

      infrun_debug_printf ("random signal (%s)",
			   gdb_signal_to_symbol_string (stop_signal));

      stopped_by_random_signal = 1;

      /* Always stop on signals if we're either just gaining control
	 of the program, or the user explicitly requested this thread
	 to remain stopped.  */
      if (stop_soon != NO_STOP_QUIETLY
	  || ecs->event_thread->stop_requested
	  || signal_stop_state (ecs->event_thread->stop_signal ()))
	{
	  stop_waiting (ecs);
	  return;
	}

      /* Notify observers the signal has "handle print" set.  Note we
	 returned early above if stopping; normal_stop handles the
	 printing in that case.  */
      if (signal_print[ecs->event_thread->stop_signal ()])
	{
	  /* The signal table tells us to print about this signal.  */
	  target_terminal::ours_for_output ();
	  gdb::observers::signal_received.notify (ecs->event_thread->stop_signal ());
	  target_terminal::inferior ();
	}

      /* Clear the signal if it should not be passed.  */
      if (signal_program[ecs->event_thread->stop_signal ()] == 0)
	ecs->event_thread->set_stop_signal (GDB_SIGNAL_0);

      if (ecs->event_thread->prev_pc == ecs->event_thread->stop_pc ()
	  && ecs->event_thread->control.trap_expected
	  && ecs->event_thread->control.step_resume_breakpoint == nullptr)
	{
	  /* We were just starting a new sequence, attempting to
	     single-step off of a breakpoint and expecting a SIGTRAP.
	     Instead this signal arrives.  This signal will take us out
	     of the stepping range so GDB needs to remember to, when
	     the signal handler returns, resume stepping off that
	     breakpoint.  */
	  /* To simplify things, "continue" is forced to use the same
	     code paths as single-step - set a breakpoint at the
	     signal return address and then, once hit, step off that
	     breakpoint.  */
	  infrun_debug_printf ("signal arrived while stepping over breakpoint");

	  insert_hp_step_resume_breakpoint_at_frame (frame);
	  ecs->event_thread->step_after_step_resume_breakpoint = 1;
	  /* Reset trap_expected to ensure breakpoints are re-inserted.  */
	  ecs->event_thread->control.trap_expected = 0;

	  /* If we were nexting/stepping some other thread, switch to
	     it, so that we don't continue it, losing control.  */
	  if (!switch_back_to_stepped_thread (ecs))
	    keep_going (ecs);
	  return;
	}

      if (ecs->event_thread->stop_signal () != GDB_SIGNAL_0
	  && (pc_in_thread_step_range (ecs->event_thread->stop_pc (),
				       ecs->event_thread)
	      || ecs->event_thread->control.step_range_end == 1)
	  && (get_stack_frame_id (frame)
	      == ecs->event_thread->control.step_stack_frame_id)
	  && ecs->event_thread->control.step_resume_breakpoint == nullptr)
	{
	  /* The inferior is about to take a signal that will take it
	     out of the single step range.  Set a breakpoint at the
	     current PC (which is presumably where the signal handler
	     will eventually return) and then allow the inferior to
	     run free.

	     Note that this is only needed for a signal delivered
	     while in the single-step range.  Nested signals aren't a
	     problem as they eventually all return.  */
	  infrun_debug_printf ("signal may take us out of single-step range");

	  clear_step_over_info ();
	  insert_hp_step_resume_breakpoint_at_frame (frame);
	  ecs->event_thread->step_after_step_resume_breakpoint = 1;
	  /* Reset trap_expected to ensure breakpoints are re-inserted.  */
	  ecs->event_thread->control.trap_expected = 0;
	  keep_going (ecs);
	  return;
	}

      /* Note: step_resume_breakpoint may be non-NULL.  This occurs
	 when either there's a nested signal, or when there's a
	 pending signal enabled just as the signal handler returns
	 (leaving the inferior at the step-resume-breakpoint without
	 actually executing it).  Either way continue until the
	 breakpoint is really hit.  */

      if (!switch_back_to_stepped_thread (ecs))
	{
	  infrun_debug_printf ("random signal, keep going");

	  keep_going (ecs);
	}
      return;
    }

  process_event_stop_test (ecs);
}
```
# bpstat_stop_status
在呼叫bpstat_stop_status 又先存了gdbarch,這裡就是要檢查bp是否跟當前程式運行到的位置是否相符
```c
/* At this point, get hold of the now-current thread's frame.  */
  frame = get_current_frame ();
  gdbarch = get_frame_arch (frame);
```
```c

/* See breakpoint.h.  */

bpstat *
bpstat_stop_status (const address_space *aspace,
		    CORE_ADDR bp_addr, thread_info *thread,
		    const target_waitstatus &ws,
		    bpstat *stop_chain)
{
  struct breakpoint *b = NULL;
  /* First item of allocated bpstat's.  */
  bpstat *bs_head = stop_chain;
  bpstat *bs;
  int need_remove_insert;
  int removed_any;

  /* First, build the bpstat chain with locations that explain a
     target stop, while being careful to not set the target running,
     as that may invalidate locations (in particular watchpoint
     locations are recreated).  Resuming will happen here with
     breakpoint conditions or watchpoint expressions that include
     inferior function calls.  */
  if (bs_head == NULL)
    bs_head = build_bpstat_chain (aspace, bp_addr, ws);

  /* A bit of special processing for shlib breakpoints.  We need to
     process solib loading here, so that the lists of loaded and
     unloaded libraries are correct before we handle "catch load" and
     "catch unload".  */
  for (bs = bs_head; bs != NULL; bs = bs->next)
    {
      if (bs->breakpoint_at && bs->breakpoint_at->type == bp_shlib_event)
	{
	  handle_solib_event ();
	  break;
	}
    }

  /* Now go through the locations that caused the target to stop, and
     check whether we're interested in reporting this stop to higher
     layers, or whether we should resume the target transparently.  */

  removed_any = 0;

  for (bs = bs_head; bs != NULL; bs = bs->next)
    {
      if (!bs->stop)
	continue;

      b = bs->breakpoint_at;
      b->check_status (bs);
      if (bs->stop)
	{
	  bpstat_check_breakpoint_conditions (bs, thread);

	  if (bs->stop)
	    {
	      ++(b->hit_count);

	      /* We will stop here.  */
	      if (b->disposition == disp_disable)
		{
		  --(b->enable_count);
		  if (b->enable_count <= 0)
		    b->enable_state = bp_disabled;
		  removed_any = 1;
		}
	      gdb::observers::breakpoint_modified.notify (b);
	      if (b->silent)
		bs->print = false;
	      bs->commands = b->commands;
	      if (command_line_is_silent (bs->commands
					  ? bs->commands.get () : NULL))
		bs->print = false;

	      b->after_condition_true (bs);
	    }

	}

      /* Print nothing for this entry if we don't stop or don't
	 print.  */
      if (!bs->stop || !bs->print)
	bs->print_it = print_it_noop;
    }

  /* If we aren't stopping, the value of some hardware watchpoint may
     not have changed, but the intermediate memory locations we are
     watching may have.  Don't bother if we're stopping; this will get
     done later.  */
  need_remove_insert = 0;
  if (! bpstat_causes_stop (bs_head))
    for (bs = bs_head; bs != NULL; bs = bs->next)
      if (!bs->stop
	  && bs->breakpoint_at
	  && is_hardware_watchpoint (bs->breakpoint_at))
	{
	  struct watchpoint *w = (struct watchpoint *) bs->breakpoint_at;

	  update_watchpoint (w, false /* don't reparse.  */);
	  need_remove_insert = 1;
	}

  if (need_remove_insert)
    update_global_location_list (UGLL_MAY_INSERT);
  else if (removed_any)
    update_global_location_list (UGLL_DONT_INSERT);

  return bs_head;
}
```
```c
  /* First, build the bpstat chain with locations that explain a
     target stop, while being careful to not set the target running,
     as that may invalidate locations (in particular watchpoint
     locations are recreated).  Resuming will happen here with
     breakpoint conditions or watchpoint expressions that include
     inferior function calls.  */
  if (bs_head == NULL)
    bs_head = build_bpstat_chain (aspace, bp_addr, ws);

  /* A bit of special processing for shlib breakpoints.  We need to
     process solib loading here, so that the lists of loaded and
     unloaded libraries are correct before we handle "catch load" and
     "catch unload".  */
  for (bs = bs_head; bs != NULL; bs = bs->next)
    {
      if (bs->breakpoint_at && bs->breakpoint_at->type == bp_shlib_event)
	{
	  handle_solib_event ();
	  break;
	}
```
在gdb直接下shardlib會會問你是否要直接下，觸發事件就是在這裡
handle_solib_event ();
那我們先看
build_bpstat_chain (aspace, bp_addr, ws);
也就是gdb會先從所有斷點中，再把
再回想一下
```C
  /* See if there is a breakpoint/watchpoint/catchpoint/etc. that
     handles this event.  */
  ecs->event_thread->control.stop_bpstat
    = bpstat_stop_status (get_current_regcache ()->aspace (),
			  ecs->event_thread->stop_pc (),
			  ecs->event_thread, ecs->ws, stop_chain);
```

我們把當前程式的Aaddress 都傳進來為的就是要呼叫breakpoint裡面的address做比對，也就是在會先從build_bpstat_chain,撈出所有breakpoint 在bpstat_check_location 做檢查，當然breakpoint有各種不同的type
![](https://i.imgur.com/W5U9cpg.png)
watchpoint,breakpoint等等，
反正都是對應到(應該)
```c
int
code_breakpoint::breakpoint_hit (const struct bp_location *bl,
				 const address_space *aspace,
				 CORE_ADDR bp_addr,
				 const target_waitstatus &ws)
{
  
  if (ws.kind () != TARGET_WAITKIND_STOPPED
      || ws.sig () != GDB_SIGNAL_TRAP)
    return 0;

  if (!breakpoint_address_match (bl->pspace->aspace, bl->address,
				 aspace, bp_addr))
    return 0;

  if (overlay_debugging		/* unmapped overlay section */
      && section_is_overlay (bl->section)
      && !section_is_mapped (bl->section))
    return 0;

  return 1;
}
```
這邊又回到breakpoint_address_match
```c

/* See breakpoint.h.  */

int
breakpoint_address_match (const address_space *aspace1, CORE_ADDR addr1,
			  const address_space *aspace2, CORE_ADDR addr2)
{
  return ((gdbarch_has_global_breakpoints (target_gdbarch ())
	   || aspace1 == aspace2)
	  && addr1 == addr2);
}
```
比較pc addres 和 address_space 是否相符，相符就代表遇到斷點了，
```c
	  if (!bpstat_check_location (bl, aspace, bp_addr, ws))
	    continue;

	  /* Come here if it's a watchpoint, or if the break address
	     matches.  */

	  bpstat *bs = new bpstat (bl, &bs_link);	/* Alloc a bpstat to
							   explain stop.  */

	  /* Assume we stop.  Should we find a watchpoint that is not
	     actually triggered, or if the condition of the breakpoint
	     evaluates as false, we'll reset 'stop' to 0.  */
	  bs->stop = true;
	  bs->print = true;
```

# bpstat_check_location
```c
static bool
bpstat_check_location (const struct bp_location *bl,
		       const address_space *aspace, CORE_ADDR bp_addr,
		       const target_waitstatus &ws)
{
  struct breakpoint *b = bl->owner;

  /* BL is from an existing breakpoint.  */
  gdb_assert (b != NULL);

  return b->breakpoint_hit (bl, aspace, bp_addr, ws);
}
```
這樣就會增加到bs_head 節點上了，這樣這單個breakpoint就算生效，也就是該次的SINGAL會存到
```C
ecs->event_thread->control.stop_bpstat
```
此時該SINGAL 裡面的某個斷點bs->stop 為TRUE

```C
ecs->event_thread->control.stop_bpstat
```
設定該SIGNAL 是因為什麼而中斷
# bpstat_explains_signal
```C
  if (ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP
      && !bpstat_explains_signal (ecs->event_thread->control.stop_bpstat,
				  GDB_SIGNAL_TRAP)
      && stopped_by_watchpoint)
    {
      infrun_debug_printf ("no user watchpoint explains watchpoint SIGTRAP, "
			   "ignoring");
    }
```
# bpstat_explains_signal
```C
/* See breakpoint.h.  */

bool
bpstat_explains_signal (bpstat *bsp, enum gdb_signal sig)
{
  for (; bsp != NULL; bsp = bsp->next)
    {
      if (bsp->breakpoint_at == NULL)
	{
	  /* A moribund location can never explain a signal other than
	     GDB_SIGNAL_TRAP.  */
	  if (sig == GDB_SIGNAL_TRAP)
	    return true;
	}
      else
	{
	  if (bsp->breakpoint_at->explains_signal (sig))
	    return true;
	}
    }

  return false;
}

```

# process_event_stop_test
然後可以看到handle_signal_stop最後CALL呼叫process_event_stop_test就是對後續SINGAL處理
```c
static void
process_event_stop_test (struct execution_control_state *ecs)
{
  struct symtab_and_line stop_pc_sal;
  frame_info_ptr frame;
  struct gdbarch *gdbarch;
  CORE_ADDR jmp_buf_pc;
  struct bpstat_what what;

  /* Handle cases caused by hitting a breakpoint.  */

  frame = get_current_frame ();
  gdbarch = get_frame_arch (frame);

  what = bpstat_what (ecs->event_thread->control.stop_bpstat);

```
可以看到  what = bpstat_what (ecs->event_thread->control.stop_bpstat);
bpstat_what又回到剛剛的breakpoint來決定到底是什麼停下來

# back to breakpoint
```c

/* Prepare WHAT final decision for infrun.  */

/* Decide what infrun needs to do with this bpstat.  */

struct bpstat_what
bpstat_what (bpstat *bs_head)
{
  struct bpstat_what retval;
  bpstat *bs;

  retval.main_action = BPSTAT_WHAT_KEEP_CHECKING;
  retval.call_dummy = STOP_NONE;
  retval.is_longjmp = false;

  for (bs = bs_head; bs != NULL; bs = bs->next)
    {
      /* Extract this BS's action.  After processing each BS, we check
	 if its action overrides all we've seem so far.  */
      enum bpstat_what_main_action this_action = BPSTAT_WHAT_KEEP_CHECKING;
      enum bptype bptype;

      if (bs->breakpoint_at == NULL)
	{
	  /* I suspect this can happen if it was a momentary
	     breakpoint which has since been deleted.  */
	  bptype = bp_none;
	}
      else
	bptype = bs->breakpoint_at->type;

      switch (bptype)
	{
	case bp_none:
	  break;
	case bp_breakpoint:
	case bp_hardware_breakpoint:
	case bp_single_step:
	case bp_until:
	case bp_finish:
	case bp_shlib_event:
	  if (bs->stop)
	    {
	      if (bs->print)
		this_action = BPSTAT_WHAT_STOP_NOISY;
	      else
		this_action = BPSTAT_WHAT_STOP_SILENT;
	    }
	  else
	    this_action = BPSTAT_WHAT_SINGLE;
	  break;
	case bp_watchpoint:
	case bp_hardware_watchpoint:
	case bp_read_watchpoint:
	case bp_access_watchpoint:
	  if (bs->stop)
	    {
	      if (bs->print)
		this_action = BPSTAT_WHAT_STOP_NOISY;
	      else
		this_action = BPSTAT_WHAT_STOP_SILENT;
	    }
	  else
	    {
	      /* There was a watchpoint, but we're not stopping.
		 This requires no further action.  */
	    }
	  break;
	case bp_longjmp:
	case bp_longjmp_call_dummy:
	case bp_exception:
	  if (bs->stop)
	    {
	      this_action = BPSTAT_WHAT_SET_LONGJMP_RESUME;
	      retval.is_longjmp = bptype != bp_exception;
	    }
	  else
	    this_action = BPSTAT_WHAT_SINGLE;
	  break;
	case bp_longjmp_resume:
	case bp_exception_resume:
	  if (bs->stop)
	    {
	      this_action = BPSTAT_WHAT_CLEAR_LONGJMP_RESUME;
	      retval.is_longjmp = bptype == bp_longjmp_resume;
	    }
	  else
	    this_action = BPSTAT_WHAT_SINGLE;
	  break;
	case bp_step_resume:
	  if (bs->stop)
	    this_action = BPSTAT_WHAT_STEP_RESUME;
	  else
	    {
	      /* It is for the wrong frame.  */
	      this_action = BPSTAT_WHAT_SINGLE;
	    }
	  break;
	case bp_hp_step_resume:
	  if (bs->stop)
	    this_action = BPSTAT_WHAT_HP_STEP_RESUME;
	  else
	    {
	      /* It is for the wrong frame.  */
	      this_action = BPSTAT_WHAT_SINGLE;
	    }
	  break;
	case bp_watchpoint_scope:
	case bp_thread_event:
	case bp_overlay_event:
	case bp_longjmp_master:
	case bp_std_terminate_master:
	case bp_exception_master:
	  this_action = BPSTAT_WHAT_SINGLE;
	  break;
	case bp_catchpoint:
	  if (bs->stop)
	    {
	      if (bs->print)
		this_action = BPSTAT_WHAT_STOP_NOISY;
	      else
		this_action = BPSTAT_WHAT_STOP_SILENT;
	    }
	  else
	    {
	      /* Some catchpoints are implemented with breakpoints.
		 For those, we need to step over the breakpoint.  */
	      if (bs->bp_location_at->loc_type == bp_loc_software_breakpoint
		  || bs->bp_location_at->loc_type == bp_loc_hardware_breakpoint)
		this_action = BPSTAT_WHAT_SINGLE;
	    }
	  break;
	case bp_jit_event:
	  this_action = BPSTAT_WHAT_SINGLE;
	  break;
	case bp_call_dummy:
	  /* Make sure the action is stop (silent or noisy),
	     so infrun.c pops the dummy frame.  */
	  retval.call_dummy = STOP_STACK_DUMMY;
	  this_action = BPSTAT_WHAT_STOP_SILENT;
	  break;
	case bp_std_terminate:
	  /* Make sure the action is stop (silent or noisy),
	     so infrun.c pops the dummy frame.  */
	  retval.call_dummy = STOP_STD_TERMINATE;
	  this_action = BPSTAT_WHAT_STOP_SILENT;
	  break;
	case bp_tracepoint:
	case bp_fast_tracepoint:
	case bp_static_tracepoint:
	case bp_static_marker_tracepoint:
	  /* Tracepoint hits should not be reported back to GDB, and
	     if one got through somehow, it should have been filtered
	     out already.  */
	  internal_error (_("bpstat_what: tracepoint encountered"));
	  break;
	case bp_gnu_ifunc_resolver:
	  /* Step over it (and insert bp_gnu_ifunc_resolver_return).  */
	  this_action = BPSTAT_WHAT_SINGLE;
	  break;
	case bp_gnu_ifunc_resolver_return:
	  /* The breakpoint will be removed, execution will restart from the
	     PC of the former breakpoint.  */
	  this_action = BPSTAT_WHAT_KEEP_CHECKING;
	  break;

	case bp_dprintf:
	  if (bs->stop)
	    this_action = BPSTAT_WHAT_STOP_SILENT;
	  else
	    this_action = BPSTAT_WHAT_SINGLE;
	  break;

	default:
	  internal_error (_("bpstat_what: unhandled bptype %d"), (int) bptype);
	}

      retval.main_action = std::max (retval.main_action, this_action);
    }

  return retval;
}
```

可以看到gdb 一進來就是對所有的breakpoint做掃描 還沒開始檢查就是
bpstat_what_main_action this_action = BPSTAT_WHAT_KEEP_CHECKING;

```c
for (bs = bs_head; bs != NULL; bs = bs->next)
    {
      /* Extract this BS's action.  After processing each BS, we check
	 if its action overrides all we've seem so far.  */
      enum bpstat_what_main_action this_action = BPSTAT_WHAT_KEEP_CHECKING;
      enum bptype bptype;

      if (bs->breakpoint_at == NULL)
	{
	  /* I suspect this can happen if it was a momentary
	     breakpoint which has since been deleted.  */
	  bptype = bp_none;
	}
      else
	bptype = bs->breakpoint_at->type;

      switch (bptype)
	{
	case bp_none:
	  break;
	case bp_breakpoint:
	case bp_hardware_breakpoint:
	case bp_single_step:
	case bp_until:
	case bp_finish:
	case bp_shlib_event:
	  if (bs->stop)
	    {
	      if (bs->print)
		this_action = BPSTAT_WHAT_STOP_NOISY;
	      else
		this_action = BPSTAT_WHAT_STOP_SILENT;
	    }
	  else
	    this_action = BPSTAT_WHAT_SINGLE;
	  break;
```
那可以看到gdb可以使用slinet功能來決定要不要輸出一些ouput
```c
	case bp_breakpoint:
	case bp_hardware_breakpoint:
	case bp_single_step:
	case bp_until:
	case bp_finish:
	case bp_shlib_event:
	  if (bs->stop)
	    {
	      if (bs->print)
		this_action = BPSTAT_WHAT_STOP_NOISY;
	      else
		this_action = BPSTAT_WHAT_STOP_SILENT;
	    }
	  else
	    this_action = BPSTAT_WHAT_SINGLE;
	  break;
```
假設我們剛剛斷點成功觸發也就代表bs->stop = TRUE
也就是this_action = BPSTAT_WHAT_SINGLE
回到process_event_stop_test
case BPSTAT_WHAT_SINGLE
```c
   case BPSTAT_WHAT_SINGLE:
      infrun_debug_printf ("BPSTAT_WHAT_SINGLE");
      ecs->event_thread->stepping_over_breakpoint = 1;
      /* Still need to check other stuff, at least the case where we
	 are stepping and step out of the right range.  */
      break;
```
可以發現後面就是不斷的在對single事件做細分，
keep_going 在呼叫keep_going_pass_signal
```c

/* Called when we should continue running the inferior, because the
   current event doesn't cause a user visible stop.  This does the
   resuming part; waiting for the next event is done elsewhere.  */

static void
keep_going (struct execution_control_state *ecs)
{
  if (ecs->event_thread->control.trap_expected
      && ecs->event_thread->stop_signal () == GDB_SIGNAL_TRAP)
    ecs->event_thread->control.trap_expected = 0;

  if (!signal_program[ecs->event_thread->stop_signal ()])
    ecs->event_thread->set_stop_signal (GDB_SIGNAL_0);
  keep_going_pass_signal (ecs);
}
```
keep_going_pass_signal

```c

/* Like keep_going, but passes the signal to the inferior, even if the
   signal is set to nopass.  */

static void
keep_going_pass_signal (struct execution_control_state *ecs)
{
  gdb_assert (ecs->event_thread->ptid == inferior_ptid);
  gdb_assert (!ecs->event_thread->resumed ());

  /* Save the pc before execution, to compare with pc after stop.  */
  ecs->event_thread->prev_pc
    = regcache_read_pc_protected (get_thread_regcache (ecs->event_thread));

  if (ecs->event_thread->control.trap_expected)
    {
      struct thread_info *tp = ecs->event_thread;

      infrun_debug_printf ("%s has trap_expected set, "
			   "resuming to collect trap",
			   tp->ptid.to_string ().c_str ());

      /* We haven't yet gotten our trap, and either: intercepted a
	 non-signal event (e.g., a fork); or took a signal which we
	 are supposed to pass through to the inferior.  Simply
	 continue.  */
      resume (ecs->event_thread->stop_signal ());
    }
  else if (step_over_info_valid_p ())
    {
      /* Another thread is stepping over a breakpoint in-line.  If
	 this thread needs a step-over too, queue the request.  In
	 either case, this resume must be deferred for later.  */
      struct thread_info *tp = ecs->event_thread;

      if (ecs->hit_singlestep_breakpoint
	  || thread_still_needs_step_over (tp))
	{
	  infrun_debug_printf ("step-over already in progress: "
			       "step-over for %s deferred",
			       tp->ptid.to_string ().c_str ());
	  global_thread_step_over_chain_enqueue (tp);
	}
      else
	infrun_debug_printf ("step-over in progress: resume of %s deferred",
			     tp->ptid.to_string ().c_str ());
    }
  else
    {
      struct regcache *regcache = get_current_regcache ();
      int remove_bp;
      int remove_wps;
      step_over_what step_what;

      /* Either the trap was not expected, but we are continuing
	 anyway (if we got a signal, the user asked it be passed to
	 the child)
	 -- or --
	 We got our expected trap, but decided we should resume from
	 it.

	 We're going to run this baby now!

	 Note that insert_breakpoints won't try to re-insert
	 already inserted breakpoints.  Therefore, we don't
	 care if breakpoints were already inserted, or not.  */

      /* If we need to step over a breakpoint, and we're not using
	 displaced stepping to do so, insert all breakpoints
	 (watchpoints, etc.) but the one we're stepping over, step one
	 instruction, and then re-insert the breakpoint when that step
	 is finished.  */

      step_what = thread_still_needs_step_over (ecs->event_thread);

      remove_bp = (ecs->hit_singlestep_breakpoint
		   || (step_what & STEP_OVER_BREAKPOINT));
      remove_wps = (step_what & STEP_OVER_WATCHPOINT);

      /* We can't use displaced stepping if we need to step past a
	 watchpoint.  The instruction copied to the scratch pad would
	 still trigger the watchpoint.  */
      if (remove_bp
	  && (remove_wps || !use_displaced_stepping (ecs->event_thread)))
	{
	  set_step_over_info (regcache->aspace (),
			      regcache_read_pc (regcache), remove_wps,
			      ecs->event_thread->global_num);
	}
      else if (remove_wps)
	set_step_over_info (nullptr, 0, remove_wps, -1);

      /* If we now need to do an in-line step-over, we need to stop
	 all other threads.  Note this must be done before
	 insert_breakpoints below, because that removes the breakpoint
	 we're about to step over, otherwise other threads could miss
	 it.  */
      if (step_over_info_valid_p () && target_is_non_stop_p ())
	stop_all_threads ("starting in-line step-over");

      /* Stop stepping if inserting breakpoints fails.  */
      try
	{
	  insert_breakpoints ();
	}
      catch (const gdb_exception_error &e)
	{
	  exception_print (gdb_stderr, e);
	  stop_waiting (ecs);
	  clear_step_over_info ();
	  return;
	}

      ecs->event_thread->control.trap_expected = (remove_bp || remove_wps);

      resume (ecs->event_thread->stop_signal ());
    }

  prepare_to_wait (ecs);
}
```
# prepare_to_wait
這邊就算確定整個inferior是要被中斷的ecs->wait_some_more=1
大概意思是這個中斷確實是因為已確定因素而中斷.
```c

/* This function normally comes after a resume, before
   handle_inferior_event exits.  It takes care of any last bits of
   housekeeping, and sets the all-important wait_some_more flag.  */

static void
prepare_to_wait (struct execution_control_state *ecs)
{
  infrun_debug_printf ("prepare_to_wait");

  ecs->wait_some_more = 1;

  /* If the target can't async, emulate it by marking the infrun event
     handler such that as soon as we get back to the event-loop, we
     immediately end up in fetch_inferior_event again calling
     target_wait.  */
  if (!target_can_async_p ())
    mark_infrun_async_event_handler ();
}

```
#  insert_breakpoints ();
```C
/* Make sure all breakpoints are inserted in inferior.
   Throws exception on any error.
   A breakpoint that is already inserted won't be inserted
   again, so calling this function twice is safe.  */
void
insert_breakpoints (void)
{
  for (breakpoint *bpt : all_breakpoints ())
    if (is_hardware_watchpoint (bpt))
      {
	struct watchpoint *w = (struct watchpoint *) bpt;

	update_watchpoint (w, false /* don't reparse.  */);
      }

  /* Updating watchpoints creates new locations, so update the global
     location list.  Explicitly tell ugll to insert locations and
     ignore breakpoints_always_inserted_mode.  Also,
     update_global_location_list tries to "upgrade" software
     breakpoints to hardware breakpoints to handle "set breakpoint
     auto-hw", so we need to call it even if we don't have new
     locations.  */
  update_global_location_list (UGLL_INSERT);
}
```

# handle_inferior_event
總而言之，會有一個地方在控管所有的事件
在這邊會創建被監控的
	 
```C
     If a child inferior was created by infrun while following the fork
     (CHILD_INF is non-nullptr), push this target on CHILD_INF's target stack
     and add an initial thread with ptid CHILD_PTID.  */
  void follow_fork (inferior *child_inf, ptid_t child_ptid,
		    target_waitkind fork_kind, bool follow_child,
		    bool detach_on_fork) override;
            
```
監控fork出來的process 查看現在的process什麼狀態
```C
 bool should_resume = follow_fork ();

	  /* Note that one of these may be an invalid pointer,
	     depending on detach_fork.  */
	  thread_info *parent = ecs->event_thread;
	  thread_info *child = find_thread_ptid (targ, ecs->ws.child_ptid ());

    case TARGET_WAITKIND_STOPPED:
      handle_signal_stop (ecs);
      return;
```
```C

/* Given an execution control state that has been freshly filled in by
   an event from the inferior, figure out what it means and take
   appropriate action.

   The alternatives are:

   1) stop_waiting and return; to really stop and return to the
   debugger.

   2) keep_going and return; to wait for the next event (set
   ecs->event_thread->stepping_over_breakpoint to 1 to single step
   once).  */

static void
handle_inferior_event (struct execution_control_state *ecs)
{
  /* Make sure that all temporary struct value objects that were
     created during the handling of the event get deleted at the
     end.  */
  scoped_value_mark free_values;

  infrun_debug_printf ("%s", ecs->ws.to_string ().c_str ());

  if (ecs->ws.kind () == TARGET_WAITKIND_IGNORE)
    {
      /* We had an event in the inferior, but we are not interested in
	 handling it at this level.  The lower layers have already
	 done what needs to be done, if anything.

	 One of the possible circumstances for this is when the
	 inferior produces output for the console.  The inferior has
	 not stopped, and we are ignoring the event.  Another possible
	 circumstance is any event which the lower level knows will be
	 reported multiple times without an intervening resume.  */
      prepare_to_wait (ecs);
      return;
    }

  if (ecs->ws.kind () == TARGET_WAITKIND_THREAD_EXITED)
    {
      prepare_to_wait (ecs);
      return;
    }

  if (ecs->ws.kind () == TARGET_WAITKIND_NO_RESUMED
      && handle_no_resumed (ecs))
    return;

  /* Cache the last target/ptid/waitstatus.  */
  set_last_target_status (ecs->target, ecs->ptid, ecs->ws);

  /* Always clear state belonging to the previous time we stopped.  */
  stop_stack_dummy = STOP_NONE;

  if (ecs->ws.kind () == TARGET_WAITKIND_NO_RESUMED)
    {
      /* No unwaited-for children left.  IOW, all resumed children
	 have exited.  */
      stop_print_frame = false;
      stop_waiting (ecs);
      return;
    }

  if (ecs->ws.kind () != TARGET_WAITKIND_EXITED
      && ecs->ws.kind () != TARGET_WAITKIND_SIGNALLED)
    {
      ecs->event_thread = find_thread_ptid (ecs->target, ecs->ptid);
      /* If it's a new thread, add it to the thread database.  */
      if (ecs->event_thread == nullptr)
	ecs->event_thread = add_thread (ecs->target, ecs->ptid);

      /* Disable range stepping.  If the next step request could use a
	 range, this will be end up re-enabled then.  */
      ecs->event_thread->control.may_range_step = 0;
    }

  /* Dependent on valid ECS->EVENT_THREAD.  */
  adjust_pc_after_break (ecs->event_thread, ecs->ws);

  /* Dependent on the current PC value modified by adjust_pc_after_break.  */
  reinit_frame_cache ();

  breakpoint_retire_moribund ();

  /* First, distinguish signals caused by the debugger from signals
     that have to do with the program's own actions.  Note that
     breakpoint insns may cause SIGTRAP or SIGILL or SIGEMT, depending
     on the operating system version.  Here we detect when a SIGILL or
     SIGEMT is really a breakpoint and change it to SIGTRAP.  We do
     something similar for SIGSEGV, since a SIGSEGV will be generated
     when we're trying to execute a breakpoint instruction on a
     non-executable stack.  This happens for call dummy breakpoints
     for architectures like SPARC that place call dummies on the
     stack.  */
  if (ecs->ws.kind () == TARGET_WAITKIND_STOPPED
      && (ecs->ws.sig () == GDB_SIGNAL_ILL
	  || ecs->ws.sig () == GDB_SIGNAL_SEGV
	  || ecs->ws.sig () == GDB_SIGNAL_EMT))
    {
      struct regcache *regcache = get_thread_regcache (ecs->event_thread);

      if (breakpoint_inserted_here_p (regcache->aspace (),
				      regcache_read_pc (regcache)))
	{
	  infrun_debug_printf ("Treating signal as SIGTRAP");
	  ecs->ws.set_stopped (GDB_SIGNAL_TRAP);
	}
    }

  mark_non_executing_threads (ecs->target, ecs->ptid, ecs->ws);

  switch (ecs->ws.kind ())
    {
    case TARGET_WAITKIND_LOADED:
      {
	context_switch (ecs);
	/* Ignore gracefully during startup of the inferior, as it might
	   be the shell which has just loaded some objects, otherwise
	   add the symbols for the newly loaded objects.  Also ignore at
	   the beginning of an attach or remote session; we will query
	   the full list of libraries once the connection is
	   established.  */

	stop_kind stop_soon = get_inferior_stop_soon (ecs);
	if (stop_soon == NO_STOP_QUIETLY)
	  {
	    struct regcache *regcache;

	    regcache = get_thread_regcache (ecs->event_thread);

	    handle_solib_event ();

	    ecs->event_thread->set_stop_pc (regcache_read_pc (regcache));
	    ecs->event_thread->control.stop_bpstat
	      = bpstat_stop_status_nowatch (regcache->aspace (),
					    ecs->event_thread->stop_pc (),
					    ecs->event_thread, ecs->ws);

	    if (handle_stop_requested (ecs))
	      return;

	    if (bpstat_causes_stop (ecs->event_thread->control.stop_bpstat))
	      {
		/* A catchpoint triggered.  */
		process_event_stop_test (ecs);
		return;
	      }

	    /* If requested, stop when the dynamic linker notifies
	       gdb of events.  This allows the user to get control
	       and place breakpoints in initializer routines for
	       dynamically loaded objects (among other things).  */
	    ecs->event_thread->set_stop_signal (GDB_SIGNAL_0);
	    if (stop_on_solib_events)
	      {
		/* Make sure we print "Stopped due to solib-event" in
		   normal_stop.  */
		stop_print_frame = true;

		stop_waiting (ecs);
		return;
	      }
	  }

	/* If we are skipping through a shell, or through shared library
	   loading that we aren't interested in, resume the program.  If
	   we're running the program normally, also resume.  */
	if (stop_soon == STOP_QUIETLY || stop_soon == NO_STOP_QUIETLY)
	  {
	    /* Loading of shared libraries might have changed breakpoint
	       addresses.  Make sure new breakpoints are inserted.  */
	    if (stop_soon == NO_STOP_QUIETLY)
	      insert_breakpoints ();
	    resume (GDB_SIGNAL_0);
	    prepare_to_wait (ecs);
	    return;
	  }

	/* But stop if we're attaching or setting up a remote
	   connection.  */
	if (stop_soon == STOP_QUIETLY_NO_SIGSTOP
	    || stop_soon == STOP_QUIETLY_REMOTE)
	  {
	    infrun_debug_printf ("quietly stopped");
	    stop_waiting (ecs);
	    return;
	  }

	internal_error (_("unhandled stop_soon: %d"), (int) stop_soon);
      }

    case TARGET_WAITKIND_SPURIOUS:
      if (handle_stop_requested (ecs))
	return;
      context_switch (ecs);
      resume (GDB_SIGNAL_0);
      prepare_to_wait (ecs);
      return;

    case TARGET_WAITKIND_THREAD_CREATED:
      if (handle_stop_requested (ecs))
	return;
      context_switch (ecs);
      if (!switch_back_to_stepped_thread (ecs))
	keep_going (ecs);
      return;

    case TARGET_WAITKIND_EXITED:
    case TARGET_WAITKIND_SIGNALLED:
      {
	/* Depending on the system, ecs->ptid may point to a thread or
	   to a process.  On some targets, target_mourn_inferior may
	   need to have access to the just-exited thread.  That is the
	   case of GNU/Linux's "checkpoint" support, for example.
	   Call the switch_to_xxx routine as appropriate.  */
	thread_info *thr = find_thread_ptid (ecs->target, ecs->ptid);
	if (thr != nullptr)
	  switch_to_thread (thr);
	else
	  {
	    inferior *inf = find_inferior_ptid (ecs->target, ecs->ptid);
	    switch_to_inferior_no_thread (inf);
	  }
      }
      handle_vfork_child_exec_or_exit (0);
      target_terminal::ours ();	/* Must do this before mourn anyway.  */

      /* Clearing any previous state of convenience variables.  */
      clear_exit_convenience_vars ();

      if (ecs->ws.kind () == TARGET_WAITKIND_EXITED)
	{
	  /* Record the exit code in the convenience variable $_exitcode, so
	     that the user can inspect this again later.  */
	  set_internalvar_integer (lookup_internalvar ("_exitcode"),
				   (LONGEST) ecs->ws.exit_status ());

	  /* Also record this in the inferior itself.  */
	  current_inferior ()->has_exit_code = true;
	  current_inferior ()->exit_code = (LONGEST) ecs->ws.exit_status ();

	  /* Support the --return-child-result option.  */
	  return_child_result_value = ecs->ws.exit_status ();

	  gdb::observers::exited.notify (ecs->ws.exit_status ());
	}
      else
	{
	  struct gdbarch *gdbarch = current_inferior ()->gdbarch;

	  if (gdbarch_gdb_signal_to_target_p (gdbarch))
	    {
	      /* Set the value of the internal variable $_exitsignal,
		 which holds the signal uncaught by the inferior.  */
	      set_internalvar_integer (lookup_internalvar ("_exitsignal"),
				       gdbarch_gdb_signal_to_target (gdbarch,
							  ecs->ws.sig ()));
	    }
	  else
	    {
	      /* We don't have access to the target's method used for
		 converting between signal numbers (GDB's internal
		 representation <-> target's representation).
		 Therefore, we cannot do a good job at displaying this
		 information to the user.  It's better to just warn
		 her about it (if infrun debugging is enabled), and
		 give up.  */
	      infrun_debug_printf ("Cannot fill $_exitsignal with the correct "
				   "signal number.");
	    }

	  gdb::observers::signal_exited.notify (ecs->ws.sig ());
	}

      gdb_flush (gdb_stdout);
      target_mourn_inferior (inferior_ptid);
      stop_print_frame = false;
      stop_waiting (ecs);
      return;

    case TARGET_WAITKIND_FORKED:
    case TARGET_WAITKIND_VFORKED:
      /* Check whether the inferior is displaced stepping.  */
      {
	struct regcache *regcache = get_thread_regcache (ecs->event_thread);
	struct gdbarch *gdbarch = regcache->arch ();
	inferior *parent_inf = find_inferior_ptid (ecs->target, ecs->ptid);

	/* If this is a fork (child gets its own address space copy)
	   and some displaced step buffers were in use at the time of
	   the fork, restore the displaced step buffer bytes in the
	   child process.

	   Architectures which support displaced stepping and fork
	   events must supply an implementation of
	   gdbarch_displaced_step_restore_all_in_ptid.  This is not
	   enforced during gdbarch validation to support architectures
	   which support displaced stepping but not forks.  */
	if (ecs->ws.kind () == TARGET_WAITKIND_FORKED
	    && gdbarch_supports_displaced_stepping (gdbarch))
	  gdbarch_displaced_step_restore_all_in_ptid
	    (gdbarch, parent_inf, ecs->ws.child_ptid ());

	/* If displaced stepping is supported, and thread ecs->ptid is
	   displaced stepping.  */
	if (displaced_step_in_progress_thread (ecs->event_thread))
	  {
	    struct regcache *child_regcache;
	    CORE_ADDR parent_pc;

	    /* GDB has got TARGET_WAITKIND_FORKED or TARGET_WAITKIND_VFORKED,
	       indicating that the displaced stepping of syscall instruction
	       has been done.  Perform cleanup for parent process here.  Note
	       that this operation also cleans up the child process for vfork,
	       because their pages are shared.  */
	    displaced_step_finish (ecs->event_thread, GDB_SIGNAL_TRAP);
	    /* Start a new step-over in another thread if there's one
	       that needs it.  */
	    start_step_over ();

	    /* Since the vfork/fork syscall instruction was executed in the scratchpad,
	       the child's PC is also within the scratchpad.  Set the child's PC
	       to the parent's PC value, which has already been fixed up.
	       FIXME: we use the parent's aspace here, although we're touching
	       the child, because the child hasn't been added to the inferior
	       list yet at this point.  */

	    child_regcache
	      = get_thread_arch_aspace_regcache (parent_inf->process_target (),
						 ecs->ws.child_ptid (),
						 gdbarch,
						 parent_inf->aspace);
	    /* Read PC value of parent process.  */
	    parent_pc = regcache_read_pc (regcache);

	    displaced_debug_printf ("write child pc from %s to %s",
				    paddress (gdbarch,
					      regcache_read_pc (child_regcache)),
				    paddress (gdbarch, parent_pc));

	    regcache_write_pc (child_regcache, parent_pc);
	  }
      }

      context_switch (ecs);

      /* Immediately detach breakpoints from the child before there's
	 any chance of letting the user delete breakpoints from the
	 breakpoint lists.  If we don't do this early, it's easy to
	 leave left over traps in the child, vis: "break foo; catch
	 fork; c; <fork>; del; c; <child calls foo>".  We only follow
	 the fork on the last `continue', and by that time the
	 breakpoint at "foo" is long gone from the breakpoint table.
	 If we vforked, then we don't need to unpatch here, since both
	 parent and child are sharing the same memory pages; we'll
	 need to unpatch at follow/detach time instead to be certain
	 that new breakpoints added between catchpoint hit time and
	 vfork follow are detached.  */
      if (ecs->ws.kind () != TARGET_WAITKIND_VFORKED)
	{
	  /* This won't actually modify the breakpoint list, but will
	     physically remove the breakpoints from the child.  */
	  detach_breakpoints (ecs->ws.child_ptid ());
	}

      delete_just_stopped_threads_single_step_breakpoints ();

      /* In case the event is caught by a catchpoint, remember that
	 the event is to be followed at the next resume of the thread,
	 and not immediately.  */
      ecs->event_thread->pending_follow = ecs->ws;

      ecs->event_thread->set_stop_pc
	(regcache_read_pc (get_thread_regcache (ecs->event_thread)));

      ecs->event_thread->control.stop_bpstat
	= bpstat_stop_status_nowatch (get_current_regcache ()->aspace (),
				      ecs->event_thread->stop_pc (),
				      ecs->event_thread, ecs->ws);

      if (handle_stop_requested (ecs))
	return;

      /* If no catchpoint triggered for this, then keep going.  Note
	 that we're interested in knowing the bpstat actually causes a
	 stop, not just if it may explain the signal.  Software
	 watchpoints, for example, always appear in the bpstat.  */
      if (!bpstat_causes_stop (ecs->event_thread->control.stop_bpstat))
	{
	  bool follow_child
	    = (follow_fork_mode_string == follow_fork_mode_child);

	  ecs->event_thread->set_stop_signal (GDB_SIGNAL_0);

	  process_stratum_target *targ
	    = ecs->event_thread->inf->process_target ();

	  bool should_resume = follow_fork ();

	  /* Note that one of these may be an invalid pointer,
	     depending on detach_fork.  */
	  thread_info *parent = ecs->event_thread;
	  thread_info *child = find_thread_ptid (targ, ecs->ws.child_ptid ());

	  /* At this point, the parent is marked running, and the
	     child is marked stopped.  */

	  /* If not resuming the parent, mark it stopped.  */
	  if (follow_child && !detach_fork && !non_stop && !sched_multi)
	    parent->set_running (false);

	  /* If resuming the child, mark it running.  */
	  if (follow_child || (!detach_fork && (non_stop || sched_multi)))
	    child->set_running (true);

	  /* In non-stop mode, also resume the other branch.  */
	  if (!detach_fork && (non_stop
			       || (sched_multi && target_is_non_stop_p ())))
	    {
	      if (follow_child)
		switch_to_thread (parent);
	      else
		switch_to_thread (child);

	      ecs->event_thread = inferior_thread ();
	      ecs->ptid = inferior_ptid;
	      keep_going (ecs);
	    }

	  if (follow_child)
	    switch_to_thread (child);
	  else
	    switch_to_thread (parent);

	  ecs->event_thread = inferior_thread ();
	  ecs->ptid = inferior_ptid;

	  if (should_resume)
	    {
	      /* Never call switch_back_to_stepped_thread if we are waiting for
	         vfork-done (waiting for an external vfork child to exec or
		 exit).  We will resume only the vforking thread for the purpose
		 of collecting the vfork-done event, and we will restart any
		 step once the critical shared address space window is done.  */
	      if ((!follow_child
		   && detach_fork
		   && parent->inf->thread_waiting_for_vfork_done != nullptr)
		  || !switch_back_to_stepped_thread (ecs))
		keep_going (ecs);
	    }
	  else
	    stop_waiting (ecs);
	  return;
	}
      process_event_stop_test (ecs);
      return;

    case TARGET_WAITKIND_VFORK_DONE:
      /* Done with the shared memory region.  Re-insert breakpoints in
	 the parent, and keep going.  */

      context_switch (ecs);

      handle_vfork_done (ecs->event_thread);
      gdb_assert (inferior_thread () == ecs->event_thread);

      if (handle_stop_requested (ecs))
	return;

      if (!switch_back_to_stepped_thread (ecs))
	{
	  gdb_assert (inferior_thread () == ecs->event_thread);
	  /* This also takes care of reinserting breakpoints in the
	     previously locked inferior.  */
	  keep_going (ecs);
	}
      return;

    case TARGET_WAITKIND_EXECD:

      /* Note we can't read registers yet (the stop_pc), because we
	 don't yet know the inferior's post-exec architecture.
	 'stop_pc' is explicitly read below instead.  */
      switch_to_thread_no_regs (ecs->event_thread);

      /* Do whatever is necessary to the parent branch of the vfork.  */
      handle_vfork_child_exec_or_exit (1);

      /* This causes the eventpoints and symbol table to be reset.
	 Must do this now, before trying to determine whether to
	 stop.  */
      follow_exec (inferior_ptid, ecs->ws.execd_pathname ());

      /* In follow_exec we may have deleted the original thread and
	 created a new one.  Make sure that the event thread is the
	 execd thread for that case (this is a nop otherwise).  */
      ecs->event_thread = inferior_thread ();

      ecs->event_thread->set_stop_pc
	(regcache_read_pc (get_thread_regcache (ecs->event_thread)));

      ecs->event_thread->control.stop_bpstat
	= bpstat_stop_status_nowatch (get_current_regcache ()->aspace (),
				      ecs->event_thread->stop_pc (),
				      ecs->event_thread, ecs->ws);

      if (handle_stop_requested (ecs))
	return;

      /* If no catchpoint triggered for this, then keep going.  */
      if (!bpstat_causes_stop (ecs->event_thread->control.stop_bpstat))
	{
	  ecs->event_thread->set_stop_signal (GDB_SIGNAL_0);
	  keep_going (ecs);
	  return;
	}
      process_event_stop_test (ecs);
      return;

      /* Be careful not to try to gather much state about a thread
	 that's in a syscall.  It's frequently a losing proposition.  */
    case TARGET_WAITKIND_SYSCALL_ENTRY:
      /* Getting the current syscall number.  */
      if (handle_syscall_event (ecs) == 0)
	process_event_stop_test (ecs);
      return;

      /* Before examining the threads further, step this thread to
	 get it entirely out of the syscall.  (We get notice of the
	 event when the thread is just on the verge of exiting a
	 syscall.  Stepping one instruction seems to get it back
	 into user code.)  */
    case TARGET_WAITKIND_SYSCALL_RETURN:
      if (handle_syscall_event (ecs) == 0)
	process_event_stop_test (ecs);
      return;

    case TARGET_WAITKIND_STOPPED:
      handle_signal_stop (ecs);
      return;

    case TARGET_WAITKIND_NO_HISTORY:
      /* Reverse execution: target ran out of history info.  */

      /* Switch to the stopped thread.  */
      context_switch (ecs);
      infrun_debug_printf ("stopped");

      delete_just_stopped_threads_single_step_breakpoints ();
      ecs->event_thread->set_stop_pc
	(regcache_read_pc (get_thread_regcache (inferior_thread ())));

      if (handle_stop_requested (ecs))
	return;

      gdb::observers::no_history.notify ();
      stop_waiting (ecs);
      return;
    }
}
```

inferior_event_handler 監控fork出來的chinld process的狀態
如果程式已經停止，也就意味著該inferior 狀態已經暫停了
```c
case TARGET_WAITKIND_STOPPED:
      handle_signal_stop (ecs);
      return;
```
則處理該ecs 交給handle_signal_stop  來判斷該inferior 停止原因
wait_for_inferior 會一直檢查剛剛程式中有可能觸發的exception,直到
```c
  if (!ecs.wait_some_more)
	break;
```

# wait_for_inferior
```c
/* Wait for control to return from inferior to debugger.

   If inferior gets a signal, we may decide to start it up again
   instead of returning.  That is why there is a loop in this function.
   When this function actually returns it means the inferior
   should be left stopped and GDB should read more commands.  */

static void
wait_for_inferior (inferior *inf)
{
  infrun_debug_printf ("wait_for_inferior ()");

  SCOPE_EXIT { delete_just_stopped_threads_infrun_breakpoints (); };

  /* If an error happens while handling the event, propagate GDB's
     knowledge of the executing state to the frontend/user running
     state.  */
  scoped_finish_thread_state finish_state
    (inf->process_target (), minus_one_ptid);

  while (1)
    {
      execution_control_state ecs;

      overlay_cache_invalid = 1;

      /* Flush target cache before starting to handle each event.
	 Target was running and cache could be stale.  This is just a
	 heuristic.  Running threads may modify target memory, but we
	 don't get any event.  */
      target_dcache_invalidate ();

      ecs.ptid = do_target_wait_1 (inf, minus_one_ptid, &ecs.ws, 0);
      ecs.target = inf->process_target ();

      if (debug_infrun)
	print_target_wait_results (minus_one_ptid, ecs.ptid, ecs.ws);

      /* Now figure out what to do with the result of the result.  */
      handle_inferior_event (&ecs);

      if (!ecs.wait_some_more)
	break;
    }

  stop_all_threads_if_all_stop_mode ();

  /* No error, don't finish the state yet.  */
  finish_state.release ();
}
```
再往上追就是就是gdb 透過command 方式 去讀取file
```c
/* Implement the "run" command.  Force a stop during program start if
   requested by RUN_HOW.  */

static void
run_command_1 (const char *args, int from_tty, enum run_how run_how)
{
  const char *exec_file;
  struct ui_out *uiout = current_uiout;
  struct target_ops *run_target;
  int async_exec;

  dont_repeat ();

  scoped_disable_commit_resumed disable_commit_resumed ("running");

  kill_if_already_running (from_tty);

  init_wait_for_inferior ();
  clear_breakpoint_hit_counts ();

  /* Clean up any leftovers from other runs.  Some other things from
     this function should probably be moved into target_pre_inferior.  */
  target_pre_inferior (from_tty);

  /* The comment here used to read, "The exec file is re-read every
     time we do a generic_mourn_inferior, so we just have to worry
     about the symbol file."  The `generic_mourn_inferior' function
     gets called whenever the program exits.  However, suppose the
     program exits, and *then* the executable file changes?  We need
     to check again here.  Since reopen_exec_file doesn't do anything
     if the timestamp hasn't changed, I don't see the harm.  */
  reopen_exec_file ();
  reread_symbols (from_tty);

  gdb::unique_xmalloc_ptr<char> stripped = strip_bg_char (args, &async_exec);
  args = stripped.get ();

  /* Do validation and preparation before possibly changing anything
     in the inferior.  */

  run_target = find_run_target ();
```
熟悉的attach
```c

/* "attach" command entry point.  Takes a program started up outside
   of gdb and ``attaches'' to it.  This stops it cold in its tracks
   and allows us to start debugging it.  */

void
attach_command (const char *args, int from_tty)
{
  int async_exec;
  struct target_ops *attach_target;
  struct inferior *inferior = current_inferior ();
  enum attach_post_wait_mode mode;

  dont_repeat ();		/* Not for the faint of heart */

  scoped_disable_commit_resumed disable_commit_resumed ("attaching");

  if (gdbarch_has_global_solist (target_gdbarch ()))
    /* Don't complain if all processes share the same symbol
       space.  */
    ;
  else if (target_has_execution ())
    {
      if (query (_("A program is being debugged already.  Kill it? ")))
	target_kill ();
      else
	error (_("Not killed."));
    }

  /* Clean up any leftovers from other runs.  Some other things from
     this function should probably be moved into target_pre_inferior.  */
  target_pre_inferior (from_tty);

  gdb::unique_xmalloc_ptr<char> stripped = strip_bg_char (args, &async_exec);
  args = stripped.get ();

  attach_target = find_attach_target ();

  prepare_execution_command (attach_target, async_exec);

  if (non_stop && !attach_target->supports_non_stop ())
    error (_("Cannot attach to this target in non-stop mode"));

  attach_target->attach (args, from_tty);
  /* to_attach should push the target, so after this point we
     shouldn't refer to attach_target again.  */
  attach_target = nullptr;

  infrun_debug_show_threads ("immediately after attach",
			     current_inferior ()->non_exited_threads ());

  /* Enable async mode if it is supported by the target.  */
  if (target_can_async_p ())
    target_async (true);

  /* Set up the "saved terminal modes" of the inferior
     based on what modes we are starting it with.  */
  target_terminal::init ();

  /* Install inferior's terminal modes.  This may look like a no-op,
     as we've just saved them above, however, this does more than
     restore terminal settings:

     - installs a SIGINT handler that forwards SIGINT to the inferior.
       Otherwise a Ctrl-C pressed just while waiting for the initial
       stop would end up as a spurious Quit.

     - removes stdin from the event loop, which we need if attaching
       in the foreground, otherwise on targets that report an initial
       stop on attach (which are most) we'd process input/commands
       while we're in the event loop waiting for that stop.  That is,
       before the attach continuation runs and the command is really
       finished.  */
  target_terminal::inferior ();

  /* Set up execution context to know that we should return from
     wait_for_inferior as soon as the target reports a stop.  */
  init_wait_for_inferior ();

```
到這邊應該大致知道gdb是怎跑的

