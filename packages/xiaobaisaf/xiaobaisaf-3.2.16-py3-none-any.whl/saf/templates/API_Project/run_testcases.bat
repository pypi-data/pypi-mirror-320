@echo off

REM ���ñ���
title Running run_testcases.py...
python run_testcases.py
IF %ERRORLEVEL% NEQ 0 (
    echo ����run_testcases.pyʧ��.
    ENDLOCAL
    EXIT /B 1
)