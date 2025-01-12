#!/usr/bin/env bash

# 设置窗口标题（适用于 macOS）
echo -e "\033]0;正在运行...\007"

# 执行 Python 脚本并检查是否成功
echo "正在运行 run_testcases.py..."
python run_testcases.py
if [ $? -ne 0 ]; then
    echo "运行 run_testcases.py 失败。"
    deactivate
    exit 1
fi


