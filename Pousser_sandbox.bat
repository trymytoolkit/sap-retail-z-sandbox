@echo off
setlocal
:: ============================================================================
:: Sandbox Retail Z : pousser le depot vers GitHub (apres des modifications
:: faites sur ce PC, par exemple les objets ecrits par Claude).
:: Ensuite, sur la VM : abapGit > Pull pour les importer dans SAP.
:: ============================================================================
cd /d "%~dp0"
where git >nul 2>nul || (echo  [!] git introuvable & pause & exit /b 1)
if exist ".git\index.lock" del /f /q ".git\index.lock"
echo [*] Normalisation des fins de ligne (abapGit attend du LF)...
call git add --renormalize -A
call git add -A
call git -c user.name="trymytoolkit" -c user.email="trymytoolkit@users.noreply.github.com" commit -m "Sandbox %date% %time%"
call git push -u origin HEAD
echo.
echo  Pousse : https://github.com/trymytoolkit/sap-retail-z-sandbox
echo  Sur la VM : abapGit, depot sap-retail-z-sandbox, Pull.
pause
