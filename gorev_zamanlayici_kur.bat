@echo off
:: ============================================================
:: Görev Zamanlayıcısı'na otomatik kurulum
:: Yönetici olarak çalıştır!
:: ============================================================

:: Bu dosyanın bulunduğu klasörü al
set "SCRIPT_DIR=%~dp0"
set "BAT_PATH=%SCRIPT_DIR%calistir.bat"

:: Her hafta içi 19:30'da çalışacak görev oluştur
schtasks /create ^
  /tn "TEFAS Fon Guncelle" ^
  /tr "\"%BAT_PATH%\"" ^
  /sc weekly ^
  /d MON,TUE,WED,THU,FRI ^
  /st 19:30 ^
  /f ^
  /rl highest

if %errorlevel% == 0 (
    echo.
    echo BASARILI! Gorev olusturuldu.
    echo Her hafta ici saat 19:30'da otomatik calisacak.
    echo.
    echo Gorevi kontrol etmek icin: Gorev Zamanlayicisi ^> TEFAS Fon Guncelle
) else (
    echo.
    echo HATA: Lutfen bu dosyayi sag tikla - Yonetici olarak calistir
)
pause
