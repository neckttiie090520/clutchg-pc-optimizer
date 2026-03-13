# ClutchG Setup and Test Script
# สคริปต์ติดตั้งและทดสอบ ClutchG App

$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green @args }
function Write-Error { Write-ColorOutput Red @args }
function Write-Warning { Write-ColorOutput Yellow @args }
function Write-Info { Write-ColorOutput Cyan @args }

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$SRC_DIR = Join-Path $SCRIPT_DIR "src"

Write-Info "="*60
Write-Info "ClutchG Setup and Test Script"
Write-Info "="*60
Write-Output ""

# Step 1: Check Python
Write-Info "Step 1: Checking Python..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "✓ Python found: $pythonVersion"
} catch {
    Write-Error "✗ Python not found! Please install Python 3.11+ first."
    exit 1
}
Write-Output ""

# Step 2: Install Dependencies
Write-Info "Step 2: Installing dependencies..."
Write-Output "Running: pip install -r requirements.txt"
try {
    pip install -r requirements.txt
    Write-Success "✓ Dependencies installed successfully"
} catch {
    Write-Error "✗ Failed to install dependencies"
    Write-Warning "Try running manually: pip install -r requirements.txt"
}
Write-Output ""

# Step 3: Test Imports
Write-Info "Step 3: Testing imports..."
try {
    python "$SRC_DIR\test_imports.py"
    Write-Success "✓ All imports successful"
} catch {
    Write-Error "✗ Import test failed"
    exit 1
}
Write-Output ""

# Step 4: Test App Initialization
Write-Info "Step 4: Testing app initialization..."
try {
    python "$SRC_DIR\test_app_init.py"
    Write-Success "✓ App initialization successful"
} catch {
    Write-Error "✗ App initialization failed"
    exit 1
}
Write-Output ""

# Step 5: Launch App
Write-Info "Step 5: Launching ClutchG App..."
Write-Warning "Press Ctrl+C to stop the app"
Write-Output ""

try {
    python "$SRC_DIR\app_minimal.py"
} catch {
    Write-Error "✗ App launch failed"
    Write-Output ""
    Write-Info "For debugging, try:"
    Write-Output "1. cd $SRC_DIR"
    Write-Output "2. python app_minimal.py"
    Write-Output ""
    Write-Info "And check the error message carefully"
    exit 1
}

Write-Output ""
Write-Success "="*60
Write-Success "ClutchG ran successfully!"
Write-Success "="*60
