Windows Subsystem for Linex (WSL) is a compatibility layer for Linux binaries to run directly on Windows (via a Linux kernel).
Installed via: `$ wsl --install`

Some good base package installations:
```zsh
# update package index and upgrade installed ones
$ sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    build-essential \
    curl \
    wget \
    git \
    ca-certificates \
    zip unzip \
    htop \
    tmux \
    software-properties-common \
    python3 python3-pip python3-venv
```

It allows you to run a full Linux environment natively on your Windows machine without a VM or dual-boot setup.

This provides a quick, convenient, and direct access to all of Linux's file system utilities, tools, packages, etc.

The local data stored on your machine is also shared and **synced** within the Linux envrionment under the path:
`$ /mnt/c/Users/<Windows_username>/...`,
where `mnt/` is the mount point to access the Windows file system. 

However, when running scripts in WSL, it's advisable to move pertinent directories/files from the mounted drive into the home directory in WSL. This allows for faster read and write access.

But then, how do we modify the files directly within the WSL environment?
1. Install VS Code locally (on Windows) and install the WSL extension
2. In WSL CLI (Ubuntu), navigate toward the project directory and run `$ code .`
