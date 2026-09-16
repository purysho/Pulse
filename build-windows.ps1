$ErrorActionPreference = "Stop"
py -m pip install --upgrade pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed --name Pulse pulse_desktop.pyw
Write-Host "Built dist\Pulse.exe"
