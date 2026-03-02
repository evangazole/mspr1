Set-Location "c:\Users\Evan\Documents\sujet mspr1\project"
Write-Host "Current dir: $(Get-Location)"
& "C:\Program Files\Git\bin\git.exe" checkout HEAD -- "data/processed/colonnes-mspr_AURA.csv"
Write-Host "Restored original file"
