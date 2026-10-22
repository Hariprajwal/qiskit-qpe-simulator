Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  QUANTUM PHASE ESTIMATION (QPE) - STREAMLIT DASHBOARD" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = $PSScriptRoot
if (Test-Path "$baseDir\New Folder With Items\app.py") {
    Set-Location "$baseDir\New Folder With Items"
} elseif (Test-Path "$baseDir\app.py") {
    Set-Location "$baseDir"
}

Write-Host "[*] Project directory: $(Get-Location)" -ForegroundColor Green

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[*] Creating fresh Windows Python virtual environment (venv)..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "[*] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

python -c "import streamlit, qiskit, qiskit_aer, plotly, pyarrow" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[*] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    pip install -r requirements.txt
}

Write-Host "============================================================" -ForegroundColor Green
Write-Host "[*] Launching Streamlit Dashboard at http://localhost:8501" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
python -m streamlit run app.py
