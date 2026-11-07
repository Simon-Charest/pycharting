# pycharting\bin\pycharting.ps1
# Run the PyCharting Web API from any directory.
$ErrorActionPreference = "Stop"
Push-Location (Join-Path $PSScriptRoot "..\..")

try {
    & ".venv\Scripts\python.exe" pycharting --api
}
finally {
    Pop-Location
}
