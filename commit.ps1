Set-Location "C:\Users\Evan\Documents\sujet mspr1\project"
Write-Host "Committing changes..."
& "C:\Program Files\Git\bin\git.exe" add -A
& "C:\Program Files\Git\bin\git.exe" commit -m "Feature: Add median income indicator (revenus_median_today) to AURA master - 3,441/4,094 communes enriched with income data"
& "C:\Program Files\Git\bin\git.exe" push origin main
Write-Host "Changes pushed to GitHub"
