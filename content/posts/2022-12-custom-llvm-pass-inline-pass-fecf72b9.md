---
title: "custom llvm pass inline pass"
date: "2022-12-08T23:30:00.003+08:00"
updated: "2022-12-08T23:31:01.005+08:00"
permalink: "/2022/12/custom-llvm-pass-inline-pass.html"
original_url: "https://x8795278.blogspot.com/2022/12/custom-llvm-pass-inline-pass.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-636917194708322864"
tags: ["inline", "llvm", "pass"]
layout: post
---

![](https://i.imgur.com/XSJo4YA.png)

# llvm pass
https://reviews.llvm.org/D70199
https://zhuanlan.zhihu.com/p/122522485
https://juejin.cn/post/6844904030636867598
https://llvm.org/devmtg/2019-10/slides/Warzynski-WritingAnLLVMPass.pdf
https://csstormq.github.io/blog/LLVM%20%E4%B9%8B%20IR%20%E7%AF%87%EF%BC%886%EF%BC%89%EF%BC%9A%E5%A6%82%E4%BD%95%E7%BC%96%E5%86%99%E6%B6%88%E9%99%A4%E6%AD%BB%E4%BB%A3%E7%A0%81%20Pass
https://csstormq.github.io/blog/LLVM%20%E4%B9%8B%20IR%20%E7%AF%87%EF%BC%886%EF%BC%89%EF%BC%9A%E5%A6%82%E4%BD%95%E7%BC%96%E5%86%99%E6%B6%88%E9%99%A4%E6%AD%BB%E4%BB%A3%E7%A0%81%20Pass
https://blog.csdn.net/tristan_tian/article/details/81585175
https://csstormq.github.io/blog/LLVM%20%E4%B9%8B%20IR%20%E7%AF%87%EF%BC%887%EF%BC%89%EF%BC%9A%E5%A6%82%E4%BD%95%E7%BC%96%E5%86%99%E5%86%85%E8%81%94%20Pass
![](https://i.imgur.com/XSJo4YA.png)

![](https://i.imgur.com/8ZPqCcx.png)

```bash
https://releases.llvm.org/download.html#10.0.0
wget https://github.com/llvm/llvm-project/releases/download/llvmorg-10.0.0/llvm-project-10.0.0.tar.xz
tar -xf llvm-project-10.0.0.tar.xz

cd llvm-project
mkdir build && cd build
cmake -G "Unix Makefiles" -DLLVM_ENABLE_PROJECTS="clang" \
    -DCMAKE_BUILD_TYPE=Release -DLLVM_TARGETS_TO_BUILD="X86" \
    -DBUILD_SHARED_LIBS=On ../llvm
make -j8
sudo make install 
git clone https://github.com/LeadroyaL/llvm-pass-tutorial.git
```
在這個專案內有一個
https://github.com/LeadroyaL/llvm-pass-tutorial/tree/dev/ollvm
和
https://github.com/LeadroyaL/llvm-pass-tutorial/tree/dev/skeleton
都有模板可以玩玩看，但是我的需求假設只能在llvm-10，在直接使用模板確實可以透過動態加載的方式直接呼叫我們的pass
下面則是用skeleton
https://github.com/LeadroyaL/llvm-pass-tutorial/tree/dev/skeleton

# llvm/lib/Transforms/IPO/MyInliner.cpp
```c
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace {
  struct SkeletonPass : public FunctionPass {
    static char ID;
    SkeletonPass() : FunctionPass(ID) {}

    virtual bool runOnFunction(Function &F) {
      errs() << "I saw a function called " << F.getName() << "!\n";
      return false;
    }
  };
}

char SkeletonPass::ID = 0;

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerSkeletonPass(const PassManagerBuilder &,
                         legacy::PassManagerBase &PM) {
  PM.add(new SkeletonPass());
}
static RegisterStandardPasses
  RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                 registerSkeletonPass);

#if LLVM_VERSION_MAJOR >= 13

struct NewSkeletonPass : PassInfoMixin<NewSkeletonPass> {
public:
    static bool isRequired() {
        errs() << "isRequired invoked\n";
        return true;
    }

    static PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
        errs() << "Module name is " << M.getName() << "!\n";
        return PreservedAnalyses::all();
    }
};

void myCallback(llvm::ModulePassManager &PM, llvm::PassBuilder::OptimizationLevel Level) {
    PM.addPass(NewSkeletonPass());
}

/* New PM Registration */
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    errs() << "llvmGetPassPluginInfo\n";
    return {LLVM_PLUGIN_API_VERSION,
            "skeleton",
            LLVM_VERSION_STRING,
            [](PassBuilder &PB) {
                PB.registerPipelineStartEPCallback(myCallback);
                // TODO: handle opt
                // PB.registerPipelineParsingCallback
            }};
}
#endif
```

可以看到一般而言假設要用下面版本的pass可能要到llvm13以上才有支援，範例上面的部分呢我們直接使用這樣子的方式加載

```bahs
make
 clang -Xclang -load -Xclang ./libSkeletonPass.so test.c
 -o test
```
![](https://i.imgur.com/J73YjEo.png)

那麼要真正的修改某一層的pass我們直接參考怎麼在llvm 的內部加載我們的pass
以https://csstormq.github.io/blog/LLVM%20%E4%B9%8B%20IR%20%E7%AF%87%EF%BC%887%EF%BC%89%EF%BC%9A%E5%A6%82%E4%BD%95%E7%BC%96%E5%86%99%E5%86%85%E8%81%94%20Pass
文章參考，他是llvm 12 他的程式碼可能要異動一下變為下列的版本
https://codebrowser.dev/llvm/llvm/lib/Transforms/IPO/AlwaysInliner.cpp.html
那麼我們重新順一下他的流程

# llvm/lib/Transforms/IPO/MyInliner.cpp
產生我們的pass到時候要用,MyInliner.cpp新增到llvm/lib/Transforms/IPO資料夾下，由於依賴Inliner.h所以我們的pass 會被集中到 libLLVMipo.so中。
```c
#include "llvm/InitializePasses.h"
#include "llvm/Transforms/IPO.h"
#include "llvm/Transforms/IPO/Inliner.h"
#include "llvm/Analysis/InlineCost.h"

using namespace llvm;

#define DEBUG_TYPE "myinliner"

namespace {

class MyInlinerLegacyPass : public LegacyInlinerBase {
public:
static char ID;

MyInlinerLegacyPass() : LegacyInlinerBase(ID) {
initializeMyInlinerLegacyPassPass(*PassRegistry::getPassRegistry());
}

  InlineCost getInlineCost(CallSite CS) override;

};

} // anonymous namespace

char MyInlinerLegacyPass::ID = 0;

INITIALIZE_PASS(MyInlinerLegacyPass, DEBUG_TYPE,
"Inliner for always_inline functions Legacy Pass", false, false)

Pass *llvm::createMyInlinerLegacyPass() {
return new MyInlinerLegacyPass();
}
InlineCost MyInlinerLegacyPass::getInlineCost(CallSite CS) {
  Function *Callee = CS.getCalledFunction();

  // Only inline direct calls to functions with always-inline attributes
  // that are viable for inlining.
  if (!Callee)
    return InlineCost::getNever("indirect call");

  // FIXME: We shouldn't even get here for declarations.
  if (Callee->isDeclaration())
    return InlineCost::getNever("no definition");

  if (!CS.hasFnAttr(Attribute::AlwaysInline))
    return InlineCost::getNever("no alwaysinline attribute");

  auto IsViable = isInlineViable(*Callee);
  if (!IsViable)
    return InlineCost::getNever(IsViable.message);

  return InlineCost::getAlways("always inliner");
}

```
# llvm/include/llvm/InitializePasses.h
增加到最後一列
```bash
namespace llvm {
......
void initializeMyInlinerLegacyPassPass(PassRegistry&);
} // end namespace llvm
```

# llvm/include/llvm/LinkAllPasses.h
增加到最後一列
```bash
(void) llvm::createMyInlinerLegacyPass();
```
```bash
namespace {
  struct ForcePassLinking {
    ForcePassLinking() {
       ...
      (void) llvm::createMyInlinerLegacyPass();
       ...
    }
  } ForcePassLinking; // Force link by creating a global definition.
}
```
# llvm/include/llvm/Transforms/IPO.h
增加到最後一列
```bash
namespace llvm {
...
Pass *createMyInlinerLegacyPass();
} // End llvm namespace
```

# llvm/include/llvm-c/Transforms/IPO.h
增加到最後一列
```bash
/** See llvm::createMyInlinerLegacyPass function. */
void LLVMMyInlinerLegacyPass(LLVMPassManagerRef PM);
```

# llvm/lib/Transforms/IPO/IPO.cpp
增加到最後一列
```bash
void llvm::initializeIPOOpts(PassRegistry &Registry) {
   ...
  initializeMyInlinerLegacyPassPass(Registry);
}
```

```bash
void LLVMMyInlinerLegacyPass(LLVMPassManagerRef PM) {
  unwrap(PM)->add(createMyInlinerLegacyPass());
}
```

# llvm/lib/Transforms/IPO/CMakeLists.txt
增加到最後一列
```
MyInliner.cpp
```

# opt
![](https://i.imgur.com/Zl9rFKL.png)

最後我們進行重編，最後可以在opt的tool 看到我們編譯後的pass
```
$ opt --help | grep myinliner
      --myinliner                                                          - Inliner for always_inline functions Legacy Pass
```

# using
```
clang -S -emit-llvm test.c
opt -S -myinliner test.ll
```
![](https://i.imgur.com/YcQMznF.png)

# 後紀
剛剛的git專案
https://github.com/LeadroyaL/llvm-pass-tutorial/blob/dev/ollvm/Utils.cpp
像這種地方也可以看到
也是跟gcc pass一樣,function , basicblock 等等

```c
   for (Function::iterator i = f->begin(); i != f->end(); ++i) {

      for (BasicBlock::iterator j = i->begin(); j != i->end(); ++j) {

       ....
      }
    }
```

像是剛剛的AlwaysInliner.cpp.html,可以看到他也是可能再對fucntion做判斷
https://codebrowser.dev/llvm/llvm/lib/Transforms/IPO/AlwaysInliner.cpp.html
```c
 for (Function &F : M) {
    // When callee coroutine function is inlined into caller coroutine function
    // before coro-split pass,
    // coro-early pass can not handle this quiet well.
    // So we won't inline the coroutine function if it have not been unsplited
    if (F.isPresplitCoroutine())
      continue;
    if (!F.isDeclaration() && isInlineViable(F).isSuccess()) {
      Calls.clear();

```
像是判斷Attribute等等
```c
CB->getAttributes().hasFnAttr(Attribute::NoInline)
```
當然codebrowser是屬於比較新的
像是在llvm-10,指令偶爾就會大改
```
//===- InlineAlways.cpp - Code to inline always_inline functions ----------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
//
// This file implements a custom inliner that handles only functions that
// are marked as "always inline".
//
//===----------------------------------------------------------------------===//

#include "llvm/Transforms/IPO/AlwaysInliner.h"
#include "llvm/ADT/SetVector.h"
#include "llvm/Analysis/AssumptionCache.h"
#include "llvm/Analysis/InlineCost.h"
#include "llvm/Analysis/TargetLibraryInfo.h"
#include "llvm/IR/CallSite.h"
#include "llvm/IR/CallingConv.h"
#include "llvm/IR/DataLayout.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Type.h"
#include "llvm/InitializePasses.h"
#include "llvm/Transforms/IPO.h"
#include "llvm/Transforms/IPO/Inliner.h"
#include "llvm/Transforms/Utils/Cloning.h"
#include "llvm/Transforms/Utils/ModuleUtils.h"

using namespace llvm;

#define DEBUG_TYPE "inline"

PreservedAnalyses AlwaysInlinerPass::run(Module &M,
                                         ModuleAnalysisManager &MAM) {
  // Add inline assumptions during code generation.
  FunctionAnalysisManager &FAM =
      MAM.getResult<FunctionAnalysisManagerModuleProxy>(M).getManager();
  std::function<AssumptionCache &(Function &)> GetAssumptionCache =
      [&](Function &F) -> AssumptionCache & {
    return FAM.getResult<AssumptionAnalysis>(F);
  };
  InlineFunctionInfo IFI(/*cg=*/nullptr, &GetAssumptionCache);

  SmallSetVector<CallSite, 16> Calls;
  bool Changed = false;
  SmallVector<Function *, 16> InlinedFunctions;
  for (Function &F : M)
    if (!F.isDeclaration() && F.hasFnAttribute(Attribute::AlwaysInline) &&
        isInlineViable(F)) {
      Calls.clear();

      for (User *U : F.users())
        if (auto CS = CallSite(U))
          if (CS.getCalledFunction() == &F)
            Calls.insert(CS);

      for (CallSite CS : Calls)
        // FIXME: We really shouldn't be able to fail to inline at this point!
        // We should do something to log or check the inline failures here.
        Changed |=
            InlineFunction(CS, IFI, /*CalleeAAR=*/nullptr, InsertLifetime);

      // Remember to try and delete this function afterward. This both avoids
      // re-walking the rest of the module and avoids dealing with any iterator
      // invalidation issues while deleting functions.
      InlinedFunctions.push_back(&F);
    }

  // Remove any live functions.
  erase_if(InlinedFunctions, [&](Function *F) {
    F->removeDeadConstantUsers();
    return !F->isDefTriviallyDead();
  });

  // Delete the non-comdat ones from the module and also from our vector.
  auto NonComdatBegin = partition(
      InlinedFunctions, [&](Function *F) { return F->hasComdat(); });
  for (Function *F : make_range(NonComdatBegin, InlinedFunctions.end()))
    M.getFunctionList().erase(F);
  InlinedFunctions.erase(NonComdatBegin, InlinedFunctions.end());

  if (!InlinedFunctions.empty()) {
    // Now we just have the comdat functions. Filter out the ones whose comdats
    // are not actually dead.
    filterDeadComdatFunctions(M, InlinedFunctions);
    // The remaining functions are actually dead.
    for (Function *F : InlinedFunctions)
      M.getFunctionList().erase(F);
  }

  return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
}

namespace {

/// Inliner pass which only handles "always inline" functions.
///
/// Unlike the \c AlwaysInlinerPass, this uses the more heavyweight \c Inliner
/// base class to provide several facilities such as array alloca merging.
class AlwaysInlinerLegacyPass : public LegacyInlinerBase {

public:
  AlwaysInlinerLegacyPass() : LegacyInlinerBase(ID, /*InsertLifetime*/ true) {
    initializeAlwaysInlinerLegacyPassPass(*PassRegistry::getPassRegistry());
  }

  AlwaysInlinerLegacyPass(bool InsertLifetime)
      : LegacyInlinerBase(ID, InsertLifetime) {
    initializeAlwaysInlinerLegacyPassPass(*PassRegistry::getPassRegistry());
  }

  /// Main run interface method.  We override here to avoid calling skipSCC().
  bool runOnSCC(CallGraphSCC &SCC) override { return inlineCalls(SCC); }

  static char ID; // Pass identification, replacement for typeid

  InlineCost getInlineCost(CallSite CS) override;

  using llvm::Pass::doFinalization;
  bool doFinalization(CallGraph &CG) override {
    return removeDeadFunctions(CG, /*AlwaysInlineOnly=*/true);
  }
};
}

char AlwaysInlinerLegacyPass::ID = 0;
INITIALIZE_PASS_BEGIN(AlwaysInlinerLegacyPass, "always-inline",
                      "Inliner for always_inline functions", false, false)
INITIALIZE_PASS_DEPENDENCY(AssumptionCacheTracker)
INITIALIZE_PASS_DEPENDENCY(CallGraphWrapperPass)
INITIALIZE_PASS_DEPENDENCY(ProfileSummaryInfoWrapperPass)
INITIALIZE_PASS_DEPENDENCY(TargetLibraryInfoWrapperPass)
INITIALIZE_PASS_END(AlwaysInlinerLegacyPass, "always-inline",
                    "Inliner for always_inline functions", false, false)

Pass *llvm::createAlwaysInlinerLegacyPass(bool InsertLifetime) {
  return new AlwaysInlinerLegacyPass(InsertLifetime);
}

/// Get the inline cost for the always-inliner.
///
/// The always inliner *only* handles functions which are marked with the
/// attribute to force inlining. As such, it is dramatically simpler and avoids
/// using the powerful (but expensive) inline cost analysis. Instead it uses
/// a very simple and boring direct walk of the instructions looking for
/// impossible-to-inline constructs.
///
/// Note, it would be possible to go to some lengths to cache the information
/// computed here, but as we only expect to do this for relatively few and
/// small functions which have the explicit attribute to force inlining, it is
/// likely not worth it in practice.
InlineCost AlwaysInlinerLegacyPass::getInlineCost(CallSite CS) {
  Function *Callee = CS.getCalledFunction();

  // Only inline direct calls to functions with always-inline attributes
  // that are viable for inlining.
  if (!Callee)
    return InlineCost::getNever("indirect call");

  // FIXME: We shouldn't even get here for declarations.
  if (Callee->isDeclaration())
    return InlineCost::getNever("no definition");

  if (!CS.hasFnAttr(Attribute::AlwaysInline))
    return InlineCost::getNever("no alwaysinline attribute");

  auto IsViable = isInlineViable(*Callee);
  if (!IsViable)
    return InlineCost::getNever(IsViable.message);

  return InlineCost::getAlways("always inliner");
}

```
差不多是這樣，快速過完，改天再來找相似的地方補足unroll loop,在看了幾次pass,原來程式碼混淆大概也可以透過pass來達成
https://bbs.pediy.com/thread-266082.htm

