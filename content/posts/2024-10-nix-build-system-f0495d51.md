---
title: "nix build system"
date: "2024-10-26T18:00:00.002+08:00"
updated: "2024-10-26T18:02:32.943+08:00"
permalink: "/2024/10/nix-build-system.html"
original_url: "https://x8795278.blogspot.com/2024/10/nix-build-system.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8495518337755977464"
tags: ["nix", "rust"]
layout: post
---

![](https://hackmd.io/_uploads/r1I4RNqxkx.png)

# nix
學一下cicd常用的套件
https://github.com/x213212/nix-project-test
最近也用chatgpt 用rust 寫了一套 build-system
應該可以搭配服用
https://github.com/x213212/minibuildsystem

# install
```
1. Installing and Configuring Nix
Install Nix on WSL and Set Up Multi-User Configuration:
# Download the Nix installation script
curl -L https://nixos.org/nix/install | sh
# After installation, create the `nixbld` group
sudo groupadd nixbld
# Create 10 users and add them to the `nixbld` group
for i in $(seq 1 10); do sudo useradd -m nixbld$i -g nixbld; done
```
# usage
```
nix-build # build add
nix-build -A appA
```

# backup
```
 ls /nix/store | grep appA
```

# dep
drv 會記錄 build 該 nix project 所有 dep lib
```
nix log /nix/store/085svyj39q9mg9gkq9vbpyby51s7az5a-appA.drv --extra-experimental-features nix-commandnix log /nix/store/085svyj39q9mg9gkq9vbpyby51s7az5a-appA.drv --extra-experimental-features nix-command
```
# garbagenix-collectgarbagenix-collect
```
nix-collect-garbagenix-collect-garbage
```
最後補一個自動化出dep 的 python
```python
import os
import re
import subprocess

# Define target directory and output files
TARGET_DIR = "/root/nix-project"
DOT_FILE = "dependencies.dot"
OUTPUT_IMAGE = "dependencies.png"

# Initialize DOT file content
dot_content = ["digraph dependencies {"]

# Traverse the directory to find .nix files
for root, _, files in os.walk(TARGET_DIR):
    for file in files:
        if file.endswith(".nix"):
            nix_path = os.path.join(root, file)
            
            # Read the .nix file content
            with open(nix_path, 'r') as f:
                content = f.read()

                # Extract the "name" attribute
                name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
                if name_match:
                    name = name_match.group(1)
                    
                    # Extract "buildInputs" dependencies
                    build_inputs_match = re.search(r'buildInputs\s*=\s*\[(.*?)\];', content, re.DOTALL)
                    if build_inputs_match:
                        dependencies = build_inputs_match.group(1)
                        # Add each dependency to the DOT file content
                        for dep in dependencies.split():
                            dep = dep.strip()
                            if dep:  # Check if dependency is not empty
                                dot_content.append(f'  "{name}" -> "{dep}";')

# Finalize DOT file content
dot_content.append("}")

# Write content to the .dot file
with open(DOT_FILE, 'w') as f:
    f.write("\n".join(dot_content))

# Use Graphviz to generate the dependency image
subprocess.run(["dot", "-Tpng", DOT_FILE, "-o", OUTPUT_IMAGE])

print(f"Dependency graph generated: {OUTPUT_IMAGE}")
import os
import re
import subprocess

# Define target directory and output files
TARGET_DIR = "/root/nix-project"
DOT_FILE = "dependencies.dot"
OUTPUT_IMAGE = "dependencies.png"

# Initialize DOT file content
dot_content = ["digraph dependencies {"]

# Traverse the directory to find .nix files
for root, _, files in os.walk(TARGET_DIR):
    for file in files:
        if file.endswith(".nix"):
            nix_path = os.path.join(root, file)
            
            # Read the .nix file content
            with open(nix_path, 'r') as f:
                content = f.read()

                # Extract the "name" attribute
                name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
                if name_match:
                    name = name_match.group(1)
                    
                    # Extract "buildInputs" dependencies
                    build_inputs_match = re.search(r'buildInputs\s*=\s*\[(.*?)\];', content, re.DOTALL)
                    if build_inputs_match:
                        dependencies = build_inputs_match.group(1)
                        # Add each dependency to the DOT file content
                        for dep in dependencies.split():
                            dep = dep.strip()
                            if dep:  # Check if dependency is not empty
                                dot_content.append(f'  "{name}" -> "{dep}";')

# Finalize DOT file content
dot_content.append("}")

# Write content to the .dot file
with open(DOT_FILE, 'w') as f:
    f.write("\n".join(dot_content))

# Use Graphviz to generate the dependency image
subprocess.run(["dot", "-Tpng", DOT_FILE, "-o", OUTPUT_IMAGE])

print(f"Dependency graph generated: {OUTPUT_IMAGE}")

```
![image](https://hackmd.io/_uploads/Bk923Vqg1e.png)

