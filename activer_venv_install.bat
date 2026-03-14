@echo off
REM Active le .venv a la racine (Flash_dash) et installe requirements.txt
cd /d "%~dp0"
echo Activation du venv...
call .venv\Scripts\activate.bat
echo Installation des dependances (requirements.txt)...
pip install -r requirements.txt
echo.
echo Termine. Vous pouvez lancer vos scripts avec: python ...
pause
