# Build a standalone coding-agent.exe.
# Output: dist\coding-agent.exe

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python -m pip install -e ".[dev]" "pyinstaller>=6.0" | Out-Host

$Spec = Join-Path $Root "packaging\coding-agent.spec"
python -m PyInstaller --noconfirm --clean --distpath dist --workpath build\pyinstaller $Spec

Write-Host ""
Write-Host "Built: $(Join-Path $Root 'dist\coding-agent.exe')"
Write-Host "Copy that file to another Windows machine (same CPU arch)."
Write-Host "Still required on the other machine: OPENAI_API_KEY (or --api-key) and network access to the LLM API."
