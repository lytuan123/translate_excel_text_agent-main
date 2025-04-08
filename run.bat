@echo off
echo Starting Advanced Translation Suite...

:: Activate virtual environment
call myenv\Scripts\activate

:: Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%

:: Run the application
python app/web_app.py

:: Wait for a few seconds to ensure the server is up
timeout /t 5 /nobreak >nul

:: Read the Gradio URL from the file
set /p GRADIO_URL=<gradio_url.txt

:: Open the Gradio link in the default web browser
start %GRADIO_URL%

pause
