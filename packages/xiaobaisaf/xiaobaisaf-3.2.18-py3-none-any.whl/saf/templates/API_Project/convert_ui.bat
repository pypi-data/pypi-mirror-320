@echo off

REM ���ñ���
title Running convert_ui.py...
python convert_ui.py
IF %ERRORLEVEL% NEQ 0 (
    echo ����convert_ui.pyʧ��.
    ENDLOCAL
    EXIT /B 1
)