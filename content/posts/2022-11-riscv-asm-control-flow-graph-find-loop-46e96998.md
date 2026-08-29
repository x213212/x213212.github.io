---
title: "riscv asm control flow graph find loop"
date: "2022-11-20T14:50:00.004+08:00"
updated: "2022-11-20T14:50:36.095+08:00"
permalink: "/2022/11/riscv-asm-control-flow-graph-find-loop.html"
original_url: "https://x8795278.blogspot.com/2022/11/riscv-asm-control-flow-graph-find-loop.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2085662222303184091"
tags: ["Control Flow Graph"]
layout: post
---

![](https://i.imgur.com/7haeJbu.png)

# asm control flow grpah domator tree
要做靜態分析要找出相似的basic block想以肉眼進行判斷，我們進一步透過tarjan-algorithm找出支配樹的節點，意味者可以找到cfg裡面的loop.
https://www.geeksforgeeks.org/tarjan-algorithm-find-strongly-connected-components/
![](https://i.imgur.com/7ddciYx.png)

主要做了一個bb index 的mapping，再傳遞給寫好的tarjan演算法即可找出cfg裡的loop

# tarjan
重新讓這演算法可以紀錄答案到list
```python

#This class represents an directed graph
# using adjacency list representation
class Graph:
  
    def __init__(self,vertices,):
        #No. of vertices
        self.V= vertices
        
        self.ans = []
        # default dictionary to store graph
        self.graph = defaultdict(list)
         
        self.Time = 0
  
    # function to add an edge to graph
    def addEdge(self,u,v):
        self.graph[u].append(v)
         
  
    '''A recursive function that find finds and prints strongly connected
    components using DFS traversal
    u --> The vertex to be visited next
    disc[] --> Stores discovery times of visited vertices
    low[] -- >> earliest visited vertex (the vertex with minimum
                discovery time) that can be reached from subtree
                rooted with current vertex
     st -- >> To store all the connected ancestors (could be part
           of SCC)
     stackMember[] --> bit/index array for faster check whether
                  a node is in stack
    '''
    def SCCUtil(self,u, low, disc, stackMember, st):
 
        # Initialize discovery time and low value
        disc[u] = self.Time
        low[u] = self.Time
        self.Time += 1
        stackMember[u] = True
        st.append(u)
 
        # Go through all vertices adjacent to this
        for v in self.graph[u]:
             
            # If v is not visited yet, then recur for it
            if disc[v] == -1 :
             
                self.SCCUtil(v, low, disc, stackMember, st)
 
                # Check if the subtree rooted with v has a connection to
                # one of the ancestors of u
                # Case 1 (per above discussion on Disc and Low value)
                low[u] = min(low[u], low[v])
                         
            elif stackMember[v] == True:
 
                '''Update low value of 'u' only if 'v' is still in stack
                (i.e. it's a back edge, not cross edge).
                Case 2 (per above discussion on Disc and Low value) '''
                low[u] = min(low[u], disc[v])
 
        # head node found, pop the stack and print an SCC
        w = -1 #To store stack extracted vertices
        anscell = []
        if low[u] == disc[u]:
            while w != u:
                w = st.pop()
                print (w, end=" ")
                anscell.append(w)
                stackMember[w] = False
            self.ans.append(anscell)
            print()
             
     
 
    #The function to do DFS traversal.
    # It uses recursive SCCUtil()
    def SCC(self):
  
        # Mark all the vertices as not visited
        # and Initialize parent and visited,
        # and ap(articulation point) arrays
        disc = [-1] * (self.V)
        low = [-1] * (self.V)
        stackMember = [False] * (self.V)
        st =[]
         
 
        # Call the recursive helper function
        # to find articulation points
        # in DFS tree rooted with vertex 'i'
        time_disc=[]
        for i in range(self.V):
            if disc[i] == -1:
                self.SCCUtil(i, low, disc, stackMember, st)
            time_disc.append([i,disc[i]])
        for x in time_disc:
            print(x)
        print("time")
```
# cfg5
這邊注意
```
 if(jkey>cur_bb_index):
                    tarjans.addEdge(key, jkey)
```
我故意讓當前節點jump 只能大於目前節點，類似強迫cfg只能往下走，這樣 tarjan 就不會把整個fucntion當成連通(一組解)
```python

def draw_cfg5(function_name,get_print_list, view):
    dot=None
    dot2=None
    index =0
    
    dot = Digraph(name=function_name, comment=function_name, engine='dot')
    dot2 = Digraph(name=function_name, comment=function_name, engine='dot')
    # dot.graph_attr['rankdir'] = 'LR'
    dot.attr('graph', label=function_name)
    dot2.attr('graph', label=function_name)

    total_node =0
    index =0
    cur_bb_index=0
    for get_child in get_print_list:
        for address, basic_block in get_child[1].items():
            key = str(address)
            graph[key] =[]
            total_node+=1
        for basic_block in  get_child[1].values():
            bb_index_mapping[str(cur_bb_index)] =str(basic_block.key)
            cur_bb_index+=1
        cur_bb_index=0
        break

    cur_bb_index=0
    tarjansans=[]

    # Create a graph given in the above diagram
    tarjans = Graph(total_node)
    for get_child in get_print_list:
        for basic_block in  get_child[1].values():
            if basic_block.jump_edge:
                key=0
                jkey=0
                nojkey=0
                if basic_block.no_jump_edge is not None:
                    for x in bb_index_mapping:
                        if(bb_index_mapping[x] == str(basic_block.key)):
                            key=int(x)
                        elif(bb_index_mapping[x] == str(basic_block.no_jump_edge)):
                            nojkey=int(x)
                    tarjans.addEdge(key, nojkey)

                for x in bb_index_mapping:
                    if(bb_index_mapping[x] == str(basic_block.key)):
                        key=int(x)
                    elif(bb_index_mapping[x] == str(basic_block.jump_edge)):
                        jkey=int(x)

                if(jkey>cur_bb_index):
                    tarjans.addEdge(key, jkey)

            elif basic_block.no_jump_edge:       
                key=0
                nojkey=0
                for x in bb_index_mapping:
                    if(bb_index_mapping[x] == str(basic_block.key)):
                        key=int(x)
                    elif(bb_index_mapping[x] == str(basic_block.no_jump_edge)):
                        nojkey=int(x)

                tarjans.addEdge(key, nojkey)
        cur_bb_index=0
        break
    
    print ("SSC in first graph ")
    tarjans.SCC()
    print(total_node)
    print ("tarjans")
    count_tarjans_ans_index=0
    for x in tarjans.ans:
        if(len (x)>2):
            count_tarjans_ans_index+=1

    green = Color("green")
    colors = list(green.range_to(Color("blue"),count_tarjans_ans_index+1))

    for get_child in get_print_list:
        for address, basic_block in get_child[1].items():
            key = str(address)            
            newkey =""
            tarjankey=0
            find =0
         
            for x in bb_index_mapping:
                if(bb_index_mapping[x] == str(basic_block.key)):
                    tarjankey=int(x)
                    break
            count_tarjans_ans_index=0
            for x in tarjans.ans:
                if(len (x)>2):
                    if(tarjankey in x):
                        find=1
                        print("tarjanskey:"+str(tarjankey))
                        break
                    count_tarjans_ans_index+=1
            
            if(find==0):
                dot.node(key, shape='record', label=basic_block.get_label(),style="filled",fillcolor="white")
            else:
                dot.node(key, shape='record', label=basic_block.get_label(),style="filled",fillcolor=str(colors[count_tarjans_ans_index]))
                
        for basic_block in get_child[1].values():
            if basic_block.jump_edge:
                if basic_block.no_jump_edge is not None:
                    dot.edge(f'{basic_block.key}:s0', str(basic_block.no_jump_edge))
                dot.edge(f'{basic_block.key}:s1', str(basic_block.jump_edge))
            elif basic_block.no_jump_edge:
                    dot.edge(f'{basic_block.key}:s0', str(basic_block.no_jump_edge))
        break

    if view:
        dot.format = 'gv'
        with tempfile.NamedTemporaryFile(mode='w+b', prefix=function_name) as filename:
            # dot.view(filename.name)
            print(f'Opening a file {filename.name}.{dot.format} with default viewer. Don\'t forget to delete it later.')
    else:
        dot.format = 'svg'
        dot.render(filename=function_name, cleanup=True)
        print(f'Saved CFG to a file {function_name}.{dot.format}')
        replaceline_0(f'{function_name}.{dot.format}', f'back{function_name}.{dot.format}')
        redundant(f'back{function_name}.{dot.format}', f'new{function_name}.{dot.format}')
        # replaceline(f'back{function_name}.{dot.format}', f'new{function_name}.{dot.format}')
        print(f'Saved new CFG to a file new{function_name}.{dot.format}')

```

結果呈現
![](https://i.imgur.com/7haeJbu.png)
,確實可以找loop的開頭與結尾，這項功能應該又可以衍生出更多的演算法可以做靜態分析，知道某些區間可能有unrooling loop..。

