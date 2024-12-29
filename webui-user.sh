#!/bin/bash


unset no_proxy
unset http_proxy
unset https_proxy
unset ftp_proxy
unset NO_PROXY
unset HTTP_PROXY
unset HTTPS_PROXY
unset FTP_PROXY
unset ALL_PROXY
unset all_proxy
unset ALL_PROXY

export HF_ENDPOINT=https://hf-mirror.com

#########################################################
# Uncomment and change the variables below to your need:#
#########################################################

# Install directory without trailing slash
install_dir="/home/sunset/newspace/stable-diffusion-webui-forge/myinstall"

# Name of the subdirectory
clone_dir="stable-diffusion-webui-forge/myclone"

# Commandline arguments for webui.py, for example:
export COMMANDLINE_ARGS=" --xformers --no-gradio-queue"
#export COMMANDLINE_ARGS="--medvram --opt-split-attention"

# python3 executable
python_cmd="python3"

# git executable
export GIT="git"

#python3 venv without trailing slash (defaults to ${install_dir}/${clone_dir}/venv)
venv_dir="venv"

# script to launch to start the app
export LAUNCH_SCRIPT="launch.py"

# install command for torch
export TORCH_COMMAND="pip install torch==1.12.1+cu113 --extra-index-url  https://download.pytorch.org/whl/cu113"

# Requirements file to use for stable-diffusion-webui
export REQS_FILE="requirements_versions.txt"

# Fixed git repos
#export K_DIFFUSION_PACKAGE=""
#export GFPGAN_PACKAGE=""

# Fixed git commits
#export STABLE_DIFFUSION_COMMIT_HASH=""
#export CODEFORMER_COMMIT_HASH=""
#export BLIP_COMMIT_HASH=""

# Uncomment to enable accelerated launch
# export ACCELERATE="True"

# Uncomment to disable TCMalloc
export NO_TCMALLOC="True"

###########################################:
