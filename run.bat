@echo off
REM Study Group Matcher - Windows Deployment Script

echo.
echo ================================
echo Study Group Matcher - Setup
echo ================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker Compose is not installed.
    pause
    exit /b 1
)

echo [OK] Docker and Docker Compose found
echo.

REM Ask for action
echo Select action:
echo 1. Start local development environment
echo 2. Stop all services
echo 3. Rebuild and restart
echo 4. View logs
echo 5. Seed database
set /p ACTION="Enter choice (1-5) [default: 1]: "
if "%ACTION%"=="" set ACTION=1

if "%ACTION%"=="1" goto START
if "%ACTION%"=="2" goto STOP
if "%ACTION%"=="3" goto REBUILD
if "%ACTION%"=="4" goto LOGS
if "%ACTION%"=="5" goto SEED
goto INVALID

:START
echo.
echo Starting local development environment...
echo.

REM Update .env for local development if needed
echo DATABASE_URL=sqlite:///./students.db > .env.tmp
findstr /v "DATABASE_URL" .env >> .env.tmp
move /y .env.tmp .env >nul
echo [OK] Updated .env for SQLite

echo.
echo Building Docker images...
docker-compose build
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo Starting services...
docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Seeding database...
docker-compose exec backend python -m app.seed
if %ERRORLEVEL% neq 0 (
    echo [WARN] Database seeding skipped (may already be seeded)
)

echo.
echo ================================
echo [SUCCESS] Services started!
echo ================================
echo.
echo Frontend: http://localhost:80
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo View logs: docker-compose logs -f
echo Stop services: docker-compose down
pause
goto END

:STOP
echo.
echo Stopping all services...
docker-compose down
echo.
echo [OK] All services stopped
pause
goto END

:REBUILD
echo.
echo Rebuilding and restarting...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo.
echo [OK] Rebuild complete
pause
goto END

:LOGS
echo.
echo Viewing logs (Ctrl+C to exit)...
docker-compose logs -f
goto END

:SEED
echo.
echo Seeding database...
docker-compose exec backend python -m app.seed
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to seed database
    pause
    exit /b 1
)
echo.
echo [OK] Database seeded successfully
pause
goto END

:INVALID
echo.
echo [ERROR] Invalid choice
pause
goto END

:END
echo.
echo ================================
echo Done!
echo ================================
