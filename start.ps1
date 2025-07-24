# WordPress Link Manager Startup Script
Write-Host "Starting WordPress Link Manager..." -ForegroundColor Green
Write-Host ""

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Check if backend is already running
if (Test-Port 8000) {
    Write-Host "Backend already running on port 8000" -ForegroundColor Yellow
} else {
    Write-Host "Starting FastAPI backend..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal
}

# Wait for backend to start
Start-Sleep -Seconds 3

# Check if frontend is already running
if (Test-Port 5173) {
    Write-Host "Frontend already running on port 5173" -ForegroundColor Yellow
} else {
    Write-Host "Starting React frontend..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd drijfveer-dashboard; npm run dev" -WindowStyle Normal
}

Write-Host ""
Write-Host "Services are starting up..." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Blue
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Blue
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "Press any key to exit (services will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
