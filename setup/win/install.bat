@ECHO OFF

CD ../..

REM TODO: verify python & pip

ECHO [92mInstalling dependencies[0m
REM Install project dependencies
pip install -r src\library\requirements.txt
REM Install pyinstaller to build executables
pip install pyinstaller

ECHO [92mDo you want to connect to a remote server?
ECHO If yes, you will be prompted to enter a remote address.
ECHO If no, this install will be configured for a local database.[0m
SET /P REMOTE=(Y/[N])
IF /I "%REMOTE%" NEQ "Y" (
  GOTO local
) ELSE (
  GOTO remote
)

:local
ECHO [92mConfiguring local install[0m
REM Leave config file as-is with local db
MKDIR run\tmp
COPY src\library\config.ini run\tmp\config.ini
REM Optionally create a new local DB
SET /P MAKEDB=Do you want to initialize a blank database (Y/[N])?
IF /I "%MAKEDB%" NEQ "Y" GOTO install
ECHO Creating and initializing database
python setup\makedb.py src\library\backend\books.schema run\books.db
GOTO install

:remote
ECHO [92mConfiguring remote install[0m
REM Edit config file to have remote address
MKDIR run\tmp
COPY src\library\config.ini run\tmp\config.ini
SET /P ADDR=What is the URL of the remote server?
ECHO RemoteBackend = %ADDR% >> run\tmp\config.ini
GOTO install

:install
ECHO [92mBundling executable[0m
REM Bundle the script, starting from main.py as the base file
REM --distpath ~/library: put the bundled app in ~/library
REM --add-data [...]: data files to bundle inside the app
REM -F: bundle as a single file, rather than a directory
REM -n library: name it library.exe (and not main.exe)
REM -w: run in windowed mode (no accompanying command prompt)
pyinstaller ^
  --distpath run --workpath run\tmp ^
  --add-data src\library\book-solid.ico:. ^
  --add-data run\tmp\config.ini:. ^
  -F -n library -w ^
  src\library\main.py

ECHO [92mDeleting temp files[0m
RMDIR run\tmp /s /q
DEL library.spec

ECHO [92mLibrary is now installed at %cd%\run\library.exe[0m

PAUSE
