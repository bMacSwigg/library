@ECHO OFF

CD ../..

REM TODO: verify python & pip

ECHO Installing dependencies
REM Install project dependencies
pip install -r requirements.txt
REM Install pyinstaller to build executables
pip install pyinstaller

ECHO Bundling executable
REM Bundle the script, starting from main.py as the base file
REM --distpath ~/library: put the bundled app in ~/library
REM -F: bundle as a single file, rather than a directory
REM -n library: name it library.exe (and not main.exe)
REM -w: run in windowed mode (no accompanying command prompt)
REM -i book-solid.ico: set the icon image
pyinstaller ^
  --distpath run --workpath run\tmp ^
  --add-data book-solid.ico:. ^
  -F -n library -w ^
  main.py

ECHO Deleting temp files
RMDIR run\tmp /s
DEL library.spec

ECHO Library is now installed at %cd%\run\library.exe

SET /P MAKEDB=Do you want to initialize a blank database (Y/[N])?
IF /I "%MAKEDB%" NEQ "Y" EXIT /B

ECHO Creating and initializing database
python setup\makedb.py backend\books.schema run\books.db
