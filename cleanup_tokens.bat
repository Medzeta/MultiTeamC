@echo off
echo Rensar token-filer från Git...

REM Remove files with tokens from Git tracking
git rm --cached complete_build_and_deploy.bat 2>nul
git rm --cached push_with_new_token.bat 2>nul
git rm --cached create_and_push_github.bat 2>nul
git rm --cached push_with_token.bat 2>nul

REM Add to .gitignore
echo complete_build_and_deploy.bat >> .gitignore
echo push_with_new_token.bat >> .gitignore
echo create_and_push_github.bat >> .gitignore
echo push_with_token.bat >> .gitignore

echo Token-filer rensade från Git!
pause
