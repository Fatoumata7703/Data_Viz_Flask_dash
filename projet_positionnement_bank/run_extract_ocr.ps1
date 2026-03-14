# Lance l'extraction PDF avec OCR depuis le dossier projet_positionnement_bank.
# Utilise le Python du venv ici (.venv) ou du parent (Flash_dash\.venv).

$ProjectDir = $PSScriptRoot
Set-Location $ProjectDir

$VenvHere = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$VenvParent = Join-Path (Split-Path $ProjectDir -Parent) ".venv\Scripts\python.exe"

if (Test-Path $VenvHere) {
    Write-Host "Python: $VenvHere"
    & $VenvHere -m scripts.extract_pdf_to_mongo @args
} elseif (Test-Path $VenvParent) {
    Write-Host "Python: $VenvParent (venv parent)"
    Write-Host "Pour --ocr, installez d'abord dans ce venv: & '$VenvParent' -m pip install pymupdf Pillow pytesseract"
    & $VenvParent -m scripts.extract_pdf_to_mongo @args
} else {
    Write-Host "Aucun .venv trouvé. Activez un venv puis: python -m scripts.extract_pdf_to_mongo --ocr"
    python -m scripts.extract_pdf_to_mongo @args
}
