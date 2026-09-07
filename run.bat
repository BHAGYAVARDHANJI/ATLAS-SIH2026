@echo off
setlocal
if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found.
    echo Please double-click setup.bat first.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
streamlit run atlas_app\Home.py
endlocal
pause
