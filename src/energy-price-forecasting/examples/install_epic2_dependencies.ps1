# Install Epic 2 Dependencies Script
# Run this script to install pmdarima and prophet packages

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Epic 2 Dependency Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version
Write-Host "Python: $pythonVersion" -ForegroundColor Green

# Check if packages are already installed
Write-Host ""
Write-Host "Checking current installation..." -ForegroundColor Yellow
python -c "try: import pmdarima; print('[OK] pmdarima already installed'); except ImportError: print('[MISSING] pmdarima not installed')"
python -c "try: import prophet; print('[OK] prophet already installed'); except ImportError: print('[MISSING] prophet not installed')"

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host ""

# Install pmdarima
Write-Host "Installing pmdarima..." -ForegroundColor Cyan
pip install pmdarima
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] pmdarima installed successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] pmdarima installation failed" -ForegroundColor Red
}

Write-Host ""

# Install prophet
Write-Host "Installing prophet..." -ForegroundColor Cyan
Write-Host "Note: This may take a few minutes and may require C++ build tools on Windows" -ForegroundColor Yellow
pip install prophet --only-binary :all:
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] prophet installed successfully" -ForegroundColor Green
} else {
    Write-Host "[WARNING] prophet installation may have failed" -ForegroundColor Yellow
    Write-Host "If it failed, you may need to install Visual C++ Build Tools" -ForegroundColor Yellow
    Write-Host "Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
python -c "try: from pmdarima import auto_arima; print('[OK] pmdarima import successful'); except ImportError as e: print('[ERROR] pmdarima import failed:', e)"
python -c "try: from prophet import Prophet; print('[OK] prophet import successful'); except ImportError as e: print('[ERROR] prophet import failed:', e)"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run the Epic 2 tests:" -ForegroundColor Green
Write-Host "  python examples\test_epic2_step2_baseline_models.py" -ForegroundColor White
Write-Host ""

