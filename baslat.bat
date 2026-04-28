@echo off
echo ==============================================
echo Mr. Fridge - Backend ve Frontend Baslatiliyor
echo ==============================================

echo [1/2] Backend (FastAPI) baslatiliyor...
start "Mr. Fridge Backend" cmd /k "cd backend && ..\.venv_kivy\Scripts\activate && uvicorn main:app --reload"

echo [2/2] Sunucunun hazir olmasi icin 3 saniye bekleniyor...
timeout /t 3 /nobreak > nul

echo Frontend (Kivy) baslatiliyor...
start "Mr. Fridge Frontend" cmd /k "cd frontend && ..\.venv_kivy\Scripts\activate && python main.py"

echo Bitti! Her iki uygulama da ayri pencerelerde calismaya basladi.
