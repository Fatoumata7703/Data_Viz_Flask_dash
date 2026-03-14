# Active le .venv a la racine (Flash_dash) et installe requirements.txt
Set-Location $PSScriptRoot
Write-Host "Activation du venv..."
& .\.venv\Scripts\Activate.ps1
Write-Host "Installation des dependances (requirements.txt)..."
pip install -r requirements.txt
Write-Host ""
Write-Host "Termine. Vous pouvez lancer vos scripts avec: python ..."
