@echo off
echo Starting Advanced Translation Suite...

:: Chuyển sang ổ D:
D:

:: Di chuyển đến thư mục dự án
cd "D:\Github resporitories\translate_excel_text_agent-main1\translate_excel_text_agent-main"

:: Chạy server ở cửa sổ mới, không block
start cmd /k "call myenv\Scripts\activate && set PYTHONPATH=%PYTHONPATH%;%CD% && python run.py web"

:: Đợi 5 giây
timeout /t 5 /nobreak >nul

:: Mở trang web
start http://127.0.0.1:7860/


pause
