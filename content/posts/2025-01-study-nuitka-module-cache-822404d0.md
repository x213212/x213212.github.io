---
title: "study nuitka module cache"
date: "2025-01-12T23:07:00.004+08:00"
updated: "2025-01-12T23:07:40.854+08:00"
permalink: "/2025/01/study-nuitka-module-cache.html"
original_url: "https://x8795278.blogspot.com/2025/01/study-nuitka-module-cache.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5830278570513119267"
tags: ["Nuitka"]
layout: post
---

![](https://hackmd.io/_uploads/BybwcUbDkg.png)

# study nuitka module cache
本來在研究看能不能在 nuitka 找尋 module 的時候加一層cache 追到後面發現作者已經有寫了，這邊記錄一下
```python
def makeOptimizationPass():
    """Make a single pass for optimization, indication potential completion."""

    finished = True

    ModuleRegistry.startTraversal()
    _restartProgress()

    main_module = None
    stdlib_phase_done = False

    while True:
        current_module = ModuleRegistry.nextModule()

        if current_module is None:
            if main_module is not None and pass_count == 1:
                considerUsedModules(module=main_module, pass_count=-1)

                stdlib_phase_done = True
                main_module = None
                continue

            break

        if current_module.isMainModule() and not stdlib_phase_done:
            main_module = current_module

        _traceProgressModuleStart(current_module)

        module_name = current_module.getFullName()

        with TimerReport(
            message="Optimizing %s" % module_name, decider=False
        ) as module_timer:
            changed, micro_passes = optimizeModule(current_module)

        ModuleRegistry.addModuleOptimizationTimeInformation(
            module_name=module_name,
            pass_number=pass_count,
            time_used=module_timer.getDelta(),
            micro_passes=micro_passes,
            merge_counts=fetchMergeCounts(),
        )

        _traceProgressModuleEnd(current_module)

        if changed:
            finished = False

    # Unregister collection traces from now unused code, dropping the trace
    # collections of functions no longer used. This must be done after global
    # optimization due to cross module usages.
    for current_module in ModuleRegistry.getDoneModules():
        if current_module.isCompiledPythonModule():
            for unused_function in current_module.getUnusedFunctions():
                Variables.updateVariablesFromCollection(
                    old_collection=unused_function.trace_collection,
                    new_collection=None,
                    source_ref=unused_function.getSourceReference(),
                )

                unused_function.trace_collection = None
                unused_function.finalize()

            current_module.subnode_functions = tuple(
                function
                for function in current_module.subnode_functions
                if function in current_module.getUsedFunctions()
            )

    _endProgress()

    return finished

def optimizeModules(output_filename):
    Graphs.startGraph()

    finished = makeOptimizationPass()

    # Demote compiled modules to bytecode, now that imports had a chance to be resolved, and
    # dependencies were handled.
    for module in ModuleRegistry.getDoneModules():
        if (
            module.isCompiledPythonModule()
            and module.getCompilationMode() == "bytecode"
        ):
            demoteCompiledModuleToBytecode(module)

    # Second, "endless" pass.
    while not finished:
        finished = makeOptimizationPass()

    Graphs.endGraph(output_filename)
```
需要關注的是，這邊是我一開始想優化的地方optimizeModule
```python
        with TimerReport(
            message="Optimizing %s" % module_name, decider=False
        ) as module_timer:
            changed, micro_passes = optimizeModule(current_module)
```
這邊有三種module type
```python
def optimizeModule(module):
    # The tag set is global, so it can track changes without context.
    # pylint: disable=global-statement
    global tag_set
    tag_set = TagSet()

    addExtraSysPaths(Plugins.getModuleSysPathAdditions(module.getFullName()))

    if module.isPythonExtensionModule():
        optimizeExtensionModule(module)
        return False, 0
    elif module.isCompiledPythonModule():
        return optimizeCompiledPythonModule(module)
    else:
        optimizeUncompiledPythonModule(module)
        return False, 0

```

其中attemptRecursion()可以看到裡面其實有時做cache 機制
```python
 module.attemptRecursion()

```
這邊會遞迴找尋依賴的 module
```python

    def attemptRecursion(self):
        # Make sure the package is recursed to if any
        package_name = self.module_name.getPackageName()
        if package_name is None:
            return ()

        # Return the list of newly added modules.

        package = getModuleByName(package_name)

        if package_name is not None and package is None:
            (
                _package_name,
                package_filename,
                package_module_kind,
                finding,
            ) = locateModule(
                module_name=package_name,
                parent_package=None,
                level=0,
            )

            # If we can't find the package for Python3.3 that is semi-OK, it might be in a
            # namespace package, these have no init code.
            if python_version >= 0x300 and not package_filename:
                return ()

            if package_name == "uniconvertor.app.modules":
                return ()

            assert package_filename is not None, (package_name, finding)

            assert _package_name == package_name, (
                package_filename,
                _package_name,
                package_name,
            )

            decision, _reason = decideRecursion(
                using_module_name=self.getFullName(),
                module_filename=package_filename,
                module_name=package_name,
                module_kind=package_module_kind,
            )

            if decision is not None:
                package = recurseTo(
                    module_name=package_name,
                    module_filename=package_filename,
                    module_kind=package_module_kind,
                    source_ref=self.source_ref,
                    reason="parent package",
                    using_module_name=self.module_name,
                )

        if package:
            from nuitka.ModuleRegistry import addUsedModule

            addUsedModule(
                package,
                using_module=self,
                usage_tag="package",
                reason="Containing package of '%s'." % self.getFullName(),
                source_ref=self.source_ref,
            )
```

這邊要關注recurseTo
```python
def recurseTo(
    module_name,
    module_filename,
    module_kind,
    source_ref,
    reason,
    using_module_name,
):
    try:
        module = ImportCache.getImportedModuleByNameAndPath(
            module_name, module_filename
        )
    except KeyError:
        module = None

    if module is None:
        Plugins.onModuleRecursion(
            module_filename=module_filename,
            module_name=module_name,
            module_kind=module_kind,
            using_module_name=using_module_name,
            source_ref=source_ref,
            reason=reason,
        )

        module = _recurseTo(
            module_name=module_name,
            module_filename=module_filename,
            module_kind=module_kind,
            reason=reason,
        )

    return module
```
這邊其實就是做cache 的地方了，假設之前沒遇過的module透過 遞迴找到的module 會存到ImportCache.addImportedModule(module)
```python
def _recurseTo(module_name, module_filename, module_kind, reason):
    from nuitka.tree import Building

    module = Building.buildModule(
        module_name=module_name,
        module_kind=module_kind,
        module_filename=module_filename,
        reason=reason,
        source_code=None,
        is_top=False,
        is_main=False,
        is_fake=False,
        hide_syntax_error=True,
    )

    ImportCache.addImportedModule(module)

    return module

```
而前一行建立 module 的function 其實可以在裡面看到 load module cache 的地方
```pyhton
    module = Building.buildModule(
        module_name=module_name,
        module_kind=module_kind,
        module_filename=module_filename,
        reason=reason,
        source_code=None,
        is_top=False,
        is_main=False,
        is_fake=False,
        hide_syntax_error=True,
    )
```
buildModule =>_createModule =>
```pyhton
def buildModule(
    module_name,
    module_kind,
    module_filename,
    reason,
    source_code,
    is_top,
    is_main,
    is_fake,
    hide_syntax_error,
):
    # Many details to deal with,
    # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    (
        main_added,
        is_package,
        is_namespace,
        source_ref,
        source_filename,
    ) = Importing.decideModuleSourceRef(
        filename=module_filename,
        module_name=module_name,
        is_main=is_main,
        is_fake=is_fake,
        logger=general,
    )

    if hasPythonFlagPackageMode():
        if is_top and shallMakeModule():
            optimization_logger.warning(
                "Python flag -m (package_mode) has no effect in module mode, it's only for executables."
            )
        elif is_main and not main_added:
            optimization_logger.warning(
                "Python flag -m (package_mode) only works on packages with '__main__.py'."
            )

    # Handle bytecode module case immediately.
    if module_kind == "pyc":
        return makeUncompiledPythonModule(
            module_name=module_name,
            reason=reason,
            filename=module_filename,
            bytecode=loadCodeObjectData(module_filename),
            is_package=is_package,
            technical=module_name in detectEarlyImports(),
        )

    # Read source code if necessary. Might give a SyntaxError due to not being proper
    # encoded source.
    if source_filename is not None and not is_namespace and module_kind == "py":
        # For fake modules, source is provided directly.
        original_source_code = None
        contributing_plugins = ()

        if source_code is None:
            try:
                (
                    source_code,
                    original_source_code,
                    contributing_plugins,
                ) = readSourceCodeFromFilenameWithInformation(
                    module_name=module_name, source_filename=source_filename
                )
            except SyntaxError as e:
                # Avoid hiding our own syntax errors.
                if not hasattr(e, "generated_by_nuitka"):
                    raise

                # Do not hide SyntaxError in main module.
                if not hide_syntax_error:
                    raise

                return _makeModuleBodyFromSyntaxError(
                    exc=e,
                    module_name=module_name,
                    reason=reason,
                    module_filename=module_filename,
                )

        try:
            with withNoSyntaxWarning():
                ast_tree = parseSourceCodeToAst(
                    source_code=source_code,
                    module_name=module_name,
                    filename=source_filename,
                    line_offset=0,
                )
        except (SyntaxError, IndentationError) as e:
            # Do not hide SyntaxError if asked not to.
            if not hide_syntax_error:
                raise

            if original_source_code is not None:
                try:
                    parseSourceCodeToAst(
                        source_code=original_source_code,
                        module_name=module_name,
                        filename=source_filename,
                        line_offset=0,
                    )
                except (SyntaxError, IndentationError):
                    # Also an exception without the plugins, that is OK
                    pass
                else:
                    source_diff = getSourceCodeDiff(original_source_code, source_code)

                    for line in source_diff:
                        plugins_logger.warning(line, keep_format=True)

                    if len(contributing_plugins) == 1:
                        next(iter(contributing_plugins)).sysexit(
                            "Making changes to '%s' that cause SyntaxError '%s'"
                            % (module_name, e)
                        )
                    else:
                        plugins_logger.sysexit(
                            "One of the plugins '%s' is making changes to '%s' that cause SyntaxError '%s'"
                            % (",".join(contributing_plugins), module_name, e)
                        )

            return _makeModuleBodyFromSyntaxError(
                exc=e,
                module_name=module_name,
                reason=reason,
                module_filename=module_filename,
            )
        except CodeTooComplexCode:
            # Do not hide CodeTooComplexCode in main module.
            if is_main:
                raise

            return _makeModuleBodyTooComplex(
                module_name=module_name,
                reason=reason,
                module_filename=module_filename,
                source_code=source_code,
                is_package=is_package,
            )
    else:
        ast_tree = None
        source_code = None

    module = _createModule(
        module_name=module_name,
        module_filename=None if is_fake else module_filename,
        module_kind=module_kind,
        reason=reason,
        source_code=source_code,
        source_ref=source_ref,
        is_top=is_top,
        is_main=is_main,
        is_namespace=is_namespace,
        is_package=is_package,
        main_added=main_added,
    )

    if is_top:
        ModuleRegistry.addRootModule(module)

        OutputDirectories.setMainModule(module)

    if module.isCompiledPythonModule() and source_code is not None:
        try:
            createModuleTree(
                module=module,
                source_ref=source_ref,
                ast_tree=ast_tree,
                is_main=is_main,
            )
        except CodeTooComplexCode:
            # Do not hide CodeTooComplexCode in main module.
            if is_main or is_top:
                raise

            return _makeModuleBodyTooComplex(
                module_name=module_name,
                reason=reason,
                module_filename=module_filename,
                source_code=source_code,
                is_package=is_package,
            )

    return module
```

其中可以看到
_loadUncompiledModuleFromCache這邊就是load cache 的核心
```python
def _createModule(
    module_name,
    module_filename,
    module_kind,
    reason,
    source_code,
    source_ref,
    is_namespace,
    is_package,
    is_top,
    is_main,
    main_added,
):

    is_stdlib = module_filename is not None and isStandardLibraryPath(module_filename)

    if module_kind == "extension":
        result = PythonExtensionModule(
            module_name=module_name,
            module_filename=module_filename,
            reason=reason,
            technical=is_stdlib and module_name in detectEarlyImports(),
            source_ref=source_ref,
        )
    elif is_main:
        assert reason == "main", reason

        result = PythonMainModule(
            main_added=main_added,
            module_name=module_name,
            mode=decideCompilationMode(
                is_top=is_top,
                module_name=module_name,
                module_filename=module_filename,
                for_pgo=False,
            ),
            future_spec=None,
            source_ref=source_ref,
        )

        checkPythonVersionFromCode(source_code)
    elif is_namespace:
        result = createNamespacePackage(
            module_name=module_name,
            reason=reason,
            is_top=is_top,
            source_ref=source_ref,
        )
    else:
        mode = decideCompilationMode(
            is_top=is_top,
            module_name=module_name,
            module_filename=module_filename,
            for_pgo=False,
        )

        if (
            mode == "bytecode"
            and not is_top
            and not shallDisableBytecodeCacheUsage()
            and hasCachedImportedModuleUsageAttempts(
                module_name=module_name, source_code=source_code, source_ref=source_ref
            )
        ):
            result = _loadUncompiledModuleFromCache(
                module_name=module_name,
                reason=reason,
                is_package=is_package,
                source_code=source_code,
                source_ref=source_ref,
            )

            # Not used anymore
            source_code = None
        else:
            if is_package:
                result = CompiledPythonPackage(
                    module_name=module_name,
                    reason=reason,
                    is_top=is_top,
                    mode=mode,
                    future_spec=None,
                    source_ref=source_ref,
                )
            else:
                result = CompiledPythonModule(
                    module_name=module_name,
                    reason=reason,
                    is_top=is_top,
                    mode=mode,
                    future_spec=None,
                    source_ref=source_ref,
                )

    return result
```

這邊的 getCachedImportedModuleUsageAttempts 就是去撈存在json 的 module 的各個路徑
```python

def _loadUncompiledModuleFromCache(
    module_name, reason, is_package, source_code, source_ref
):  

    result = makeUncompiledPythonModule(
        module_name=module_name,
        reason=reason,
        filename=source_ref.getFilename(),
        bytecode=demoteSourceCodeToBytecode(
            module_name=module_name,
            source_code=source_code,
            filename=source_ref.getFilename(),
        ),
        technical=module_name in detectEarlyImports(),
        is_package=is_package,
    )

    used_modules = OrderedSet()

    used_modules = getCachedImportedModuleUsageAttempts(
        module_name=module_name, source_code=source_code, source_ref=source_ref
    )

    # assert not is_package, (module_name, used_modules, result, result.getCompileTimeFilename())

    result.setUsedModules(used_modules)

    return result

```

```python

def getCachedImportedModuleUsageAttempts(module_name, source_code, source_ref):
    
    cache_name = makeCacheName(module_name, source_code)
    cache_filename = _getCacheFilename(cache_name, "json")

    if not os.path.exists(cache_filename):
        return None

    data = loadJsonFromFilename(cache_filename)
    print("add test",cache_filename)
    if data is None:
        return None

    if data.get("file_format_version") != _cache_format_version:
        return None

    if data["module_name"] != module_name:
        return None

    result = OrderedSet()

    for module_used in data["modules_used"]:
        used_module_name = ModuleName(module_used["module_name"])

        # Retry the module scan to see if it still gives same result
        if module_used["finding"] == "relative":
            _used_module_name, filename, module_kind, finding = locateModule(
                module_name=used_module_name.getBasename(),
                parent_package=used_module_name.getPackageName(),
                level=1,
            )
        else:
            _used_module_name, filename, module_kind, finding = locateModule(
                module_name=used_module_name, parent_package=None, level=0
            )

        if (
            finding != module_used["finding"]
            or module_kind != module_used["module_kind"]
        ):
            assert module_name != "email._header_value_parser", (
                finding,
                module_used["finding"],
            )

            return None

        result.add(
            makeModuleUsageAttempt(
                module_name=used_module_name,
                filename=filename,
                finding=module_used["finding"],
                module_kind=module_used["module_kind"],
                # TODO: Level might have to be dropped.
                level=0,
                # We store only the line number, so this cheats it to at full one.
                source_ref=source_ref.atLineNumber(module_used["source_ref_line"]),
                reason=module_used["reason"],
            )
        )

    for module_used in data["distribution_names"]:
        # TODO: Consider distributions found and not found and return None if
        # something changed there.
        pass

    return result
```

```
add test /root/.cache/Nuitka/module-cache/functools@6f55d84b07fe21822d6580fa0cc48ba6@13d363d7c34fe331426e37bf7696c311.json
add test /root/.cache/Nuitka/module-cache/importlib@6f55d84b07fe21822d6580fa0cc48ba6@9ba1a7efe39543a96efe13a91b57b8d1.json
add test /root/.cache/Nuitka/module-cache/importlib@6f55d84b07fe21822d6580fa0cc48ba6@9ba1a7efe39543a96efe13a91b57b8d1.json
add test /root/.cache/Nuitka/module-cache/inspect@99d5702d32117a583f47ffcdeef829eb@871d90d3ff28338d5df2c4752edc5013.json
add test /root/.cache/Nuitka/module-cache/inspect@99d5702d32117a583f47ffcdeef829eb@871d90d3ff28338d5df2c4752edc5013.json
add test /root/.cache/Nuitka/module-cache/logging@6f55d84b07fe21822d6580fa0cc48ba6@7426f300ca25f73ae2d58a8d12f79e98.json
add test /root/.cache/Nuitka/module-cache/logging@6f55d84b07fe21822d6580fa0cc48ba6@7426f300ca25f73ae2d58a8d12f79e98.json
add test /root/.cache/Nuitka/module-cache/numbers@6f55d84b07fe21822d6580fa0cc48ba6@05fb1bc183478279024344474aceb99d.json
add test /root/.cache/Nuitka/module-cache/numbers@6f55d84b07fe21822d6580fa0cc48ba6@05fb1bc183478279024344474aceb99d.json
add test /root/.cache/Nuitka/module-cache/re@6f55d84b07fe21822d6580fa0cc48ba6@1b88c6fb134b9d2d3415304d358eb9a3.json
```
到這邊就大概知道實作cache這邊到底是怎麼完成的了
![image](https://hackmd.io/_uploads/BybwcUbDkg.png)

