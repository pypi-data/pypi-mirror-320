@echo off

REM 设置标题
title Running run_testcases.py...
python run_testcases.py
IF %ERRORLEVEL% NEQ 0 (
    echo 运行run_testcases.py失败.
    ENDLOCAL
    EXIT /B 1
)