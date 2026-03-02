Set-Location "C:\Users\Evan\Documents\sujet mspr1\project"
Write-Host "Committing cleanup..."
& "C:\Program Files\Git\bin\git.exe" add -A
& "C:\Program Files\Git\bin\git.exe" commit -m "Cleanup: Remove deprecated/debug scripts - keep only production ETL scripts"
& "C:\Program Files\Git\bin\git.exe" push origin main
Write-Host "Cleanup committed and pushed"
