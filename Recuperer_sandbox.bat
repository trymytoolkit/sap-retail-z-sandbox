@echo off
setlocal
:: ============================================================================
:: Sandbox Retail Z : recuperer sur ce PC ce qui a ete commite depuis la VM
:: (abapGit > Stage > Commit sur la VM, puis ce script ici).
:: ============================================================================
cd /d "%~dp0"
where git >nul 2>nul || (echo  [!] git introuvable & pause & exit /b 1)
if exist ".git\index.lock" del /f /q ".git\index.lock"
call git add --renormalize -A >nul 2>nul
call git stash >nul 2>nul
call git pull --rebase origin HEAD
call git stash pop >nul 2>nul
echo.
echo  Depot a jour : C:\Dev\SAP\sap-retail-z-sandbox
pause
