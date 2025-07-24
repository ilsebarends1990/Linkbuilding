# WordPress Link Manager Stop Script
Write-Host "Stopping WordPress Link Manager services..." -ForegroundColor Red
Write-Host ""

# Function to kill processes on specific ports
function Stop-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                    Select-Object -ExpandProperty OwningProcess | 
                    ForEach-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }
        
        if ($processes) {
            foreach ($process in $processes) {
                Write-Host "Stopping $ServiceName (PID: $($process.Id))..." -ForegroundColor Yellow
                Stop-Process -Id $process.Id -Force
            }
            Write-Host "$ServiceName stopped successfully" -ForegroundColor Green
        } else {
            Write-Host "$ServiceName not running on port $Port" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "Error stopping $ServiceName`: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Stop backend (port 8000)
Stop-ProcessOnPort -Port 8000 -ServiceName "FastAPI Backend"

# Stop frontend (port 5173)
Stop-ProcessOnPort -Port 5173 -ServiceName "React Frontend"

# Also kill any python uvicorn processes
try {
    $uvicornProcesses = Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*uvicorn*" }
    foreach ($process in $uvicornProcesses) {
        Write-Host "Stopping uvicorn process (PID: $($process.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $process.Id -Force
    }
}
catch {
    # Ignore errors if no processes found
}

Write-Host ""
Write-Host "All services stopped" -ForegroundColor Green
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
