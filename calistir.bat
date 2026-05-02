@echo off
:: ============================================================
:: TEFAS Fon Verisi Çekici - Windows Görev Zamanlayıcısı için
:: Bu dosyayı tefas_bot.py ile aynı klasöre koy
:: ============================================================

:: Script'in bulunduğu klasöre git
cd /d "%~dp0"

echo [%date% %time%] TEFAS guncelleme basliyor... >> tefas_log.txt

:: Python ile scripti çalıştır
python tefas_bot.py >> tefas_log.txt 2>&1

if %errorlevel% == 0 (
    echo [%date% %time%] Basarili! >> tefas_log.txt
) else (
    echo [%date% %time%] HATA olustu! >> tefas_log.txt
)

:: GitHub'a push et
git add "yatirim_fonlari .json"
git diff --staged --quiet
if %errorlevel% == 1 (
    git commit -m "chore: TEFAS fon verileri guncellendi"
    git push
    echo [%date% %time%] GitHub push tamamlandi >> tefas_log.txt
) else (
    echo [%date% %time%] Degisiklik yok, push atilmadi >> tefas_log.txt
)
