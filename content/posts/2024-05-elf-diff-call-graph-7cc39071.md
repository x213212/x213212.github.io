---
title: "elf diff call graph"
date: "2024-05-26T02:47:00.003+08:00"
updated: "2024-05-26T02:47:23.098+08:00"
permalink: "/2024/05/elf-diff-call-graph.html"
original_url: "https://x8795278.blogspot.com/2024/05/elf-diff-call-graph.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3825997524476207552"
tags: ["elf diff", "RISC-V"]
layout: post
---

![](https://hackmd.io/_uploads/rkHQzhkNR.png)

elf diff tool
最近在想可不可以將分析的路徑在減少一點，這樣在分析code size 會更省事
```python
import subprocess
import re
from graphviz import Digraph

def generate_objdump_output(elf_file, output_file):
    cmd = ['riscv64-elf-objdump', '-d', elf_file]
    with open(output_file, 'w') as f:
        subprocess.run(cmd, stdout=f)

def parse_objdump(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    functions = {}
    current_function = None
    asm_code = []

    function_pattern = re.compile(r'([0-9a-f]+) <(.+)>:')
    call_pattern = re.compile(r'\s*([0-9a-f]+):\s+[0-9a-f]+\s+call\s+[0-9a-f]+\s+<(.+)>')
    
    for line in lines:
        function_match = function_pattern.match(line)
        if function_match:
            if current_function:
                functions[current_function]['asm'] = asm_code
            addr, name = function_match.groups()
            current_function = name
            asm_code = []
            functions[name] = {'address': addr, 'calls': [], 'asm': []}
        
        if current_function:
            asm_code.append(line.strip())
            call_match = call_pattern.match(line)
            if call_match:
                call_addr, callee = call_match.groups()
                functions[current_function]['calls'].append(callee)
    
    if current_function:
        functions[current_function]['asm'] = asm_code
    
    return functions

def build_call_graph(functions):
    call_graph = {}
    for function, details in functions.items():
        call_graph[function] = details['calls']
    return call_graph

def analyze_calls(func, functions):
    calls = []
    for line in functions[func]['asm']:
        for callee in functions:
            if f"<{callee}>" in line and callee != func:
                calls.append(callee)
    return calls

def generate_paths(functions, start):
    paths = []
    stack = [(start, [start])]
    
    while stack:
        (func, path) = stack.pop()
        calls = analyze_calls(func, functions)
        for callee in calls:
            if callee not in path:
                stack.append((callee, path + [callee]))
            else:
                paths.append(path + [callee])
        if not calls:  # No more calls, dead-end
            paths.append(path)
    
    return paths

def main():
    elf_files = ['yuvconvert-clang.elf', 'yuvconvert-gcc.elf']
    objdump_files = ['yuvconvert-clang.dis', 'yuvconvert-gcc.dis']
    entry_function = 'main'

    all_functions = {}
    all_paths = []

    for elf_file, objdump_file in zip(elf_files, objdump_files):
        generate_objdump_output(elf_file, objdump_file)
        functions = parse_objdump(objdump_file)
        all_functions[elf_file] = functions
        if entry_function in functions:
            paths = generate_paths(functions, entry_function)
            all_paths.append(paths)
        else:
            print(f"Entry function '{entry_function}' not found in {elf_file}.")
            return

    # Convert paths to tuples to make them hashable
    all_paths = [[tuple(path) for path in paths] for paths in all_paths]

    # Find common paths and unique paths
    common_paths = set(all_paths[0]) & set(all_paths[1])
    unique_paths = [set(all_paths[0]) - common_paths, set(all_paths[1]) - common_paths]

    # Create graph with left-to-right layout for all paths
    dot_all = Digraph(comment='Function Call Graph - All Paths', graph_attr={'rankdir': 'LR'})

    drawn_edges_all = set()

    for path in common_paths:
        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            if edge not in drawn_edges_all:
                dot_all.edge(path[i], path[i + 1], color='purple')
                drawn_edges_all.add(edge)

    for i, paths in enumerate(unique_paths):
        color = 'blue' if i == 0 else 'red'
        for path in paths:
            for j in range(len(path) - 1):
                edge = (path[j], path[j + 1])
                if edge not in drawn_edges_all:
                    dot_all.edge(path[j], path[j + 1], color=color)
                    drawn_edges_all.add(edge)

    dot_all.render('function_call_graph_all', format='dot')

    # Create graph with left-to-right layout for unique paths only
    dot_unique = Digraph(comment='Function Call Graph - Unique Paths', graph_attr={'rankdir': 'LR'})

    drawn_edges_unique = set()

    for i, paths in enumerate(unique_paths):
        color = 'blue' if i == 0 else 'red'
        for path in paths:
            for j in range(len(path) - 1):
                edge = (path[j], path[j + 1])
                if edge not in drawn_edges_unique:
                    dot_unique.edge(path[j], path[j + 1], color=color)
                    drawn_edges_unique.add(edge)

    dot_unique.render('function_call_graph_unique', format='dot')

if __name__ == '__main__':
    main()

```
```graphviz
digraph {
	graph [bb="0,0,2362.9,4117",
		rankdir=LR
	];
	node [label="\N"];
	main	 [height=0.5,
		pos="30.348,666",
		width=0.84299];
	I420Scale	 [height=0.5,
		pos="300.31,1589",
		width=1.3791];
	main -> I420Scale	 [color=purple,
		pos="e,285.19,1571.8 31.241,684.28 35.734,772.73 57.216,1156.7 96.695,1269 139.32,1390.2 235.27,1512.6 278.48,1563.9"];
	iprintf	 [height=0.5,
		pos="663.05,904",
		width=0.97706];
	main -> iprintf	 [color=purple,
		pos="e,628.69,908.42 32.893,684.21 40.176,733.42 62.777,867.06 96.695,893 177.74,954.98 499.46,923.72 618.48,909.64"];
	fprintf	 [height=0.5,
		pos="300.31,774",
		width=0.99181];
	main -> fprintf	 [color=purple,
		pos="e,264.74,776.89 39.408,683.55 50.262,702.62 70.333,732.32 96.695,747 145.62,774.25 211.15,778.23 254.5,777.23"];
	_Znaj	 [height=0.5,
		pos="300.31,720",
		width=0.93231];
	main -> _Znaj	 [color=purple,
		pos="e,266.65,718.17 54.105,677.39 66.532,682.9 82.15,689.14 96.695,693 150.71,707.32 214.9,714.23 256.56,717.43"];
	_ZL9PrintHelpPKc	 [height=0.5,
		pos="300.31,866",
		width=2.4074];
	main -> _ZL9PrintHelpPKc	 [color=purple,
		pos="e,217.35,871.23 31.782,684.1 35.593,719.1 49.21,795.97 96.695,834 127.46,858.64 169.45,868 207.31,870.67"];
	exit	 [height=0.5,
		pos="663.05,796",
		width=0.75];
	main -> exit	 [color=purple,
		pos="e,636.37,799.9 33.083,684.02 38.773,714.41 55.02,775.05 96.695,801 185.13,856.08 515.24,816.54 626.32,801.29"];
	memset	 [height=0.5,
		pos="1075.2,1367",
		width=1.1409];
	main -> memset	 [color=purple,
		pos="e,1035,1371.1 31.86,684.08 38.704,764.05 67.692,1083.6 96.695,1117 342.57,1400.5 861.34,1384.7 1024.8,1371.9"];
	ARGBAttenuate	 [height=0.5,
		pos="1512,1035",
		width=2.0944];
	main -> ARGBAttenuate	 [color=purple,
		pos="e,1436.5,1035.8 31.07,684.12 34.022,747.88 47.46,960.31 96.695,1002 147.53,1045 1127.3,1038.8 1426.2,1035.9"];
	putchar	 [height=0.5,
		pos="300.31,666",
		width=1.1109];
	main -> putchar	 [color=purple,
		pos="e,259.91,666 60.791,666 106.65,666 193.99,666 249.57,666"];
	fputs	 [height=0.5,
		pos="300.31,612",
		width=0.84299];
	main -> fputs	 [color=purple,
		pos="e,269.83,613.62 54.105,654.61 66.532,649.1 82.15,642.86 96.695,639 152.14,624.3 218.31,617.41 259.82,614.32"];
	strcmp	 [height=0.5,
		pos="300.31,558",
		width=1.0366];
	main -> strcmp	 [color=purple,
		pos="e,263.22,555.04 39.408,648.45 50.262,629.38 70.333,599.68 96.695,585 145.05,558.07 209.61,553.87 252.96,554.74"];
	fopen	 [height=0.5,
		pos="300.31,504",
		width=0.91732];
	main -> fopen	 [color=purple,
		pos="e,268.02,499.54 33.565,648.07 39.912,618.39 57.032,559.49 96.695,531 143.88,497.1 213.49,495.42 257.86,498.67"];
	fread	 [height=0.5,
		pos="300.31,450",
		width=0.85744];
	main -> fread	 [color=purple,
		pos="e,270.3,445.02 34.179,647.91 43.634,605.06 69.305,499.26 96.695,477 142.9,439.44 215.47,439.39 260.34,443.9"];
	strstr	 [height=0.5,
		pos="300.31,396",
		width=0.84291];
	main -> strstr	 [color=purple,
		pos="e,271,390.71 32.705,647.84 39.729,596.69 62.197,453.14 96.695,423 141.91,383.5 215.74,384.28 260.97,389.44"];
	fseek	 [height=0.5,
		pos="300.31,342",
		width=0.87247];
	main -> fseek	 [color=purple,
		pos="e,270.38,336.37 31.752,647.72 36.652,589.07 55.002,407.18 96.695,369 140.86,328.56 214.69,329.56 260.27,335.03"];
	fclose	 [height=0.5,
		pos="300.31,288",
		width=0.94701];
	main -> fclose	 [color=purple,
		pos="e,267.96,281.84 31.074,647.72 34.07,582.31 47.713,361.36 96.695,315 139.55,274.44 212.09,275.03 258.02,280.53"];
	fwrite	 [height=0.5,
		pos="300.31,234",
		width=0.94699];
	main -> fwrite	 [color=purple,
		pos="e,268.19,227.74 30.568,647.95 31.834,576.63 40.308,315.69 96.695,261 139.17,219.8 212.14,220.67 258.22,226.38"];
	_ZL29ExtractResolutionFromFilenamePKcPiS1_	 [height=0.5,
		pos="300.31,180",
		width=5.656];
	main -> _ZL29ExtractResolutionFromFilenamePKcPiS1_	 [color=purple,
		pos="e,121.29,188.89 31.695,647.76 37.88,566.35 64.626,238.7 96.695,207 101.64,202.12 107.01,197.82 112.71,194.05"];
	_ZdaPv	 [height=0.5,
		pos="300.31,126",
		width=1.141];
	main -> _ZdaPv	 [color=purple,
		pos="e,262.51,118.73 31.392,648 36.591,561.23 60.875,188.94 96.695,153 136.83,112.73 205.96,112.15 252.39,117.44"];
	atoi	 [height=0.5,
		pos="300.31,72",
		width=0.75];
	main -> atoi	 [color=purple,
		pos="e,274.45,66.532 31.161,647.98 35.492,555.72 57.144,139.16 96.695,99 140.22,54.803 218.61,58.203 264.38,64.923"];
	ARGBScaleClip	 [height=0.5,
		pos="663.05,3512",
		width=2.0947];
	main -> ARGBScaleClip	 [color=blue,
		pos="e,655.88,3493.7 31.067,684.14 35.709,799.04 62.323,1427.1 96.695,1616 238.94,2397.7 586.41,3314.4 652.21,3484.2"];
	ARGBUnattenuate	 [height=0.5,
		pos="1512,981",
		width=2.3476];
	main -> ARGBUnattenuate	 [color=blue,
		pos="e,1430.1,985.81 31.533,684.13 35.806,743.17 52.56,928.17 96.695,964 198.92,1047 1122,1002.9 1419.8,986.39"];
	ARGBToI420	 [height=0.5,
		pos="1075.2,1305",
		width=1.8413];
	main -> ARGBToI420	 [color=blue,
		pos="e,1024.8,1293.1 31.044,684.45 33.992,752.68 47.648,989.47 96.695,1043 128.86,1078.1 806.92,1241.3 1015,1290.8"];
	OUTLINED_FUNCTION_0	 [height=0.5,
		pos="1825.9,873",
		width=3.4202];
	main -> OUTLINED_FUNCTION_0	 [color=blue,
		pos="e,1716,881.15 32.168,684.01 37.999,737.66 58.122,894.64 96.695,925 174.1,985.92 441.42,930.33 539.93,931 649.37,931.74 676.78,934.05 \
786.18,931 1119.5,921.71 1512.3,895.7 1705.8,881.88"];
	__cxa_throw_bad_array_new_length	 [height=0.5,
		pos="300.31,18",
		width=4.299];
	main -> __cxa_throw_bad_array_new_length	 [color=red,
		pos="e,146.93,15.587 30.971,647.9 34.506,550.28 53.41,89.398 96.695,45 108.19,33.212 122.16,24.797 137.34,18.923"];
	ScalePlane	 [height=0.5,
		pos="663.05,2387",
		width=1.4834];
	I420Scale -> ScalePlane	 [color=purple,
		pos="e,654.95,2369.2 308.4,1606.8 355.42,1710.2 593.56,2234.1 650.71,2359.8"];
	OUTLINED_FUNCTION_5	 [height=0.5,
		pos="1825.9,1035",
		width=3.4202];
	I420Scale -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1745.9,1048.7 322.59,1572.9 392.76,1522.7 616.68,1367.5 822.18,1278 1052.2,1177.9 1120,1177.9 1364.1,1120 1433.2,1103.6 1622.2,\
1070.2 1735.9,1050.5"];
	OUTLINED_FUNCTION_18	 [height=0.5,
		pos="1825.9,1721",
		width=3.5544];
	I420Scale -> OUTLINED_FUNCTION_18	 [color=blue,
		pos="e,1762.7,1705.3 349.99,1590.4 437.96,1593.1 626.87,1599.3 786.18,1608 1175.3,1629.2 1275.4,1619.4 1659.8,1684 1690.4,1689.2 1723.9,\
1696.3 1752.7,1703"];
	OUTLINED_FUNCTION_1	 [height=0.5,
		pos="663.05,1635",
		width=3.4202];
	I420Scale -> OUTLINED_FUNCTION_1	 [color=blue,
		pos="e,570.02,1623.2 347.36,1595 400.9,1601.8 489.95,1613 559.85,1621.9"];
	ScalePlaneBilinearDown	 [height=0.5,
		pos="1075.2,2295",
		width=3.0031];
	ScalePlane -> ScalePlaneBilinearDown	 [color=purple,
		pos="e,975.66,2302.1 694.95,2372.4 726.59,2358.6 776.76,2338.3 822.18,2327 868.52,2315.5 920.71,2308 965.6,2303.2"];
	ScalePlaneBilinearUp	 [height=0.5,
		pos="1075.2,2241",
		width=2.6753];
	ScalePlane -> ScalePlaneBilinearUp	 [color=purple,
		pos="e,979.21,2239.3 679.72,2369.6 706.74,2342.5 763.1,2291.2 822.18,2268 868.34,2249.9 922.66,2242.5 969.12,2239.8"];
	ScaleSlope	 [height=0.5,
		pos="1512,2527",
		width=1.4985];
	ScalePlane -> ScaleSlope	 [color=purple,
		pos="e,1458.9,2530.6 709.03,2377.8 843.38,2351.9 1231.9,2285.4 1328.1,2360 1378.9,2399.4 1317.1,2456.2 1364.1,2500 1386.6,2520.9 1419.6,\
2528.3 1448.8,2530.2"];
	malloc	 [height=0.5,
		pos="1512,2895",
		width=1.0366];
	ScalePlane -> malloc	 [color=purple,
		pos="e,1474.8,2896.9 666.03,2405.2 679.84,2487.6 740.61,2823.5 822.18,2884 873.43,2922 1317.5,2904.4 1464.7,2897.4"];
	ScalePlaneUp2_Bilinear	 [height=0.5,
		pos="1075.2,3171",
		width=2.9435];
	ScalePlane -> ScalePlaneUp2_Bilinear	 [color=purple,
		pos="e,1002.8,3184.2 664.08,2405.3 670.38,2510.8 707.49,3040.3 822.18,3144 867.53,3185 937.78,3189.6 992.75,3185.1"];
	__assert_func	 [height=0.5,
		pos="2115.2,2764",
		width=1.7962];
	ScalePlane -> __assert_func	 [color=purple,
		pos="e,2113.8,2746 663.98,2368.9 669.75,2264.6 704.36,1741.2 822.18,1646 914.11,1571.7 1943.9,1682.7 1956.1,1694 2035.2,1767.7 2100.7,\
2574.1 2113.1,2735.9"];
	ScaleColsUp2_C	 [height=0.5,
		pos="1512,2149",
		width=2.1543];
	ScalePlane -> ScaleColsUp2_C	 [color=purple,
		pos="e,1443.9,2157.7 673.01,2369.3 694.68,2332.8 750,2249.4 822.18,2214 923.5,2164.3 1215.9,2182.5 1328.1,2171 1362.9,2167.4 1401.3,2162.9 \
1434,2158.9"];
	ScaleRowDown2Box_C	 [height=0.5,
		pos="1075.2,2987",
		width=2.944];
	ScalePlane -> ScaleRowDown2Box_C	 [color=purple,
		pos="e,992.66,2998.3 665.45,2405.2 677.5,2493.8 734.46,2879.3 822.18,2955 865.56,2992.4 929.73,3000.2 982.59,2998.7"];
	ScaleRowDown2_C	 [height=0.5,
		pos="1075.2,2857",
		width=2.4968];
	ScalePlane -> ScaleRowDown2_C	 [color=purple,
		pos="e,1005,2868.3 666.9,2405.1 683.42,2481.3 750.78,2773.9 822.18,2830 870.3,2867.8 940.45,2872.6 994.68,2869"];
	ScaleFilterReduce	 [height=0.5,
		pos="1512,3377",
		width=2.273];
	ScalePlane -> ScaleFilterReduce	 [color=purple,
		pos="e,1430.5,3378.7 663.43,2405.3 666.2,2522.2 687.5,3165.2 822.18,3293 906.29,3372.8 1252.9,3380.1 1420.5,3378.8"];
	CopyPlane	 [height=0.5,
		pos="1825.9,4099",
		width=1.4838];
	ScalePlane -> CopyPlane	 [color=purple,
		pos="e,1775.2,4104.8 664.61,2405.4 676.94,2550.7 760.29,3508.4 822.18,3620 973.21,3892.3 1075.1,3948.2 1364.1,4064 1499.3,4118.1 1674.2,\
4113.2 1765.1,4105.7"];
	ScaleRowDown34_1_Box_C	 [height=0.5,
		pos="1825.9,3056",
		width=3.4805];
	ScalePlane -> ScaleRowDown34_1_Box_C	 [color=purple,
		pos="e,1707,3061.9 664.57,2405 673.1,2501.5 718.36,2955 822.18,3038 888.84,3091.3 1441.2,3073.6 1696.9,3062.3"];
	ScaleCols_C	 [height=0.5,
		pos="1512,2095",
		width=1.6924];
	ScalePlane -> ScaleCols_C	 [color=purple,
		pos="e,1457.9,2103.3 670.05,2368.9 687.87,2325.8 739.45,2216.8 822.18,2171 920.84,2116.4 1217.3,2153.8 1328.1,2133 1344.6,2129.9 1347.9,\
2126 1364.1,2122 1391.3,2115.4 1421.7,2109.6 1447.8,2105.1"];
	ScaleRowDown4Box_C	 [height=0.5,
		pos="1075.2,2803",
		width=2.944];
	ScalePlane -> ScaleRowDown4Box_C	 [color=purple,
		pos="e,993.35,2814.5 664.23,2405.1 669.4,2468.5 695.89,2681.1 822.18,2776 867.54,2810.1 931.06,2816.8 983.11,2815"];
	ScalePlaneVertical	 [height=0.5,
		pos="1512,3285",
		width=2.3472];
	ScalePlane -> ScalePlaneVertical	 [color=purple,
		pos="e,1435.6,3292.7 663.47,2405.3 666.49,2519.7 688.83,3135.4 822.18,3252 909.71,3328.5 1260.5,3308 1425.4,3293.6"];
	ScalePlane -> memset	 [color=purple,
		pos="e,1037.4,1359.6 666.35,2368.8 681.16,2287 742.67,1944.3 786.18,1662 795.07,1604.4 780.94,1443.2 822.18,1402 875.61,1348.6 969.99,\
1350.8 1027.1,1358.2"];
	ScaleRowDown34_C	 [height=0.5,
		pos="1825.9,2918",
		width=2.6309];
	ScalePlane -> ScaleRowDown34_C	 [color=purple,
		pos="e,1786.7,2934.5 664.72,2405 673.85,2499.5 721.13,2935.4 822.18,3014 895.72,3071.2 1569,2996.8 1659.8,2976 1700.3,2966.7 1744.7,2950.9 \
1777.4,2938.2"];
	ScaleRowDown2Linear_C	 [height=0.5,
		pos="1075.2,2749",
		width=3.1968];
	ScalePlane -> ScaleRowDown2Linear_C	 [color=purple,
		pos="e,983.87,2760 665.48,2405.1 674.27,2462.6 710.05,2642.5 822.18,2722 865.5,2752.7 923.92,2760.5 973.71,2760.2"];
	free	 [height=0.5,
		pos="1512,2949",
		width=0.75];
	ScalePlane -> free	 [color=purple,
		pos="e,1484.8,2949.2 665.8,2405.2 678.97,2489.8 738.4,2843.1 822.18,2909 873.59,2949.4 1338,2950 1474.5,2949.3"];
	ScalePlaneUp2_Linear	 [height=0.5,
		pos="1075.2,2479",
		width=2.7794];
	ScalePlane -> ScalePlaneUp2_Linear	 [color=purple,
		pos="e,981.68,2472.5 694.95,2401.6 726.59,2415.4 776.76,2435.7 822.18,2447 870.62,2459 925.45,2466.7 971.66,2471.4"];
	FixedDiv_C	 [height=0.5,
		pos="1512,2695",
		width=1.6329];
	ScalePlane -> FixedDiv_C	 [color=purple,
		pos="e,1467.4,2683.1 709.54,2396.1 741.18,2401.9 784.08,2409.3 822.18,2414 878.14,2420.8 1285.6,2415 1328.1,2452 1385.1,2501.6 1318.3,\
2558 1364.1,2618 1387.3,2648.3 1425.8,2667.8 1457.7,2679.6"];
	ScaleRowDown38_2_Box_C	 [height=0.5,
		pos="1825.9,2277",
		width=3.4805];
	ScalePlane -> ScaleRowDown38_2_Box_C	 [color=purple,
		pos="e,1803.2,2259 668.18,2368.8 682.84,2320.4 729.96,2188.7 822.18,2133 918.72,2074.7 1222.6,2134.6 1328.1,2095 1346.9,2088 1345.2,2074.3 \
1364.1,2068 1426.5,2047.2 1604.6,2032.3 1659.8,2068 1692.5,2089.2 1673.6,2116 1695.8,2148 1724.3,2189.1 1766.9,2228.4 1795.5,2252.6"];
	ScaleRowDown38_C	 [height=0.5,
		pos="1825.9,2121",
		width=2.6309];
	ScalePlane -> ScaleRowDown38_C	 [color=purple,
		pos="e,1799.1,2103.6 666.64,2368.8 678.19,2315.7 719.77,2160.4 822.18,2095 917.14,2034.3 1220.1,2093.8 1328.1,2062 1345.7,2056.8 1346.4,\
2046.6 1364.1,2042 1491.3,2009 1531.6,2013.1 1659.8,2042 1707.6,2052.8 1757.9,2079.1 1790.4,2098.4"];
	ScaleRowDown38_3_Box_C	 [height=0.5,
		pos="1075.2,2035",
		width=3.4805];
	ScalePlane -> ScaleRowDown38_3_Box_C	 [color=purple,
		pos="e,963.77,2026.7 666.04,2368.6 676.19,2312.6 714.94,2143.2 822.18,2067 859.85,2040.2 908.85,2030 953.68,2027.2"];
	ScaleAddRow_C	 [height=0.5,
		pos="1075.2,1981",
		width=2.169];
	ScalePlane -> ScaleAddRow_C	 [color=purple,
		pos="e,1010.5,1970.9 664.44,2368.9 670.25,2306.6 698.53,2100 822.18,2008 872.78,1970.3 945.65,1966.3 1000.2,1970.1"];
	FixedDiv1_C	 [height=0.5,
		pos="1075.2,2387",
		width=1.767];
	ScalePlane -> FixedDiv1_C	 [color=purple,
		pos="e,1011.3,2387 716.51,2387 789.08,2387 919.13,2387 1001.1,2387"];
	ScaleRowDown34_0_Box_C	 [height=0.5,
		pos="1075.2,1927",
		width=3.4805];
	ScalePlane -> ScaleRowDown34_0_Box_C	 [color=purple,
		pos="e,984.54,1914.5 667.02,2369 683.9,2294.1 752.09,2008.7 822.18,1954 864.54,1921 923.75,1913.2 974.24,1914.2"];
	ScaleRowDown4_C	 [height=0.5,
		pos="1075.2,2695",
		width=2.4968];
	ScalePlane -> ScaleRowDown4_C	 [color=purple,
		pos="e,997.96,2704.3 667.18,2405.1 679.94,2456.4 724,2603.5 822.18,2668 870.56,2699.8 935.68,2706.1 987.74,2704.7"];
	_ZN6libyuvL15ScaleAddCols1_CEiiiiPKtPh	 [height=0.5,
		pos="1075.2,1727",
		width=5.1945];
	ScalePlane -> _ZN6libyuvL15ScaleAddCols1_CEiiiiPKtPh	 [color=blue,
		pos="e,967.54,1712.3 664.85,2369 674.63,2274.6 724.68,1838.7 822.18,1754 858.68,1722.3 910.22,1712.8 957.27,1712.2"];
	OUTLINED_FUNCTION_20	 [height=0.5,
		pos="1075.2,2641",
		width=3.5544];
	ScalePlane -> OUTLINED_FUNCTION_20	 [color=blue,
		pos="e,959.2,2648.6 669.62,2405.1 686.78,2449.6 737.61,2564.1 822.18,2614 859.87,2636.2 906.27,2645.3 949,2648.1"];
	OUTLINED_FUNCTION_9	 [height=0.5,
		pos="1825.9,1851",
		width=3.4202];
	ScalePlane -> OUTLINED_FUNCTION_9	 [color=blue,
		pos="e,1703.4,1853.3 666.18,2368.9 680.55,2288 742.99,1960.4 822.18,1900 856.22,1874 1428.5,1859.1 1693.4,1853.5"];
	OUTLINED_FUNCTION_16	 [height=0.5,
		pos="1075.2,2587",
		width=3.5544];
	ScalePlane -> OUTLINED_FUNCTION_16	 [color=blue,
		pos="e,950.49,2591.2 673.24,2404.8 695.14,2441.3 750.57,2523.9 822.18,2560 858.18,2578.1 900.67,2586.8 940.44,2590.4"];
	_ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh	 [height=0.5,
		pos="1075.2,1673",
		width=5.1945];
	ScalePlane -> _ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh	 [color=blue,
		pos="e,971.06,1658 664.49,2368.8 672.71,2269.3 717.23,1792.9 822.18,1700 859.38,1667.1 912.74,1657.9 960.88,1657.9"];
	OUTLINED_FUNCTION_12	 [height=0.5,
		pos="1825.9,1305",
		width=3.5544];
	ScalePlane -> OUTLINED_FUNCTION_12	 [color=blue,
		pos="e,1748.8,1319.4 664.32,2369 672.02,2263.8 716,1730.1 822.18,1613 980.31,1438.5 1104.1,1528.5 1328.1,1456 1492.2,1402.9 1529.4,1377.2 \
1695.8,1332 1709.6,1328.2 1724.4,1324.7 1738.9,1321.5"];
	OUTLINED_FUNCTION_8	 [height=0.5,
		pos="1075.2,2533",
		width=3.4202];
	ScalePlane -> OUTLINED_FUNCTION_8	 [color=blue,
		pos="e,952.03,2533 679.72,2404.4 706.74,2431.5 763.1,2482.8 822.18,2506 859.61,2520.7 902.41,2528.4 942.03,2532.1"];
	OUTLINED_FUNCTION_13	 [height=0.5,
		pos="1075.2,1835",
		width=3.5544];
	ScalePlane -> OUTLINED_FUNCTION_13	 [color=blue,
		pos="e,976.24,1823.5 665.92,2369 679.58,2285.3 740.94,1935.4 822.18,1867 861.47,1833.9 917.1,1824.3 966.19,1823.6"];
	_ZN6libyuvL15ScaleAddCols0_CEiiiiPKtPh	 [height=0.5,
		pos="1075.2,1781",
		width=5.1945];
	ScalePlane -> _ZN6libyuvL15ScaleAddCols0_CEiiiiPKtPh	 [color=blue,
		pos="e,962.78,1766.6 665.32,2368.8 676.88,2278.9 732.22,1884.5 822.18,1808 857.7,1777.8 906.91,1767.9 952.51,1766.7"];
	ScaleAddCols2_C	 [height=0.5,
		pos="1075.2,3225",
		width=2.2884];
	ScalePlane -> ScaleAddCols2_C	 [color=red,
		pos="e,1013.9,3237 663.8,2405.1 668.68,2514.6 699.86,3085.9 822.18,3198 870.32,3242.1 947.2,3244.3 1003.6,3238.2"];
	ScaleAddCols0_C	 [height=0.5,
		pos="1075.2,1429",
		width=2.2884];
	ScalePlane -> ScaleAddCols0_C	 [color=red,
		pos="e,1010.4,1417.8 666.12,2369 688.02,2240 820.02,1463.1 822.18,1461 868.64,1416.6 943.79,1412.2 1000.1,1416.8"];
	ScaleAddCols1_C	 [height=0.5,
		pos="1075.2,3117",
		width=2.2884];
	ScalePlane -> ScaleAddCols1_C	 [color=red,
		pos="e,1009.1,3127.8 664.45,2405.1 672.51,2505.3 716.61,2989.3 822.18,3085 869.28,3127.7 943.11,3132.6 998.89,3128.6"];
	ScaleFilterCols64_C	 [height=0.5,
		pos="1512,2311",
		width=2.5417];
	ScalePlaneBilinearDown -> ScaleFilterCols64_C	 [color=purple,
		pos="e,1422,2307.7 1180.9,2298.9 1251.2,2301.4 1342.9,2304.8 1411.9,2307.3"];
	ScalePlaneBilinearDown -> ScaleSlope	 [color=purple,
		pos="e,1459.2,2531.1 1155.3,2282.9 1210.7,2279.3 1282.5,2284.8 1328.1,2327 1385.8,2380.3 1307.9,2445.2 1364.1,2500 1386.3,2521.6 1419.6,\
2529 1449,2530.7"];
	ScalePlaneBilinearDown -> malloc	 [color=purple,
		pos="e,1475.7,2899.7 1183.4,2295.1 1235.1,2301.2 1293.2,2318 1328.1,2360 1400.6,2446.9 1288.6,2783.7 1364.1,2868 1389,2895.7 1432,2900.9 \
1465.2,2900.1"];
	InterpolateRow_C	 [height=0.5,
		pos="1825.9,3323",
		width=2.2881];
	ScalePlaneBilinearDown -> InterpolateRow_C	 [color=purple,
		pos="e,1802,3305.7 1183.1,2296.5 1234.1,2303.1 1291.7,2319.9 1328.1,2360 1396.9,2435.6 1296,2510.9 1364.1,2587 1455,2688.5 1573.4,2562.6 \
1659.8,2668 1732.4,2756.6 1650.4,3076.9 1695.8,3182 1717,3231.1 1762.8,3274.1 1794,3299.3"];
	ScaleFilterCols_C	 [height=0.5,
		pos="1512,2365",
		width=2.2735];
	ScalePlaneBilinearDown -> ScaleFilterCols_C	 [color=purple,
		pos="e,1445,2354.5 1171.3,2303.3 1218.8,2308.3 1276.9,2316 1328.1,2327 1344.5,2330.5 1347.9,2334 1364.1,2338 1387,2343.6 1412.1,2348.6 \
1435,2352.7"];
	ScalePlaneBilinearDown -> free	 [color=purple,
		pos="e,1485.5,2952.9 1183.5,2295 1235.2,2301 1293.3,2317.9 1328.1,2360 1408,2456.4 1281,2828.5 1364.1,2922 1391.5,2952.7 1441.2,2955.9 \
1475.4,2953.7"];
	OUTLINED_FUNCTION_10	 [height=0.5,
		pos="1512,2473",
		width=3.5544];
	ScalePlaneBilinearDown -> OUTLINED_FUNCTION_10	 [color=blue,
		pos="e,1396.7,2465.1 1160.4,2283.9 1214.4,2281.6 1282.4,2288.4 1328.1,2327 1370.4,2362.7 1322.9,2409.2 1364.1,2446 1371.1,2452.2 1378.9,\
2457.2 1387.3,2461.2"];
	OUTLINED_FUNCTION_21	 [height=0.5,
		pos="1512,2419",
		width=3.5544];
	ScalePlaneBilinearDown -> OUTLINED_FUNCTION_21	 [color=blue,
		pos="e,1401,2410 1172.9,2287.2 1223.1,2287.9 1283.2,2296.5 1328.1,2327 1355.5,2345.5 1337.3,2372.7 1364.1,2392 1372.5,2398 1381.8,2402.8 \
1391.5,2406.6"];
	ScalePlaneBilinearUp -> ScaleFilterCols64_C	 [color=purple,
		pos="e,1436.3,2300.7 1170.2,2244.1 1218.2,2247.5 1277,2254.3 1328.1,2268 1345.1,2272.5 1347.4,2278.8 1364.1,2284 1384,2290.1 1405.7,2295 \
1426.3,2298.9"];
	ScalePlaneBilinearUp -> ScaleSlope	 [color=purple,
		pos="e,1459.5,2531.5 1141.6,2227.9 1198.7,2220.8 1279.3,2221.4 1328.1,2268 1403.7,2340 1291.4,2425.2 1364.1,2500 1385.9,2522.3 1419.5,\
2529.7 1449.2,2531.2"];
	ScalePlaneBilinearUp -> malloc	 [color=purple,
		pos="e,1475.9,2899.7 1138.5,2227.4 1196.5,2219 1280.4,2218 1328.1,2268 1420.4,2364.6 1275.6,2768 1364.1,2868 1389,2896 1432.5,2901.1 \
1465.9,2900.2"];
	ScalePlaneBilinearUp -> ScaleColsUp2_C	 [color=purple,
		pos="e,1437.6,2154.3 1171.2,2242.5 1220.1,2239.9 1279.4,2231.6 1328.1,2209 1347.8,2199.9 1344.7,2185.7 1364.1,2176 1383.6,2166.3 1406.1,\
2160.1 1427.5,2156.1"];
	ScalePlaneBilinearUp -> InterpolateRow_C	 [color=purple,
		pos="e,1801.9,3305.7 1140.5,2227.8 1197.9,2220.3 1279.6,2220.4 1328.1,2268 1419.6,2357.7 1272.9,2464 1364.1,2554 1458.3,2646.8 1568.7,\
2491.2 1659.8,2587 1705.4,2635 1669.8,3121.1 1695.8,3182 1716.8,3231.2 1762.7,3274.2 1793.9,3299.4"];
	ScalePlaneBilinearUp -> ScaleFilterCols_C	 [color=purple,
		pos="e,1430.3,2363.4 1155.1,2230.9 1208.5,2228.4 1278,2233.6 1328.1,2268 1357,2287.8 1336,2317.2 1364.1,2338 1380.4,2350 1400.3,2357.3 \
1420.2,2361.5"];
	ScalePlaneBilinearUp -> ScaleCols_C	 [color=purple,
		pos="e,1451.1,2096 1158.8,2232 1211.2,2223.1 1278,2205.6 1328.1,2171 1350.4,2155.7 1341.2,2136.3 1364.1,2122 1386.9,2107.8 1415.2,2100.6 \
1441,2097.2"];
	ScalePlaneBilinearUp -> free	 [color=purple,
		pos="e,1485.4,2952.9 1138.3,2227.4 1196.3,2219 1280.5,2217.8 1328.1,2268 1428.4,2373.5 1267.9,2812.8 1364.1,2922 1391.4,2952.9 1441.1,\
2955.9 1475.3,2953.8"];
	OUTLINED_FUNCTION_14	 [height=0.5,
		pos="1512,2257",
		width=3.5544];
	ScalePlaneBilinearUp -> OUTLINED_FUNCTION_14	 [color=blue,
		pos="e,1387.9,2252.5 1169.9,2244.5 1230.7,2246.7 1310.4,2249.6 1377.7,2252.1"];
	OUTLINED_FUNCTION_15	 [height=0.5,
		pos="1512,2203",
		width=3.5544];
	ScalePlaneBilinearUp -> OUTLINED_FUNCTION_15	 [color=blue,
		pos="e,1403.1,2212.5 1162.5,2233.4 1228.6,2227.7 1320.1,2219.7 1392.9,2213.4"];
	__divdi3	 [height=0.5,
		pos="1825.9,2649",
		width=1.2604];
	ScaleSlope -> __divdi3	 [color=purple,
		pos="e,1786.8,2639.7 1565.2,2530.4 1594.7,2534.1 1631.2,2542.2 1659.8,2559 1680.7,2571.3 1675.8,2586.2 1695.8,2600 1720.2,2616.9 1751.3,\
2628.9 1776.9,2636.8"];
	ScaleSlope -> __assert_func	 [color=purple,
		pos="e,2108.5,2745.9 1556.9,2516.9 1640.9,2500.3 1825.4,2476.1 1956.1,2546 2034.5,2588 2084.2,2687.7 2104.6,2736.4"];
	ScaleSlope -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1719.1,1044 1563.4,2532.5 1596.2,2532.9 1636.6,2527.1 1659.8,2500 1763.7,2378.5 1593.4,1184.7 1695.8,1062 1700,1056.9 1704.9,1052.7 \
1710.3,1049.1"];
	__udivdi3	 [height=0.5,
		pos="1825.9,2573",
		width=1.3945];
	ScaleSlope -> __udivdi3	 [color=blue,
		pos="e,1779.4,2566.2 1561.4,2534.2 1617.8,2542.5 1710.1,2556 1769.4,2564.7"];
	ScaleSlope -> OUTLINED_FUNCTION_0	 [color=blue,
		pos="e,1719.1,881.98 1563.4,2532.6 1596.2,2533 1636.7,2527.1 1659.8,2500 1717.5,2432.4 1638.9,968.33 1695.8,900 1700,894.94 1704.9,890.67 \
1710.3,887.08"];
	ScalePlaneUp2_Bilinear -> __assert_func	 [color=purple,
		pos="e,2112.4,2782.1 1179,3167.2 1225.2,3163.7 1280,3156.9 1328.1,3144 1345.1,3139.5 1347.2,3132.3 1364.1,3128 1492.1,3095.7 1846.6,3156.6 \
1956.1,3083 2059.2,3013.6 2098.5,2856.7 2110.6,2792.4"];
	ScaleRowUp2_Bilinear_Any_C	 [height=0.5,
		pos="1512,3155",
		width=3.7633];
	ScalePlaneUp2_Bilinear -> ScaleRowUp2_Bilinear_Any_C	 [color=purple,
		pos="e,1381.1,3159.8 1179,3167.2 1236.3,3165.1 1308.4,3162.5 1370.8,3160.2"];
	InterpolateRow_C -> __assert_func	 [color=purple,
		pos="e,2112.2,2782.1 1904.4,3317.2 1923.2,3312.4 1942,3304.4 1956.1,3291 2031.2,3219.7 2093.2,2891 2110.4,2792.2"];
	memcpy	 [height=0.5,
		pos="2318.6,3541",
		width=1.2303];
	InterpolateRow_C -> memcpy	 [color=purple,
		pos="e,2317.5,3522.8 1878.2,3309 1962.5,3289.6 2130,3265.2 2238.3,3342 2294.5,3381.8 2311.4,3467.8 2316.5,3512.6"];
	OUTLINED_FUNCTION_4	 [height=0.5,
		pos="2115.2,3369",
		width=3.4202];
	InterpolateRow_C -> OUTLINED_FUNCTION_4	 [color=blue,
		pos="e,2031.7,3355.7 1892.6,3333.6 1931,3339.7 1979.7,3347.4 2021.7,3354.1"];
	CopyRow_C	 [height=0.5,
		pos="2115.2,3760",
		width=1.7075];
	CopyPlane -> CopyRow_C	 [color=purple,
		pos="e,2111.3,3778.2 1878.8,4096.1 1904.4,4092.3 1934.2,4084.2 1956.1,4067 2049.7,3993.3 2093.8,3849.2 2108.9,3788.3"];
	CopyRow_C -> memcpy	 [color=purple,
		pos="e,2302.8,3558 2131.5,3742.4 2167.6,3703.6 2254.4,3610.1 2295.8,3565.5"];
	ScaleRowDown34_1_Box_C -> __assert_func	 [color=purple,
		pos="e,2101,2781.7 1848.9,3038.1 1875.6,3016.9 1920.5,2980 1956.1,2945 2009,2892.8 2065.2,2825.8 2094.5,2789.8"];
	ScalePlaneVertical -> __assert_func	 [color=purple,
		pos="e,2112,2782.1 1594,3289.6 1706.7,3294.3 1901.6,3295.6 1956.1,3253 2031.9,3193.7 2092.9,2887.2 2110.2,2792.1"];
	ScalePlaneVertical -> InterpolateRow_C	 [color=purple,
		pos="e,1753.9,3314.3 1585.6,3293.9 1633.1,3299.7 1694.9,3307.1 1743.9,3313.1"];
	ScalePlaneVertical -> OUTLINED_FUNCTION_4	 [color=blue,
		pos="e,2056.8,3385 1556.9,3300.3 1587.3,3311.7 1627.5,3328.9 1659.8,3350 1678,3361.9 1675.6,3375.1 1695.8,3383 1812.5,3428.4 1961.6,3406.5 \
2047,3387.2"];
	ScaleRowUp2_Bilinear_C	 [height=0.5,
		pos="1825.9,3155",
		width=3.1673];
	ScaleRowUp2_Bilinear_Any_C -> ScaleRowUp2_Bilinear_C	 [color=purple,
		pos="e,1711.5,3155 1647.8,3155 1665.6,3155 1683.7,3155 1701.2,3155"];
	ScaleRowUp2_Bilinear_C -> __assert_func	 [color=purple,
		pos="e,2112.8,2782.3 1916.8,3144 1931,3139.2 1944.7,3132.5 1956.1,3123 2062.2,3034.1 2100.1,2860.2 2111.2,2792.2"];
	_ZL9PrintHelpPKc -> iprintf	 [color=purple,
		pos="e,628.16,900.35 378.13,874.15 451.18,881.8 557.95,892.99 617.89,899.27"];
	_ZL9PrintHelpPKc -> exit	 [color=purple,
		pos="e,636.97,801.08 375.26,856.79 413.93,851.39 461.73,843.71 503.93,834 520.23,830.25 523.74,827.24 539.93,823 569.01,815.38 602.33,\
808.16 626.98,803.11"];
	puts	 [height=0.5,
		pos="663.05,850",
		width=0.75369];
	_ZL9PrintHelpPKc -> puts	 [color=purple,
		pos="e,635.97,851.19 385.36,862.25 461.49,858.89 569.52,854.13 625.77,851.64"];
	ScaleRowDown34_C -> __assert_func	 [color=purple,
		pos="e,2085.2,2780 1858,2900.9 1911.3,2872.5 2018.2,2815.6 2076,2784.9"];
	ScalePlaneUp2_Linear -> __assert_func	 [color=purple,
		pos="e,2051.1,2761.5 1143.4,2465.8 1200.3,2459.1 1279.6,2460.2 1328.1,2506 1399,2572.8 1291.7,2657 1364.1,2722 1376.7,2733.2 1854,2753.5 \
2041.1,2761.1"];
	ScalePlaneUp2_Linear -> FixedDiv_C	 [color=purple,
		pos="e,1453.1,2696.5 1145.9,2466.2 1202.1,2460.4 1279.2,2462.5 1328.1,2506 1381.7,2553.5 1313.2,2612.7 1364.1,2663 1384.8,2683.4 1415.1,\
2692.1 1443,2695.5"];
	ScaleRowUp2_Linear_Any_C	 [height=0.5,
		pos="1512,2787",
		width=3.5992];
	ScalePlaneUp2_Linear -> ScaleRowUp2_Linear_Any_C	 [color=purple,
		pos="e,1399.2,2778 1142.6,2465.7 1199.7,2458.6 1279.8,2459.4 1328.1,2506 1408.7,2583.6 1287.9,2673.2 1364.1,2755 1371.5,2762.9 1380.2,\
2769 1389.8,2773.8"];
	OUTLINED_FUNCTION_19	 [height=0.5,
		pos="1512,2841",
		width=3.5544];
	ScalePlaneUp2_Linear -> OUTLINED_FUNCTION_19	 [color=blue,
		pos="e,1393.7,2834.1 1141.7,2465.5 1199.1,2458.1 1280.1,2458.5 1328.1,2506 1426.1,2603 1269.9,2713.5 1364.1,2814 1370.1,2820.4 1377,2825.5 \
1384.6,2829.7"];
	FixedDiv_C -> __divdi3	 [color=purple,
		pos="e,1783,2655.3 1565.2,2687.2 1623.2,2678.7 1715.2,2665.2 1773,2656.8"];
	ARGBAttenuateRow_C	 [height=0.5,
		pos="1825.9,927",
		width=2.9141];
	ARGBAttenuate -> ARGBAttenuateRow_C	 [color=purple,
		pos="e,1735.4,936.23 1587,1032.9 1611.8,1029.3 1638.4,1022 1659.8,1008 1683.9,992.15 1671.9,970.14 1695.8,954 1704.9,947.87 1715.1,943.09 \
1725.6,939.36"];
	OUTLINED_FUNCTION_2	 [height=0.5,
		pos="1825.9,981",
		width=3.4202];
	ARGBAttenuate -> OUTLINED_FUNCTION_2	 [color=blue,
		pos="e,1746,994.74 1573.2,1024.5 1619.6,1016.5 1684,1005.4 1736.1,996.45"];
	ARGBAttenuate -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1702.6,1035 1587.6,1035 1619.1,1035 1656.6,1035 1692.5,1035"];
	ARGBAttenuate -> OUTLINED_FUNCTION_0	 [color=blue,
		pos="e,1723.5,883.19 1587.4,1036.2 1613,1033 1640,1025.2 1659.8,1008 1698,974.83 1658,933.62 1695.8,900 1701.4,895.05 1707.6,890.91 1714.2,\
887.47"];
	ScaleRowDown38_2_Box_C -> __assert_func	 [color=purple,
		pos="e,2104.6,2746.2 1836.7,2295.2 1880.8,2369.4 2047.1,2649.4 2099.4,2737.4"];
	ScaleRowUp2_Linear_C	 [height=0.5,
		pos="1825.9,2787",
		width=3.0032];
	ScaleRowUp2_Linear_Any_C -> ScaleRowUp2_Linear_C	 [color=purple,
		pos="e,1717.5,2787 1641.9,2787 1663.6,2787 1686,2787 1707.4,2787"];
	ScaleRowUp2_Linear_C -> __assert_func	 [color=purple,
		pos="e,2052.7,2769 1923.9,2779.2 1962.6,2776.1 2006.4,2772.6 2042.3,2769.8"];
	ScaleRowDown38_C -> __assert_func	 [color=purple,
		pos="e,2112.8,2745.9 1849.6,2138.4 1878.7,2161.1 1927.7,2203.2 1956.1,2250 2057.6,2417.4 2099.5,2655.2 2111.4,2736"];
	ScaleRowDown38_3_Box_C -> __assert_func	 [color=purple,
		pos="e,2113.4,2745.9 1181.4,2025.4 1236,2021 1303.6,2016.2 1364.1,2014 1629.4,2004.4 1771.2,1903.4 1956.1,2094 2048.2,2189 2100,2620.7 \
2112.3,2735.7"];
	ScaleAddRow_C -> __assert_func	 [color=purple,
		pos="e,2114.5,2745.8 1149.2,1975.1 1350.1,1959.8 1894.4,1923.6 1956.1,1974 2077.5,2073.5 2108.3,2605.8 2114.1,2735.5"];
	FixedDiv1_C -> __divdi3	 [color=purple,
		pos="e,1782,2653.9 1129.8,2377.8 1186.4,2371.5 1273.9,2371.6 1328.1,2419 1374.9,2459.9 1319,2511.4 1364.1,2554 1477.1,2660.7 1676.5,2661.4 \
1772,2654.6"];
	ScaleRowDown34_0_Box_C -> __assert_func	 [color=purple,
		pos="e,2114.6,2745.9 1167.5,1914.8 1369,1890.4 1839.2,1845.7 1956.1,1944 2081,2049.1 2109.3,2603.7 2114.2,2735.8"];
	sscanf	 [height=0.5,
		pos="663.05,180",
		width=0.97679];
	_ZL29ExtractResolutionFromFilenamePKcPiS1_ -> sscanf	 [color=purple,
		pos="e,627.82,180 503.95,180 546.86,180 588.07,180 617.8,180"];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE	 [height=0.5,
		pos="1075.2,3512",
		width=7.0273];
	ARGBScaleClip -> _ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE	 [color=blue,
		pos="e,821.98,3512 738.64,3512 760.38,3512 785.41,3512 811.8,3512"];
	ScaleARGB	 [height=0.5,
		pos="1075.2,3593",
		width=1.6325];
	ARGBScaleClip -> ScaleARGB	 [color=red,
		pos="e,1025.5,3583.2 721.66,3523.5 799.61,3538.8 936.66,3565.8 1015.3,3581.2"];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleSlope	 [color=blue,
		pos="e,1485.7,2542.9 1102.9,3493.9 1157.7,3456.4 1278.4,3364.3 1328.1,3252 1380.8,3133.1 1309.3,2785.9 1364.1,2668 1388.5,2615.7 1441.6,\
2572.9 1477.1,2548.7"];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> malloc	 [color=blue,
		pos="e,1475.6,2890.6 1102.1,3494 1155.8,3456.3 1275.7,3363.4 1328.1,3252 1359.6,3185.3 1313.9,2976 1364.1,2922 1389.4,2894.9 1432.2,2889.5 \
1465.2,2890.2"];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> __assert_func	 [color=blue,
		pos="e,2111.4,2782.2 1088.6,3494 1126,3445.5 1236.6,3312.3 1364.1,3258 1485.6,3206.3 1851.4,3288.5 1956.1,3208 2025.4,3154.7 2089.8,2881.3 \
2109.2,2792.2"];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> InterpolateRow_C	 [color=blue,
		pos="e,1748.1,3317.1 1098.6,3493.9 1145.7,3458.6 1256.8,3381.4 1364.1,3350 1490.2,3313.1 1643.6,3312.3 1738.1,3316.6"];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleFilterReduce	 [color=blue,
		pos="e,1443.3,3386.9 1116,3494.1 1171.3,3470.5 1273.5,3429 1364.1,3404 1386.4,3397.9 1410.9,3392.7 1433.5,3388.7"];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScalePlaneVertical	 [color=blue,
		pos="e,1440.7,3294.8 1095.6,3494 1140.8,3455.4 1253.7,3364.2 1364.1,3317 1385,3308.1 1408.6,3301.6 1430.7,3296.8"];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> free	 [color=blue,
		pos="e,1496.1,2963.7 1099.3,3494 1149.6,3455.4 1265.7,3359.2 1328.1,3252 1357,3202.4 1337.3,3178.7 1364.1,3128 1397.8,3064.3 1456.5,3002.3 \
1488.9,2970.7"];
	ScaleARGBRowDown2_C	 [height=0.5,
		pos="1512,3539",
		width=3.2419];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDown2_C	 [color=blue,
		pos="e,1403.4,3532.3 1266.4,3523.8 1309.5,3526.5 1354,3529.2 1393.1,3531.7"];
	ScaleARGBRowDownEvenBox_C	 [height=0.5,
		pos="1512,3485",
		width=4.1061];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDownEvenBox_C	 [color=blue,
		pos="e,1379.9,3493.2 1266.4,3500.2 1301.2,3498 1336.8,3495.8 1369.8,3493.8"];
	ScaleARGBRowDown2Box_C	 [height=0.5,
		pos="1512,3431",
		width=3.689];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDown2Box_C	 [color=blue,
		pos="e,1432.6,3445.4 1165,3495.1 1222,3484.4 1297.4,3470.3 1364.1,3458 1383,3454.5 1403.3,3450.8 1422.6,3447.3"];
	ScaleARGBCols64_C	 [height=0.5,
		pos="1512,3971",
		width=2.7057];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBCols64_C	 [color=blue,
		pos="e,1414.2,3971.1 1264,3524 1288.4,3533.1 1310.8,3546.6 1328.1,3566 1384.3,3629 1307.1,3881.8 1364.1,3944 1375,3955.9 1389.3,3963.6 \
1404.6,3968.4"];
	ScaleARGBColsUp2_C	 [height=0.5,
		pos="1512,3863",
		width=2.8994];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBColsUp2_C	 [color=blue,
		pos="e,1408.2,3861.1 1262.1,3524.2 1287,3533.2 1310.2,3546.5 1328.1,3566 1410.4,3654.9 1280.6,3748.4 1364.1,3836 1373.7,3846 1385.7,3853.1 \
1398.6,3857.9"];
	ScaleARGBFilterCols64_C	 [height=0.5,
		pos="1512,3809",
		width=3.2868];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBFilterCols64_C	 [color=blue,
		pos="e,1398.8,3803.6 1260.5,3524.3 1285.9,3533.3 1309.6,3546.6 1328.1,3566 1395.4,3636.4 1295.9,3712.6 1364.1,3782 1371.5,3789.5 1380.2,\
3795.3 1389.6,3799.7"];
	ScaleARGBRowDownEven_C	 [height=0.5,
		pos="1512,3755",
		width=3.659];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDownEven_C	 [color=blue,
		pos="e,1393.8,3747 1257.7,3524.6 1283.9,3533.4 1308.6,3546.6 1328.1,3566 1380.5,3617.9 1311,3676.8 1364.1,3728 1370.2,3733.8 1377,3738.6 \
1384.3,3742.5"];
	ScaleARGBFilterCols_C	 [height=0.5,
		pos="1512,3701",
		width=3.0186];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBFilterCols_C	 [color=blue,
		pos="e,1407,3696.3 1251.5,3524.9 1279.6,3533.6 1306.5,3546.6 1328.1,3566 1365.9,3599.7 1325.9,3640.8 1364.1,3674 1373.8,3682.4 1385.1,\
3688.5 1397.2,3693"];
	ARGBCopy	 [height=0.5,
		pos="1512,3917",
		width=1.6329];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ARGBCopy	 [color=blue,
		pos="e,1455.1,3921.8 1263.4,3524.2 1287.9,3533.2 1310.6,3546.6 1328.1,3566 1425.4,3673.4 1265.3,3784 1364.1,3890 1384.5,3911.8 1416.2,\
3919.6 1445.1,3921.4"];
	ScaleARGBCols_C	 [height=0.5,
		pos="1512,3647",
		width=2.4375];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBCols_C	 [color=blue,
		pos="e,1426.2,3643.1 1232.6,3526.1 1266.1,3534.3 1299.9,3546.8 1328.1,3566 1352,3582.2 1340,3604.2 1364.1,3620 1379.7,3630.2 1398,3636.8 \
1416.4,3641.1"];
	ScaleARGBRowDown2Linear_C	 [height=0.5,
		pos="1512,3593",
		width=3.9419];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDown2Linear_C	 [color=blue,
		pos="e,1430.6,3578.2 1165,3528.9 1222,3539.6 1297.4,3553.7 1364.1,3566 1382.4,3569.4 1402,3573 1420.6,3576.4"];
	_ZN6libyuvL9SumPixelsEiPKt	 [height=0.5,
		pos="1512,1809",
		width=3.7193];
	_ZN6libyuvL15ScaleAddCols1_CEiiiiPKtPh -> _ZN6libyuvL9SumPixelsEiPKt	 [color=blue,
		pos="e,1424,1795.3 1246,1734.3 1273.9,1738.6 1302.2,1744.9 1328.1,1754 1346.1,1760.3 1346.6,1769.8 1364.1,1777 1379.9,1783.5 1397.1,1788.7 \
1414.1,1793"];
	_ZN6libyuvL9SumPixelsEiPKt -> __assert_func	 [color=blue,
		pos="e,2113.5,2745.8 1617.3,1797.9 1732.6,1788.2 1907.5,1781.5 1956.1,1824 2027.2,1886.2 2098,2585 2112.5,2735.5"];
	ARGBUnattenuate -> OUTLINED_FUNCTION_2	 [color=blue,
		pos="e,1702.6,981 1596.5,981 1626.1,981 1660,981 1692.5,981"];
	ARGBUnattenuate -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1746,1021.3 1577.8,992.32 1623.7,1000.2 1685.6,1010.9 1736.1,1019.5"];
	ARGBUnattenuate -> OUTLINED_FUNCTION_0	 [color=blue,
		pos="e,1730,884.43 1591.3,974.61 1614.7,969.97 1639.5,962.14 1659.8,949 1682.5,934.3 1673.1,914.6 1695.8,900 1703.4,895.1 1711.8,891.07 \
1720.4,887.76"];
	ARGBUnattenuateRow_C	 [height=0.5,
		pos="1825.9,819",
		width=3.1673];
	ARGBUnattenuate -> ARGBUnattenuateRow_C	 [color=blue,
		pos="e,1741,831.13 1530.3,963.2 1561.6,933.96 1628.3,876.04 1695.8,846 1706.9,841.04 1719,836.97 1731.2,833.65"];
	ARGBToI420 -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1728.5,1046 1111.7,1290 1166.1,1267.9 1272,1226.1 1364.1,1197 1493.6,1156.1 1550.5,1200.5 1659.8,1120 1684.2,1102 1670.9,1079.4 \
1695.8,1062 1702.9,1057 1710.8,1052.9 1719,1049.5"];
	ARGBToI420 -> OUTLINED_FUNCTION_4	 [color=blue,
		pos="e,1992.8,3371.2 1129.1,1294.5 1187.6,1286.6 1279.3,1285.1 1328.1,1340 1388.6,1407.9 1315.9,2898.9 1364.1,2976 1442.5,3101.3 1572.9,\
3008.5 1659.8,3128 1718.5,3208.9 1621.1,3283.5 1695.8,3350 1717,3368.9 1867.7,3371.8 1982.5,3371.2"];
	ARGBToYRow_C	 [height=0.5,
		pos="1512,1224",
		width=2.363];
	ARGBToI420 -> ARGBToYRow_C	 [color=blue,
		pos="e,1447.7,1235.9 1130,1294.8 1207.8,1280.4 1350.4,1254 1437.7,1237.8"];
	ARGBToUVRow_C	 [height=0.5,
		pos="1512,1521",
		width=2.5566];
	ARGBToI420 -> ARGBToUVRow_C	 [color=blue,
		pos="e,1500,1503.1 1141.1,1303 1194.2,1303.9 1269.4,1311.1 1328.1,1340 1402.1,1376.4 1464.7,1454 1494.1,1494.7"];
	OUTLINED_FUNCTION_11	 [height=0.5,
		pos="1512,1711",
		width=3.5544];
	ARGBToI420 -> OUTLINED_FUNCTION_11	 [color=blue,
		pos="e,1489.1,1693.2 1131.6,1295.5 1188.9,1289.3 1276.5,1290.1 1328.1,1340 1395.6,1405.2 1323,1463.7 1364.1,1548 1392.2,1605.5 1446.9,\
1657.6 1481.3,1686.7"];
	ARGBToI420 -> OUTLINED_FUNCTION_12	 [color=blue,
		pos="e,1697.9,1305 1141.5,1305 1263.4,1305 1525.7,1305 1687.9,1305"];
	_ZN6libyuvL6RGBToYEhhh	 [height=0.5,
		pos="1825.9,1251",
		width=3.5253];
	ARGBToYRow_C -> _ZN6libyuvL6RGBToYEhhh	 [color=blue,
		pos="e,1717.1,1241.6 1590.8,1230.8 1625.9,1233.8 1668,1237.4 1706.8,1240.8"];
	OUTLINED_FUNCTION_22	 [height=0.5,
		pos="1825.9,1197",
		width=3.5544];
	ARGBToYRow_C -> OUTLINED_FUNCTION_22	 [color=blue,
		pos="e,1716.5,1206.4 1590.8,1217.2 1625.7,1214.2 1667.6,1210.6 1706.2,1207.3"];
	ARGBToYRow_C -> OUTLINED_FUNCTION_12	 [color=blue,
		pos="e,1750.3,1290.4 1559.3,1239.1 1596.2,1250.5 1649,1266.3 1695.8,1278 1710.1,1281.6 1725.3,1285 1740.1,1288.2"];
	OUTLINED_FUNCTION_30	 [height=0.5,
		pos="1825.9,1143",
		width=3.5544];
	ARGBToYRow_C -> OUTLINED_FUNCTION_30	 [color=blue,
		pos="e,1750.3,1157.6 1559.3,1208.9 1596.2,1197.5 1649,1181.7 1695.8,1170 1710.1,1166.4 1725.3,1163 1740.1,1159.8"];
	RGBToY	 [height=0.5,
		pos="1825.9,1089",
		width=1.3497];
	ARGBToYRow_C -> RGBToY	 [color=red,
		pos="e,1777.8,1091.5 1559.4,1208.9 1589.9,1197.8 1629.4,1180.7 1659.8,1158 1679.5,1143.3 1674.6,1128.5 1695.8,1116 1717.4,1103.2 1744.2,\
1096.4 1767.9,1092.8"];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_2	 [color=blue,
		pos="e,1720.7,990.55 1524.8,1503.1 1554,1461.2 1625.6,1352.8 1659.8,1251 1694.5,1147.5 1620.8,1087.4 1695.8,1008 1700.5,1003 1705.9,998.77 \
1711.8,995.24"];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_9	 [color=blue,
		pos="e,1797.6,1833.4 1530.7,1538.9 1560.3,1567.7 1618.7,1627 1659.8,1684 1678.9,1710.5 1674.6,1723.2 1695.8,1748 1723,1779.9 1761.3,1808.8 \
1789.3,1827.8"];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_18	 [color=blue,
		pos="e,1787.1,1703.7 1533.5,1538.7 1567,1565.8 1634.1,1618.3 1695.8,1656 1722.1,1672.1 1752.8,1687.6 1777.8,1699.4"];
	_ZN6libyuvL8RGB2xToVEttt	 [height=0.5,
		pos="1825.9,1467",
		width=3.6148];
	ARGBToUVRow_C -> _ZN6libyuvL8RGB2xToVEttt	 [color=blue,
		pos="e,1744.3,1481 1581.3,1509.1 1626.3,1501.3 1685.5,1491.2 1734.4,1482.7"];
	_ZN6libyuvL8RGB2xToUEttt	 [height=0.5,
		pos="1825.9,1413",
		width=3.6148];
	ARGBToUVRow_C -> _ZN6libyuvL8RGB2xToUEttt	 [color=blue,
		pos="e,1728.3,1425 1596.3,1513.6 1618.2,1508.8 1641,1501.2 1659.8,1489 1682.5,1474.3 1673.1,1454.6 1695.8,1440 1702.9,1435.4 1710.7,1431.6 \
1718.7,1428.4"];
	OUTLINED_FUNCTION_27	 [height=0.5,
		pos="1825.9,1359",
		width=3.5544];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_27	 [color=blue,
		pos="e,1722.7,1369.7 1601.3,1516.6 1622.4,1511.8 1643.6,1503.3 1659.8,1489 1696.1,1456.9 1659.3,1418 1695.8,1386 1701.1,1381.4 1707,1377.4 \
1713.3,1374.1"];
	OUTLINED_FUNCTION_37	 [height=0.5,
		pos="1825.9,1629",
		width=3.5544];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_37	 [color=blue,
		pos="e,1745.1,1615 1544.7,1537.9 1580.8,1556.1 1641.2,1584.5 1695.8,1602 1708.3,1606 1721.7,1609.6 1735,1612.7"];
	RGB2xToU	 [height=0.5,
		pos="1825.9,1575",
		width=1.6179];
	ARGBToUVRow_C -> RGB2xToU	 [color=red,
		pos="e,1774.8,1566.2 1581.3,1532.9 1636.2,1542.4 1712.3,1555.5 1765,1564.5"];
	RGB2xToV	 [height=0.5,
		pos="1825.9,1521",
		width=1.6179];
	ARGBToUVRow_C -> RGB2xToV	 [color=red,
		pos="e,1767.5,1521 1604,1521 1653.1,1521 1712.3,1521 1757.3,1521"];
	_ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh -> __assert_func	 [color=blue,
		pos="e,2113.6,2745.9 1257.9,1676.9 1282.3,1681.8 1306.4,1689.2 1328.1,1700 1349,1710.3 1343.2,1728 1364.1,1738 1423.7,1766.5 1907.6,1741.3 \
1956.1,1786 2028.4,1852.8 2098.7,2582.7 2112.7,2735.9"];
	_ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh -> _ZN6libyuvL9SumPixelsEiPKt	 [color=blue,
		pos="e,1404.5,1798.1 1260.3,1670.4 1284.6,1676.3 1308,1685.6 1328.1,1700 1358.9,1721.9 1334.6,1753.4 1364.1,1777 1373.4,1784.4 1383.9,\
1790.1 1395,1794.6"];
	_ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh -> OUTLINED_FUNCTION_11	 [color=blue,
		pos="e,1403,1701.5 1214,1685.1 1271.5,1690.1 1337.5,1695.8 1392.8,1700.6"];
	ARGBCopy -> CopyPlane	 [color=blue,
		pos="e,1812.8,4081.4 1570.2,3920 1598.4,3923.3 1632.2,3930.1 1659.8,3944 1722.6,3975.6 1778.5,4038.3 1806.6,4073.5"];
	clamp255	 [height=0.5,
		pos="2115.2,819",
		width=1.3644];
	ARGBUnattenuateRow_C -> clamp255	 [color=red,
		pos="e,2065.7,819 1940.2,819 1979.7,819 2022.4,819 2055.7,819"];
	ScaleAddCols2_C -> __assert_func	 [color=red,
		pos="e,2111.1,2782 1157.3,3223.4 1369.8,3219 1924,3205.2 1956.1,3182 2022.9,3133.5 2088.5,2877.2 2108.8,2791.7"];
	ScaleARGB -> ScaleSlope	 [color=red,
		pos="e,1485.5,2542.9 1130.8,3598.9 1189.6,3601.7 1280.5,3595.5 1328.1,3539 1390.6,3465 1324.2,2756.2 1364.1,2668 1387.9,2615.4 1441.2,\
2572.7 1476.9,2548.6"];
	ScaleARGB -> malloc	 [color=red,
		pos="e,1475.9,2890.3 1131.1,3598.7 1189.8,3601.3 1280.2,3594.9 1328.1,3539 1417.6,3434.8 1273.2,3024.9 1364.1,2922 1389,2893.9 1432.5,\
2888.9 1465.9,2889.8"];
	ScaleARGB -> __assert_func	 [color=red,
		pos="e,2111.7,2782.2 1080.5,3611.2 1101.9,3680.8 1189.4,3931.7 1364.1,4025 1480,4086.9 1549.8,4096.9 1659.8,4025 1885.5,3877.6 2075.6,\
2964.4 2109.7,2792.1"];
	ScaleARGB -> InterpolateRow_C	 [color=red,
		pos="e,1824.4,3341.1 1081.1,3611 1104.5,3677.6 1196.4,3911.6 1364.1,3998 1422.6,4028.1 1608.1,4038.5 1659.8,3998 1765.3,3915.3 1812.8,\
3468.2 1823.5,3351.1"];
	ScaleARGB -> ScaleFilterReduce	 [color=red,
		pos="e,1430.2,3375.9 1132.7,3596.8 1189.7,3597.3 1275.9,3588.7 1328.1,3539 1373.1,3496.2 1318.5,3446.1 1364.1,3404 1379.5,3389.9 1399.6,\
3381.9 1420.1,3377.7"];
	ScaleARGB -> ScalePlaneVertical	 [color=red,
		pos="e,1451.1,3297.6 1132.1,3597.5 1189.8,3598.8 1277.4,3590.9 1328.1,3539 1387.9,3477.9 1310.9,3416.9 1364.1,3350 1383.4,3325.9 1413.4,\
3310.5 1441.3,3300.8"];
	ScaleARGB -> free	 [color=red,
		pos="e,1494.9,2963.1 1131.3,3598.5 1189.8,3600.8 1279.5,3594 1328.1,3539 1388.9,3470.3 1329.4,3212.8 1364.1,3128 1391.4,3061.4 1452.6,\
3000.5 1487.1,2969.9"];
	ScaleARGB -> ScaleARGBRowDown2_C	 [color=red,
		pos="e,1420.8,3550.3 1130,3586.2 1200.3,3577.5 1323.4,3562.3 1410.9,3551.5"];
	ScaleARGB -> ScaleARGBRowDownEvenBox_C	 [color=red,
		pos="e,1407.6,3497.8 1131.9,3588 1184.6,3581.7 1264.5,3568 1328.1,3539 1346.4,3530.7 1345.8,3520 1364.1,3512 1374.8,3507.3 1386.2,3503.5 \
1397.8,3500.3"];
	ScaleARGB -> ScaleARGBRowDown2Box_C	 [color=red,
		pos="e,1397.3,3440.2 1133.8,3595 1189.6,3593.8 1273,3583.7 1328.1,3539 1358.7,3514.2 1333.2,3482.4 1364.1,3458 1371.4,3452.3 1379.4,3447.7 \
1387.9,3443.9"];
	ScaleARGB -> ScaleARGBCols64_C	 [color=red,
		pos="e,1420.8,3964.6 1084,3610.9 1113.9,3669.8 1218.2,3858.2 1364.1,3944 1378.3,3952.3 1394.4,3958.2 1410.7,3962.3"];
	ScaleARGB -> ScaleARGBColsUp2_C	 [color=red,
		pos="e,1420.9,3854 1089.9,3610.6 1129.3,3656.2 1242,3778.5 1364.1,3836 1378.7,3842.9 1394.8,3848 1410.9,3851.8"];
	ScaleARGB -> ScaleARGBFilterCols64_C	 [color=red,
		pos="e,1418.9,3797.8 1095,3610.1 1139.6,3647.6 1253.1,3737.6 1364.1,3782 1378.3,3787.6 1393.6,3792.1 1408.9,3795.6"];
	ScaleARGB -> ScaleARGBRowDownEven_C	 [color=red,
		pos="e,1420.4,3742.1 1102.9,3608.9 1153.3,3637.1 1263.9,3696 1364.1,3728 1378.8,3732.7 1394.6,3736.6 1410.2,3740"];
	ScaleARGB -> ScaleARGBFilterCols_C	 [color=red,
		pos="e,1434.6,3688.3 1116.5,3605.9 1172.3,3623 1275.1,3653.4 1364.1,3674 1383.6,3678.5 1404.7,3682.7 1424.6,3686.4"];
	ScaleARGB -> ARGBCopy	 [color=red,
		pos="e,1453.5,3914.6 1086.4,3610.7 1120.7,3663.1 1230.2,3818.6 1364.1,3890 1388.2,3902.8 1417.3,3909.7 1443.3,3913.3"];
	ScaleARGB -> ScaleARGBCols_C	 [color=red,
		pos="e,1436.5,3637.7 1130,3599.8 1204.6,3609 1338.7,3625.6 1426.5,3636.4"];
	ScaleARGB -> ScaleARGBRowDown2Linear_C	 [color=red,
		pos="e,1370.1,3593 1134.1,3593 1191.7,3593 1281.8,3593 1359.7,3593"];
}

```

修剪路徑後
```graphviz
digraph {
	graph [bb="0,0,2092.5,2667.5",
		rankdir=LR
	];
	node [label="\N"];
	main	 [height=0.5,
		pos="30.348,689",
		width=0.84299];
	ARGBScaleClip	 [height=0.5,
		pos="251.46,2076",
		width=2.0947];
	main -> ARGBScaleClip	 [color=blue,
		pos="e,248.58,2057.9 33.224,707.04 56.788,854.85 217.89,1865.4 246.97,2047.8"];
	I420Scale	 [height=0.5,
		pos="251.46,811",
		width=1.3791];
	main -> I420Scale	 [color=blue,
		pos="e,216.76,798.09 47.255,704.11 60.192,715.2 78.796,730.15 96.695,741 132.24,762.54 175.55,781.57 207.3,794.34"];
	ARGBUnattenuate	 [height=0.5,
		pos="1528.1,789",
		width=2.3476];
	main -> ARGBUnattenuate	 [color=blue,
		pos="e,1444,786.92 56.475,698.44 68.554,702.4 83.188,706.62 96.695,709 354.89,754.47 1157.5,779.28 1433.6,786.64"];
	ARGBAttenuate	 [height=0.5,
		pos="1528.1,735",
		width=2.0944];
	main -> ARGBAttenuate	 [color=blue,
		pos="e,1453.5,731.89 60.855,689.67 176.6,692.23 599.68,701.83 948.19,713 1124.2,718.64 1330.2,726.83 1443.2,731.47"];
	ARGBToI420	 [height=0.5,
		pos="1171.2,590",
		width=1.8413];
	main -> ARGBToI420	 [color=blue,
		pos="e,1104.8,589.13 41.424,671.9 53.011,655.71 72.824,632.38 96.695,622 187.35,582.59 863.92,586.5 1094.5,589.01"];
	OUTLINED_FUNCTION_0	 [height=0.5,
		pos="1828.1,774",
		width=3.4202];
	main -> OUTLINED_FUNCTION_0	 [color=blue,
		pos="e,1735.2,762.16 60.73,687.89 72.022,687.53 84.942,687.18 96.695,687 234.25,684.93 268.66,685.98 406.23,687 685.32,689.06 1407.3,\
593.74 1662,708 1683.5,717.66 1677.5,735.38 1698,747 1706.6,751.86 1715.9,755.85 1725.5,759.12"];
	__cxa_throw_bad_array_new_length	 [height=0.5,
		pos="251.46,552",
		width=4.299];
	main -> __cxa_throw_bad_array_new_length	 [color=red,
		pos="e,138,564.32 36.594,670.98 45.834,647.13 65.492,605.6 96.695,584 106.39,577.29 117.19,571.93 128.45,567.66"];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE	 [height=0.5,
		pos="695.21,2157",
		width=7.0273];
	ARGBScaleClip -> _ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE	 [color=blue,
		pos="e,602.99,2140.2 311.77,2087 383.99,2100.2 506.08,2122.5 593.09,2138.4"];
	ScaleARGB	 [height=0.5,
		pos="695.21,2076",
		width=1.6325];
	ARGBScaleClip -> ScaleARGB	 [color=red,
		pos="e,636.34,2076 326.99,2076 410.86,2076 545.09,2076 626.23,2076"];
	ScaleARGBRowDown2_C	 [height=0.5,
		pos="1171.2,1941",
		width=3.2419];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDown2_C	 [color=blue,
		pos="e,1057.8,1936.6 875.13,2144.3 902.16,2135.6 927.77,2122.4 948.19,2103 993.19,2060.2 937.79,2009.3 984.19,1968 1001.9,1952.3 1024.5,\
1943.3 1047.8,1938.4"];
	__assert_func	 [height=0.5,
		pos="1828.1,1699",
		width=1.7962];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> __assert_func	 [color=blue,
		pos="e,1803,1715.6 700.43,2175.4 721.59,2245.8 808.34,2499.5 984.19,2594 1130.6,2672.7 1237.6,2708.4 1358.2,2594 1413.5,2541.5 1348.7,\
1970.2 1394.2,1909 1469.7,1807.6 1550.1,1871.9 1662,1813 1679.4,1803.8 1681.8,1798.3 1698,1787 1730.5,1764.3 1768.1,1738.9 1794.5,\
1721.3"];
	ScaleARGBRowDownEvenBox_C	 [height=0.5,
		pos="1171.2,1887",
		width=4.1061];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDownEvenBox_C	 [color=blue,
		pos="e,1024.9,1889.6 879.24,2144.6 905.04,2135.7 929.19,2122.4 948.19,2103 1008,2041.9 922.39,1973.1 984.19,1914 993.36,1905.2 1004,1898.5 \
1015.5,1893.4"];
	ScaleSlope	 [height=0.5,
		pos="1528.1,1314",
		width=1.4985];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleSlope	 [color=blue,
		pos="e,1481.9,1323.5 886.02,2145.1 909.81,2135.9 931.57,2122.5 948.19,2103 1046.6,1987.7 880.1,1532.1 984.19,1422 1041.6,1361.2 1280.4,\
1411.7 1358.2,1381 1376.8,1373.6 1376.3,1363 1394.2,1354 1418.6,1341.7 1447.4,1332.5 1472,1326"];
	ScalePlaneVertical	 [height=0.5,
		pos="1171.2,1779",
		width=2.3472];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScalePlaneVertical	 [color=blue,
		pos="e,1097.9,1770 882.95,2144.8 907.63,2135.7 930.47,2122.4 948.19,2103 1037.9,2004.9 891.25,1901.1 984.19,1806 1010.6,1779 1051.1,1770.8 \
1087.7,1770"];
	ScaleARGBRowDown2Box_C	 [height=0.5,
		pos="1171.2,2481",
		width=3.689];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDown2Box_C	 [color=blue,
		pos="e,1046.5,2474.6 706.56,2175.3 740.84,2228.8 849.26,2385.2 984.19,2454 1000.4,2462.3 1018.4,2468.2 1036.6,2472.5"];
	malloc	 [height=0.5,
		pos="1171.2,2427",
		width=1.0366];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> malloc	 [color=blue,
		pos="e,1133.7,2427.5 710.16,2175.2 749.48,2221.7 861.26,2344.9 984.19,2400 1028.7,2419.9 1084.6,2425.8 1123.6,2427.3"];
	InterpolateRow_C	 [height=0.5,
		pos="1528.1,1768",
		width=2.2881];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> InterpolateRow_C	 [color=blue,
		pos="e,1474.7,1781.8 701.35,2175.4 724.93,2242.7 816.78,2475.8 984.19,2562 1058.1,2600 1298,2619.3 1358.2,2562 1416.5,2506.5 1350.8,1905.8 \
1394.2,1838 1410.3,1812.8 1438.6,1796.2 1465.1,1785.5"];
	ScaleARGBCols64_C	 [height=0.5,
		pos="1171.2,2373",
		width=2.7057];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBCols64_C	 [color=blue,
		pos="e,1077.9,2367.6 715.55,2175 760.44,2213.5 872.88,2303.9 984.19,2346 1010.4,2355.9 1040,2362.2 1067.7,2366.2"];
	ScaleARGBColsUp2_C	 [height=0.5,
		pos="1171.2,2319",
		width=2.8994];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBColsUp2_C	 [color=blue,
		pos="e,1077.3,2310.9 725.66,2174.9 777.09,2204.3 885.24,2262.4 984.19,2292 1010.6,2299.9 1039.9,2305.5 1067.3,2309.5"];
	ScaleARGBFilterCols64_C	 [height=0.5,
		pos="1171.2,2265",
		width=3.2868];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBFilterCols64_C	 [color=blue,
		pos="e,1077.6,2253.9 749.81,2174.6 807.53,2192.7 901.48,2220.5 984.19,2238 1011.1,2243.7 1040.4,2248.5 1067.6,2252.5"];
	ScaleARGBRowDownEven_C	 [height=0.5,
		pos="1171.2,2211",
		width=3.659];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDownEven_C	 [color=blue,
		pos="e,1069.5,2199.5 829.7,2172.3 902.28,2180.5 990.81,2190.5 1059.5,2198.3"];
	ScaleARGBFilterCols_C	 [height=0.5,
		pos="1171.2,2157",
		width=3.0186];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBFilterCols_C	 [color=blue,
		pos="e,1062.4,2157 948.53,2157 984.69,2157 1020.4,2157 1052.2,2157"];
	ARGBCopy	 [height=0.5,
		pos="1171.2,1833",
		width=1.6329];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ARGBCopy	 [color=blue,
		pos="e,1118.2,1825.1 881.54,2144.7 906.65,2135.7 929.98,2122.4 948.19,2103 1022.9,2023.4 906.85,1937.1 984.19,1860 1016,1828.3 1067.3,\
1822.8 1108.1,1824.5"];
	ScaleARGBCols_C	 [height=0.5,
		pos="1171.2,2103",
		width=2.4375];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBCols_C	 [color=blue,
		pos="e,1094.2,2111.7 829.7,2141.7 911.19,2132.5 1012.8,2121 1083.9,2112.9"];
	free	 [height=0.5,
		pos="1171.2,2049",
		width=0.75];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> free	 [color=blue,
		pos="e,1144.1,2048.8 820.54,2141.3 862.38,2133.2 908.44,2121.1 948.19,2103 966.4,2094.7 965.72,2083.7 984.19,2076 1033.2,2055.7 1095,\
2050.2 1133.8,2049"];
	ScaleFilterReduce	 [height=0.5,
		pos="1171.2,1995",
		width=2.273];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleFilterReduce	 [color=blue,
		pos="e,1092.7,1989.7 865.42,2143.6 895.29,2135.2 924.39,2122.3 948.19,2103 978.79,2078.2 952.78,2045.8 984.19,2022 1011.9,2001 1048.8,\
1992.8 1082.4,1990.3"];
	ScaleARGBRowDown2Linear_C	 [height=0.5,
		pos="1171.2,2535",
		width=3.9419];
	_ZN6libyuvL9ScaleARGBEPKhiiiPhiiiiiiiNS_10FilterModeE -> ScaleARGBRowDown2Linear_C	 [color=blue,
		pos="e,1038.9,2528.4 703.9,2175.1 733.47,2234.6 836.65,2424.9 984.19,2508 998.04,2515.8 1013.3,2521.6 1029.1,2525.9"];
	ScalePlane	 [height=0.5,
		pos="695.21,1184",
		width=1.4834];
	I420Scale -> ScalePlane	 [color=blue,
		pos="e,675.08,1167.1 271.39,827.75 342.63,887.63 584.82,1091.2 667.38,1160.6"];
	OUTLINED_FUNCTION_5	 [height=0.5,
		pos="1828.1,882",
		width=3.4202];
	I420Scale -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1705.8,879.83 296.4,818.77 334.96,825.1 392.07,833.67 442.23,838 682.81,858.78 1397.5,874.01 1695.4,879.63"];
	OUTLINED_FUNCTION_18	 [height=0.5,
		pos="1828.1,342",
		width=3.5544];
	I420Scale -> OUTLINED_FUNCTION_18	 [color=blue,
		pos="e,1738.4,354.89 281.46,796.56 379.93,749.67 703.11,599.82 984.19,515 1247.8,435.47 1568.7,380.86 1728.1,356.46"];
	OUTLINED_FUNCTION_1	 [height=0.5,
		pos="695.21,811",
		width=3.4202];
	I420Scale -> OUTLINED_FUNCTION_1	 [color=blue,
		pos="e,571.63,811 301.5,811 364.14,811 473.86,811 561.58,811"];
	_ZN6libyuvL15ScaleAddCols1_CEiiiiPKtPh	 [height=0.5,
		pos="1171.2,1503",
		width=5.1945];
	ScalePlane -> _ZN6libyuvL15ScaleAddCols1_CEiiiiPKtPh	 [color=blue,
		pos="e,1025.9,1491.6 706.4,1201.6 740.63,1253.8 849.81,1408.2 984.19,1476 994.27,1481.1 1005,1485.3 1016.1,1488.8"];
	ScalePlaneBilinearUp	 [height=0.5,
		pos="1171.2,1611",
		width=2.6753];
	ScalePlane -> ScalePlaneBilinearUp	 [color=blue,
		pos="e,1074.9,1611.7 702.03,1201.9 727.65,1266.2 824.78,1487.5 984.19,1584 1008.2,1598.5 1037,1606.4 1064.8,1610.3"];
	ScalePlane -> ScaleSlope	 [color=blue,
		pos="e,1524.1,1295.8 716.02,1167.3 761.39,1131.9 874.01,1050.8 984.19,1022 1064.6,1001 1286.1,980.56 1358.2,1022 1459.6,1080.3 1506.1,\
1225 1521.7,1286.1"];
	ScalePlane -> ScalePlaneVertical	 [color=blue,
		pos="e,1131.2,1763.1 701.98,1202.1 728.44,1270.9 831.05,1519.7 984.19,1671 1024.1,1710.5 1081.4,1740.7 1122,1759.1"];
	OUTLINED_FUNCTION_20	 [height=0.5,
		pos="1171.2,1049",
		width=3.5544];
	ScalePlane -> OUTLINED_FUNCTION_20	 [color=blue,
		pos="e,1068.5,1059.8 727.41,1169.4 780.03,1146 888.2,1100.6 984.19,1076 1007.9,1069.9 1033.7,1065.1 1058.4,1061.3"];
	ScalePlaneBilinearDown	 [height=0.5,
		pos="1171.2,1557",
		width=3.0031];
	ScalePlane -> ScalePlaneBilinearDown	 [color=blue,
		pos="e,1063.5,1554.9 703.97,1201.9 733.78,1260.6 837.61,1448.2 984.19,1530 1005.2,1541.7 1029.5,1549 1053.6,1553.3"];
	OUTLINED_FUNCTION_9	 [height=0.5,
		pos="1828.1,396",
		width=3.4202];
	ScalePlane -> OUTLINED_FUNCTION_9	 [color=blue,
		pos="e,1728.3,406.67 712.83,1166.9 760.24,1119.6 890.81,981.35 948.19,838 971.1,780.78 939.9,605.85 984.19,563 1093,457.78 1537.7,583.39 \
1662,497 1692,476.12 1669.1,445.46 1698,423 1704.3,418.07 1711.3,413.98 1718.7,410.59"];
	OUTLINED_FUNCTION_16	 [height=0.5,
		pos="1171.2,903",
		width=3.5544];
	ScalePlane -> OUTLINED_FUNCTION_16	 [color=blue,
		pos="e,1052,909.73 708.84,1166.4 746.65,1118.9 858.34,988.06 984.19,930 1002.2,921.71 1022,915.83 1041.9,911.68"];
	_ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh	 [height=0.5,
		pos="1171.2,1449",
		width=5.1945];
	ScalePlane -> _ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh	 [color=blue,
		pos="e,1138.7,1431.2 722.66,1199.5 773.97,1228.4 887.91,1292.5 984.19,1346 1034.1,1373.7 1091.6,1405.3 1129.5,1426.2"];
	OUTLINED_FUNCTION_12	 [height=0.5,
		pos="1828.1,666",
		width=3.5544];
	ScalePlane -> OUTLINED_FUNCTION_12	 [color=blue,
		pos="e,1701.2,668.55 707.56,1166.2 744.16,1114.6 857.37,963.33 984.19,876 1146.4,764.31 1203,755.32 1394.2,708 1491.7,683.86 1604.8,673.46 \
1691,669.04"];
	ScalePlaneUp2_Linear	 [height=0.5,
		pos="1171.2,957",
		width=2.7794];
	ScalePlane -> ScalePlaneUp2_Linear	 [color=blue,
		pos="e,1080.1,964.72 714.19,1166.8 758.09,1128.2 871.57,1034.2 984.19,989 1011.1,978.19 1041.7,971.04 1070.2,966.29"];
	OUTLINED_FUNCTION_8	 [height=0.5,
		pos="1171.2,1319",
		width=3.4202];
	ScalePlane -> OUTLINED_FUNCTION_8	 [color=blue,
		pos="e,1070.5,1308.5 727.41,1198.6 780.03,1222 888.2,1267.4 984.19,1292 1008.6,1298.2 1035.2,1303.2 1060.5,1307"];
	OUTLINED_FUNCTION_13	 [height=0.5,
		pos="1171.2,1265",
		width=3.5544];
	ScalePlane -> OUTLINED_FUNCTION_13	 [color=blue,
		pos="e,1078.8,1252.4 741.15,1193.2 798.07,1204.4 898.09,1223.7 984.19,1238 1011.6,1242.5 1041.3,1247 1068.8,1251"];
	_ZN6libyuvL15ScaleAddCols0_CEiiiiPKtPh	 [height=0.5,
		pos="1171.2,1211",
		width=5.1945];
	ScalePlane -> _ZN6libyuvL15ScaleAddCols0_CEiiiiPKtPh	 [color=blue,
		pos="e,1010,1201.9 747.97,1187 808.5,1190.4 910.89,1196.2 999.8,1201.3"];
	ScaleAddCols2_C	 [height=0.5,
		pos="1528.1,1676",
		width=2.2884];
	ScalePlane -> ScaleAddCols2_C	 [color=red,
		pos="e,1446.9,1679.1 700.27,1202.2 721.09,1273.1 807.56,1532.9 984.19,1638 1058.2,1682.1 1301.9,1682.7 1436.6,1679.4"];
	ScaleAddCols0_C	 [height=0.5,
		pos="1171.2,1157",
		width=2.2884];
	ScalePlane -> ScaleAddCols0_C	 [color=red,
		pos="e,1091.3,1161.5 747.97,1181 828.38,1176.4 982.65,1167.7 1081.1,1162.1"];
	ScaleAddCols1_C	 [height=0.5,
		pos="1171.2,1103",
		width=2.2884];
	ScalePlane -> ScaleAddCols1_C	 [color=red,
		pos="e,1100.9,1112.4 741.15,1174.8 798.07,1163.6 898.09,1144.3 984.19,1130 1019.1,1124.2 1057.8,1118.5 1090.9,1113.9"];
	_ZN6libyuvL9SumPixelsEiPKt	 [height=0.5,
		pos="1528.1,1406",
		width=3.7193];
	_ZN6libyuvL15ScaleAddCols1_CEiiiiPKtPh -> _ZN6libyuvL9SumPixelsEiPKt	 [color=blue,
		pos="e,1428.7,1418.1 1319.5,1492 1333,1487.9 1346.2,1482.7 1358.2,1476 1380,1463.9 1372.8,1445.7 1394.2,1433 1402,1428.4 1410.4,1424.5 \
1419.1,1421.3"];
	_ZN6libyuvL9SumPixelsEiPKt -> __assert_func	 [color=blue,
		pos="e,1822.5,1680.9 1631.1,1417.7 1642.1,1421.5 1652.6,1426.5 1662,1433 1749.2,1493.4 1799.9,1616.1 1819.2,1671.1"];
	OUTLINED_FUNCTION_2	 [height=0.5,
		pos="1828.1,720",
		width=3.4202];
	ARGBUnattenuate -> OUTLINED_FUNCTION_2	 [color=blue,
		pos="e,1749.1,733.89 1595.5,778.08 1617,773.89 1640.7,768.52 1662,762 1678.6,756.93 1681.4,752.12 1698,747 1711.1,742.94 1725.2,739.31 \
1739,736.13"];
	ARGBUnattenuate -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1737,869.82 1599.1,798.77 1620.2,803.54 1642.7,810.6 1662,821 1681.3,831.47 1678.5,844.82 1698,855 1707.1,859.77 1717.1,863.7 \
1727.2,866.93"];
	ARGBUnattenuate -> OUTLINED_FUNCTION_0	 [color=blue,
		pos="e,1711.4,779.84 1610.5,784.88 1638.4,783.48 1670.4,781.89 1701,780.35"];
	ARGBUnattenuateRow_C	 [height=0.5,
		pos="1828.1,828",
		width=3.1673];
	ARGBUnattenuate -> ARGBUnattenuateRow_C	 [color=blue,
		pos="e,1739.9,816.53 1600.3,798.39 1639.2,803.44 1687.6,809.74 1729.9,815.23"];
	ScalePlaneBilinearUp -> ScaleSlope	 [color=blue,
		pos="e,1483.6,1324.3 1257.1,1619.3 1292.7,1617.9 1331.8,1609.6 1358.2,1584 1424.6,1519.6 1338.5,1452.8 1394.2,1379 1413.6,1353.3 1445.9,\
1337.2 1473.9,1327.4"];
	ScalePlaneBilinearUp -> InterpolateRow_C	 [color=blue,
		pos="e,1491.4,1751.9 1209,1627.7 1275.1,1656.7 1411,1716.5 1482.2,1747.8"];
	OUTLINED_FUNCTION_14	 [height=0.5,
		pos="1528.1,1568",
		width=3.5544];
	ScalePlaneBilinearUp -> OUTLINED_FUNCTION_14	 [color=blue,
		pos="e,1430.6,1579.7 1252.2,1601.2 1302,1595.2 1366.5,1587.5 1420.6,1580.9"];
	OUTLINED_FUNCTION_15	 [height=0.5,
		pos="1528.1,1622",
		width=3.5544];
	ScalePlaneBilinearUp -> OUTLINED_FUNCTION_15	 [color=blue,
		pos="e,1403,1618.1 1266.4,1613.9 1305.2,1615.1 1350.8,1616.5 1392.9,1617.8"];
	ScaleSlope -> __assert_func	 [color=blue,
		pos="e,1825.2,1681 1581.8,1316.1 1608.4,1319.6 1639.5,1327.8 1662,1346 1768.7,1432.8 1810.7,1604.1 1823.4,1671.2"];
	ScaleSlope -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1815.5,900.13 1540.4,1296.3 1587.1,1229 1753.5,989.39 1809.6,908.73"];
	__udivdi3	 [height=0.5,
		pos="1828.1,1341",
		width=1.3945];
	ScaleSlope -> __udivdi3	 [color=blue,
		pos="e,1778.9,1336.6 1580.4,1318.7 1632.9,1323.4 1713.7,1330.7 1768.7,1335.6"];
	ScaleSlope -> OUTLINED_FUNCTION_0	 [color=blue,
		pos="e,1723.2,783.43 1539,1296.4 1564.8,1253.7 1630,1141 1662,1038 1693.6,936.26 1624.7,878.34 1698,801 1702.8,795.94 1708.3,791.69 1714.2,\
788.14"];
	__divdi3	 [height=0.5,
		pos="1828.1,1287",
		width=1.2604];
	ScaleSlope -> __divdi3	 [color=blue,
		pos="e,1783.8,1291 1580.4,1309.3 1634.4,1304.4 1718.6,1296.9 1773.5,1291.9"];
	ScalePlaneVertical -> __assert_func	 [color=blue,
		pos="e,1806.9,1716.2 1247.4,1786.9 1365.2,1798.1 1586.1,1815.3 1662,1795 1714.2,1781 1767,1746.2 1798.6,1722.6"];
	OUTLINED_FUNCTION_4	 [height=0.5,
		pos="1828.1,1814",
		width=3.4202];
	ScalePlaneVertical -> OUTLINED_FUNCTION_4	 [color=blue,
		pos="e,1725.4,1824 1253,1783.6 1286.4,1787.3 1324.9,1794 1358.2,1806 1375.8,1812.4 1376.1,1822.9 1394.2,1828 1508.8,1860.2 1543.1,1833 \
1662,1828 1679.1,1827.3 1697.3,1826.1 1715,1824.8"];
	ScalePlaneVertical -> InterpolateRow_C	 [color=blue,
		pos="e,1446.5,1770.5 1254.9,1776.4 1309.3,1774.7 1380.2,1772.6 1436.2,1770.8"];
	ARGBAttenuate -> OUTLINED_FUNCTION_2	 [color=blue,
		pos="e,1711.6,725.83 1602.3,731.29 1632.1,729.8 1667.5,728.03 1701.2,726.35"];
	ARGBAttenuate -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1726.7,871.67 1603.4,736.99 1624.3,740.83 1645.7,748.25 1662,762 1695.9,790.56 1664.2,826.34 1698,855 1703.8,859.92 1710.3,864.03 \
1717.1,867.44"];
	ARGBAttenuate -> OUTLINED_FUNCTION_0	 [color=blue,
		pos="e,1735.8,762 1594.7,743.66 1633.2,748.66 1682.5,755.07 1725.8,760.7"];
	ScalePlaneBilinearDown -> ScaleSlope	 [color=blue,
		pos="e,1484.2,1324.7 1272.7,1563.3 1303.5,1560.1 1335.2,1551 1358.2,1530 1409.1,1483.5 1351,1432.8 1394.2,1379 1414.4,1353.9 1446.7,1337.8 \
1474.5,1327.9"];
	OUTLINED_FUNCTION_10	 [height=0.5,
		pos="1528.1,1460",
		width=3.5544];
	ScalePlaneBilinearDown -> OUTLINED_FUNCTION_10	 [color=blue,
		pos="e,1430.1,1471.7 1278.9,1554.9 1306.1,1550.8 1334.3,1543.3 1358.2,1530 1380,1517.9 1372.8,1499.7 1394.2,1487 1402.4,1482.1 1411.3,\
1478.1 1420.4,1474.9"];
	OUTLINED_FUNCTION_21	 [height=0.5,
		pos="1528.1,1514",
		width=3.5544];
	ScalePlaneBilinearDown -> OUTLINED_FUNCTION_21	 [color=blue,
		pos="e,1430.6,1525.7 1259,1546.4 1307.7,1540.6 1368.8,1533.2 1420.4,1527"];
	ScalePlaneBilinearDown -> InterpolateRow_C	 [color=blue,
		pos="e,1475.9,1753.9 1274.9,1551.8 1304.7,1555.3 1335.3,1564.3 1358.2,1584 1400.1,1620 1358.3,1661 1394.2,1703 1412.9,1725 1440.8,1740.1 \
1466.3,1750.3"];
	ARGBToI420 -> OUTLINED_FUNCTION_5	 [color=blue,
		pos="e,1740.2,869.33 1182.7,607.86 1211.9,651.74 1294,764.92 1394.2,816 1401.7,819.81 1604.5,849.65 1730.2,867.88"];
	ARGBToI420 -> OUTLINED_FUNCTION_4	 [color=blue,
		pos="e,1784.6,1797.1 1181.4,607.9 1209.3,654.96 1291.2,783.11 1394.2,850 1498.4,917.66 1585.5,832.09 1662,930 1716.5,999.79 1654.7,1648.8 \
1698,1726 1715,1756.4 1747.4,1778.3 1775.6,1792.7"];
	ARGBToYRow_C	 [height=0.5,
		pos="1528.1,567",
		width=2.363];
	ARGBToI420 -> ARGBToYRow_C	 [color=blue,
		pos="e,1446.7,572.25 1235.8,585.83 1291.9,582.22 1373.6,576.96 1436.4,572.91"];
	ARGBToUVRow_C	 [height=0.5,
		pos="1528.1,261",
		width=2.5566];
	ARGBToI420 -> ARGBToUVRow_C	 [color=blue,
		pos="e,1508.8,278.78 1190.4,572.31 1250.1,517.31 1432.5,349.15 1501.4,285.64"];
	OUTLINED_FUNCTION_11	 [height=0.5,
		pos="1528.1,957",
		width=3.5544];
	ARGBToI420 -> OUTLINED_FUNCTION_11	 [color=blue,
		pos="e,1435.6,944.55 1183,608.15 1228,677.15 1386.3,919.52 1394.2,925 1403.8,931.73 1414.7,937.05 1426,941.27"];
	ARGBToI420 -> OUTLINED_FUNCTION_12	 [color=blue,
		pos="e,1752.2,651.48 1235.7,594.58 1329.7,601.61 1509.7,616.45 1662,637 1688.1,640.53 1716.4,645.16 1742.1,649.69"];
	_ZN6libyuvL6RGBToYEhhh	 [height=0.5,
		pos="1828.1,612",
		width=3.5253];
	ARGBToYRow_C -> _ZN6libyuvL6RGBToYEhhh	 [color=blue,
		pos="e,1740.9,598.92 1597.7,577.44 1637.3,583.37 1687.5,590.9 1730.9,597.42"];
	OUTLINED_FUNCTION_22	 [height=0.5,
		pos="1828.1,558",
		width=3.5544];
	ARGBToYRow_C -> OUTLINED_FUNCTION_22	 [color=blue,
		pos="e,1702.9,561.76 1612.5,564.47 1637.5,563.72 1665.5,562.88 1692.9,562.06"];
	ARGBToYRow_C -> OUTLINED_FUNCTION_12	 [color=blue,
		pos="e,1733.4,653.79 1601.3,576.21 1621.9,580.95 1643.7,588.13 1662,599 1682.5,611.22 1677.2,627.09 1698,639 1706.1,643.65 1714.9,647.5 \
1723.9,650.69"];
	OUTLINED_FUNCTION_30	 [height=0.5,
		pos="1828.1,504",
		width=3.5544];
	ARGBToYRow_C -> OUTLINED_FUNCTION_30	 [color=blue,
		pos="e,1755.8,518.94 1588.2,554.19 1620.7,547.29 1661.5,538.64 1698,531 1713.5,527.75 1730.1,524.29 1746,520.98"];
	RGBToY	 [height=0.5,
		pos="1828.1,450",
		width=1.3497];
	ARGBToYRow_C -> RGBToY	 [color=red,
		pos="e,1779.3,451 1605.1,559.23 1625,554.49 1645.4,546.96 1662,535 1686.6,517.25 1673.1,494.38 1698,477 1718.7,462.54 1745.4,455.51 1769.3,\
452.2"];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_2	 [color=blue,
		pos="e,1724.4,710.25 1538.4,279.02 1563.1,322.55 1625.8,437.41 1662,540 1685.2,605.88 1647.9,644.26 1698,693 1703.1,697.98 1708.9,702.14 \
1715.1,705.62"];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_9	 [color=blue,
		pos="e,1742.8,382.92 1550,278.66 1581.1,302.78 1640.5,345.68 1698,369 1709,373.47 1720.9,377.24 1732.8,380.4"];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_18	 [color=blue,
		pos="e,1751.8,327.53 1573.1,276.72 1607.2,288.25 1655.2,303.79 1698,315 1712,318.68 1727.1,322.19 1741.7,325.38"];
	_ZN6libyuvL8RGB2xToVEttt	 [height=0.5,
		pos="1828.1,72",
		width=3.6148];
	ARGBToUVRow_C -> _ZN6libyuvL8RGB2xToVEttt	 [color=blue,
		pos="e,1734.9,84.699 1541.2,243.03 1567.1,209.06 1628.3,135.54 1698,99 1706.5,94.545 1715.6,90.825 1725,87.719"];
	_ZN6libyuvL8RGB2xToUEttt	 [height=0.5,
		pos="1828.1,18",
		width=3.6148];
	ARGBToUVRow_C -> _ZN6libyuvL8RGB2xToUEttt	 [color=blue,
		pos="e,1731.3,30.077 1536.6,242.99 1557.6,200.89 1616,95.738 1698,45 1705.4,40.411 1713.5,36.588 1721.8,33.405"];
	OUTLINED_FUNCTION_27	 [height=0.5,
		pos="1828.1,288",
		width=3.5544];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_27	 [color=blue,
		pos="e,1720.3,278.29 1612.1,268.56 1642.5,271.29 1677.4,274.44 1710.2,277.38"];
	OUTLINED_FUNCTION_37	 [height=0.5,
		pos="1828.1,234",
		width=3.5544];
	ARGBToUVRow_C -> OUTLINED_FUNCTION_37	 [color=blue,
		pos="e,1720.3,243.71 1612.1,253.44 1642.5,250.71 1677.4,247.56 1710.2,244.62"];
	RGB2xToU	 [height=0.5,
		pos="1828.1,180",
		width=1.6179];
	ARGBToUVRow_C -> RGB2xToU	 [color=red,
		pos="e,1777.8,189.19 1573.1,245.28 1607.2,233.75 1655.2,218.21 1698,207 1720.6,201.07 1745.8,195.6 1767.9,191.15"];
	RGB2xToV	 [height=0.5,
		pos="1828.1,126",
		width=1.6179];
	ARGBToUVRow_C -> RGB2xToV	 [color=red,
		pos="e,1774,132.74 1550,243.34 1581.1,219.22 1640.5,176.32 1698,153 1718.7,144.58 1742.5,138.66 1764,134.56"];
	InterpolateRow_C -> __assert_func	 [color=blue,
		pos="e,1778,1710.5 1584.9,1754.9 1637.2,1742.9 1714.7,1725.1 1768,1712.8"];
	InterpolateRow_C -> OUTLINED_FUNCTION_4	 [color=blue,
		pos="e,1742.9,1800.9 1595.8,1778.4 1636.3,1784.6 1688.4,1792.6 1732.9,1799.4"];
	memcpy	 [height=0.5,
		pos="2043.4,1835",
		width=1.2303];
	InterpolateRow_C -> memcpy	 [color=blue,
		pos="e,2021.9,1819.1 1604,1760.9 1691.3,1755 1838.1,1752.6 1958.2,1787 1977.7,1792.6 1997.6,1803.4 2013.2,1813.4"];
	_ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh -> _ZN6libyuvL9SumPixelsEiPKt	 [color=blue,
		pos="e,1428.3,1418 1288.1,1434.9 1329.9,1429.9 1377,1424.2 1418.2,1419.2"];
	_ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh -> __assert_func	 [color=blue,
		pos="e,1825.3,1680.8 1307,1436.5 1324.8,1431.8 1342.4,1425.5 1358.2,1417 1378.7,1406 1372.8,1388.2 1394.2,1379 1448.9,1355.5 1611.1,1348.1 \
1662,1379 1769.9,1444.6 1810.9,1605.6 1823.4,1670.8"];
	_ZN6libyuvL15ScaleAddCols2_CEiiiiPKtPh -> OUTLINED_FUNCTION_11	 [color=blue,
		pos="e,1418.1,966.42 1232.6,1431.9 1275.2,1416.6 1329.3,1389.8 1358.2,1346 1402.7,1278.5 1340,1043.9 1394.2,984 1398.6,979.1 1403.7,974.94 \
1409.2,971.43"];
	OUTLINED_FUNCTION_19	 [height=0.5,
		pos="1528.1,1011",
		width=3.5544];
	ScalePlaneUp2_Linear -> OUTLINED_FUNCTION_19	 [color=blue,
		pos="e,1440.9,997.8 1248.2,968.65 1301.6,976.74 1373.3,987.58 1430.7,996.26"];
	CopyPlane	 [height=0.5,
		pos="1528.1,1936",
		width=1.4838];
	ARGBCopy -> CopyPlane	 [color=blue,
		pos="e,1476.1,1931.5 1229.9,1830.8 1268.6,1831.8 1319.2,1838 1358.2,1860 1380.2,1872.4 1372.8,1890.6 1394.2,1904 1415.6,1917.4 1442.2,\
1925.2 1466.1,1929.8"];
	CopyRow_C	 [height=0.5,
		pos="1828.1,1902",
		width=1.7075];
	CopyPlane -> CopyRow_C	 [color=blue,
		pos="e,1770.6,1908.5 1579,1930.2 1629,1924.6 1705.5,1915.9 1760.5,1909.7"];
	CopyRow_C -> memcpy	 [color=blue,
		pos="e,2008,1846 1870.4,1888.8 1907.3,1877.4 1960.6,1860.8 1998.3,1849"];
	clamp255	 [height=0.5,
		pos="2043.4,828",
		width=1.3644];
	ARGBUnattenuateRow_C -> clamp255	 [color=red,
		pos="e,1994.1,828 1942.4,828 1956.7,828 1970.9,828 1984,828"];
	ScaleAddCols2_C -> __assert_func	 [color=red,
		pos="e,1765.6,1694.2 1606.1,1682 1652.3,1685.5 1710.4,1690 1755.6,1693.4"];
	ScaleARGB -> ScaleARGBRowDown2_C	 [color=red,
		pos="e,1073.8,1951 728.27,2061 781.2,2037.5 888.72,1992.4 984.19,1968 1009.7,1961.5 1037.6,1956.4 1063.9,1952.5"];
	ScaleARGB -> __assert_func	 [color=red,
		pos="e,1763.4,1700.6 703.43,2057.9 731.89,1997.5 832.85,1803.2 984.19,1729 1001.3,1720.6 1549.7,1706 1753.1,1700.9"];
	ScaleARGB -> ScaleARGBRowDownEvenBox_C	 [color=red,
		pos="e,1051.4,1897.6 718.16,2059.2 765.33,2025.6 877.71,1950.1 984.19,1914 1002.4,1907.8 1022.1,1903.1 1041.6,1899.4"];
	ScaleARGB -> ScaleSlope	 [color=red,
		pos="e,1482.1,1323.6 696.5,2057.7 703.94,1967.3 749.74,1564.9 984.19,1389 1051.1,1338.8 1275.5,1358.5 1358.2,1346 1396.4,1340.2 1439.1,\
1332.2 1472.2,1325.6"];
	ScaleARGB -> ScalePlaneVertical	 [color=red,
		pos="e,1086.6,1780.4 707.77,2058.3 744.07,2008.8 854.82,1868.1 984.19,1806 1012.5,1792.4 1045.8,1785.2 1076.3,1781.5"];
	ScaleARGB -> ScaleARGBRowDown2Box_C	 [color=red,
		pos="e,1040.4,2484.3 751.66,2070.7 809.94,2068.7 899.07,2075.7 948.19,2130 1045.4,2237.4 883.43,2349.9 984.19,2454 996.99,2467.2 1013.2,\
2476 1030.6,2481.5"];
	ScaleARGB -> malloc	 [color=red,
		pos="e,1136.1,2433.2 751.7,2070.9 809.78,2069.1 898.56,2076.3 948.19,2130 1030.4,2218.9 899.05,2313.9 984.19,2400 1020.6,2436.8 1083.3,\
2438.5 1126,2434.4"];
	ScaleARGB -> InterpolateRow_C	 [color=red,
		pos="e,1458.1,1758.5 704.11,2058 733.95,2000 836.99,1818 984.19,1752 1064.7,1715.9 1317.5,1741 1448.2,1757.2"];
	ScaleARGB -> ScaleARGBCols64_C	 [color=red,
		pos="e,1084.7,2381.4 751.89,2071.2 809.7,2069.7 897.84,2077.3 948.19,2130 1015.4,2200.4 914.63,2277.9 984.19,2346 1007.9,2369.2 1042,\
2378.3 1074.6,2380.8"];
	ScaleARGB -> ScaleARGBColsUp2_C	 [color=red,
		pos="e,1074.8,2326 752.39,2071.8 809.76,2070.8 896.77,2079 948.19,2130 1000.6,2181.9 930.11,2241.8 984.19,2292 1005.8,2312.1 1035.3,2321.4 \
1064.5,2325"];
	ScaleARGB -> ScaleARGBFilterCols64_C	 [color=red,
		pos="e,1054.2,2267.8 753.19,2072.9 809.73,2073 894.8,2082.2 948.19,2130 985.91,2163.7 945.37,2205.6 984.19,2238 1001.2,2252.2 1022.3,\
2260.8 1044.1,2265.8"];
	ScaleARGB -> ScaleARGBRowDownEven_C	 [color=red,
		pos="e,1042.4,2206.9 754.06,2076.3 808.71,2079.2 890.14,2090.6 948.19,2130 972.05,2146.2 959.8,2168.6 984.19,2184 998.8,2193.2 1015.3,\
2199.8 1032.3,2204.4"];
	ScaleARGB -> ScaleARGBFilterCols_C	 [color=red,
		pos="e,1086.8,2145.6 744.44,2085.8 801.87,2097.2 899.72,2116 984.19,2130 1014.3,2135 1047.2,2139.9 1076.9,2144.2"];
	ScaleARGB -> ARGBCopy	 [color=red,
		pos="e,1112.4,1834.1 711.83,2058.6 753.28,2016.5 866.43,1908.8 984.19,1860 1021.5,1844.6 1066.1,1837.7 1102.3,1834.8"];
	ScaleARGB -> ScaleARGBCols_C	 [color=red,
		pos="e,1086.5,2098.2 753.1,2079.3 833.5,2083.8 979.94,2092.2 1076.4,2097.6"];
	ScaleARGB -> free	 [color=red,
		pos="e,1144,2050.5 753.1,2072.7 852.07,2067.1 1051.1,2055.8 1133.8,2051.1"];
	ScaleARGB -> ScaleFilterReduce	 [color=red,
		pos="e,1100.9,2004.4 744.44,2066.2 801.87,2054.8 899.72,2036 984.19,2022 1019.1,2016.2 1057.8,2010.5 1090.9,2005.9"];
	ScaleARGB -> ScaleARGBRowDown2Linear_C	 [color=red,
		pos="e,1028.9,2535.2 751.3,2070.6 809.7,2068.4 899.35,2075.2 948.19,2130 1004.3,2193 925.99,2446.9 984.19,2508 994.11,2518.4 1006.1,2526.1 \
1019.2,2531.6"];
}

```

