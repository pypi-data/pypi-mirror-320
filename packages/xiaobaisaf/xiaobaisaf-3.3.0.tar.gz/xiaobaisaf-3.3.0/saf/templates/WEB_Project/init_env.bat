@echo off
:: SETLOCAL

REM ���ñ���
title Running...

REM ������⻷��Ŀ¼�Ƿ���ڣ��������򴴽�
IF NOT EXIST "venv" (
    echo �������⻷����...
    python -m venv venv
) ELSE (
    echo ���⻷���Ѿ����ڡ�
)

REM �������⻷��
IF NOT DEFINED _OLD_VIRTUAL_PROMPT (
    call venv\Scripts\activate.bat
)

REM ��װ����
echo ��װ������...
pip install -r requirements.txt --upgrade
IF %ERRORLEVEL% NEQ 0 (
    echo ��װ����ʧ��.
    ENDLOCAL
    EXIT /B 1
)



REM ����׼����ϣ�ִ����������
echo ����׼����ϣ�ִ����������
:: ENDLOCAL
