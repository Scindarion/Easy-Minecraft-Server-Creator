@echo off
setlocal enabledelayedexpansion

:: === Load latest Mojang release ===
for /f %%i in ('python -c "import requests; print(requests.get(\"https://piston-meta.mojang.com/mc/game/version_manifest_v2.json\").json()[\"latest\"][\"release\"])"') do set latest=%%i

:: === Load defaults from config ===
for /f %%v in ('python -c "import json; print(json.load(open(\"config.json\")).get(\"default_version\") or 'latest')"') do set defver=%%v
for /f %%p in ('python -c "import json; print(json.load(open(\"config.json\")).get(\"default_port\", 25565))"') do set defport=%%p

:menu
cls
echo ==============================
echo     Minecraft Server Wizard
echo ==============================
echo [1] Launch Full Menu
echo [2] Create Vanilla Server (!defver! on port !defport!)
echo [3] Create Paper Server   (!defver! on port !defport!)
echo [4] Custom Version
echo [5] Edit Settings
echo [6] Delete Server
echo [7] Exit
echo ==============================
echo If you get an error message about corruption,
echo go to the "servers" folder and delete the version that failed.
echo.
set /p choice="Choose an option: "

if "%choice%"=="1" (
    python wizard.py --menu
    pause
    goto menu
)
if "%choice%"=="2" (
    python wizard.py !defver! vanilla
    pause
    goto menu
)
if "%choice%"=="3" (
    python wizard.py !defver! paper
    pause
    goto menu
)
if "%choice%"=="4" (
    set /p customver="Enter Minecraft version (e.g. 1.20.1): "
    set /p rawtype="Enter server type (vanilla/paper): "

    if "!rawtype!"=="" (
        echo No server type entered. Aborting.
        pause
        goto menu
    )

    set "rawtype=!rawtype: =!"
    for /f "tokens=* delims=" %%A in ("!rawtype!") do set "stype=%%A"

    echo Server type detected: '!stype!'
    if /I "!stype!"=="vanilla" (
        python wizard.py !customver! vanilla
    ) else if /I "!stype!"=="paper" (
        python wizard.py !customver! paper
    ) else (
        echo Invalid server type. Only 'vanilla' or 'paper' are allowed.
    )
    pause
    goto menu
)
if "%choice%"=="5" (
    python wizard.py --settings
    pause
    goto menu
)
if "%choice%"=="6" (
    echo Launching Delete Server menu...
    python wizard.py --menu
    pause
    goto menu
)
if "%choice%"=="7" exit

goto menu
