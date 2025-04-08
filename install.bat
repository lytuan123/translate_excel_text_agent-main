@echo off
echo Installing Advanced Translation Suite...

:: Create virtual environment
python -m venv myenv
call myenv\Scripts\activate

:: Install requirements
pip install -r requirements.txt

echo Installation completed!
echo Please run run.bat to start the application.
pause 