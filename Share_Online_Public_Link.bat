@echo off
title 🌐 ScamShield AI - Share Online Public Link
color 0E

echo ===============================================================================
echo            🌐 SCAMSHIELD AI: WORLDWIDE PUBLIC SHARE LINK (TUNNEL)
echo ===============================================================================
echo.
echo This tool generates a temporary secure public HTTPS link so anyone can test
echo ScamShield AI from ANY device, phone, or laptop in the world without being
echo connected to the same Wi-Fi!
echo.
echo [1/2] Checking if local ScamShield AI app is running...
echo Make sure you have started ScamShield AI (via Launch_ScamShield_AI.bat) first.
echo.
echo [2/2] Generating instant public HTTPS URL via Localtunnel...
echo.
echo -------------------------------------------------------------------------------
echo Your public link will appear below in a few seconds.
echo (When opening on a mobile browser, enter your laptop's public IP if prompted).
echo -------------------------------------------------------------------------------
echo.

npx localtunnel --port 8501

pause
