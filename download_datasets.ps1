# Script de telechargement des datasets MSPR1
$DownloadDir = "C:\Users\Evan\Documents\sujet mspr1\project\data\raw"

if (-Not (Test-Path $DownloadDir)) {
    New-Item -ItemType Directory -Path $DownloadDir | Out-Null
}

Write-Host "Telechargement datasets MSPR1..." -ForegroundColor Cyan

$Files = @{
    "insee_population_2022.zip" = "https://www.insee.fr/fr/statistiques/fichier/8647014/base-ic-evol-struct-pop-2022_csv.zip"
    "insee_diplomes_2022.zip" = "https://www.insee.fr/fr/statistiques/fichier/8647010/base-ic-diplomes-formation-2022_csv.zip"
    "insee_rpls_2024.zip" = "https://www.insee.fr/fr/statistiques/fichier/8736658/RPLS_01-01-2024_Iris.zip"
    "delits_cambriolages.csv" = "https://www.data.gouv.fr/api/1/datasets/r/2b27a675-e3bf-41ef-a852-5fb9ab483967"
    "elections_2022_2017.csv" = "https://www.data.gouv.fr/api/1/datasets/r/b8703c69-a18f-46ab-9e7f-3a8368dcb891"
}

$Downloaded = 0
$FileCount = $Files.Count

foreach ($FileName in $Files.Keys) {
    $FilePath = "$DownloadDir\$FileName"
    $Url = $Files[$FileName]
    
    Write-Host "[$($Downloaded + 1)/$FileCount] $FileName..." -ForegroundColor Yellow
    
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $FilePath -TimeoutSec 60
        $Size = [math]::Round((Get-Item $FilePath).Length / 1MB, 2)
        Write-Host "[OK] Telechargement OK - $Size MB" -ForegroundColor Green
        $Downloaded++
    } catch {
        Write-Host "[ERROR] Erreur de telechargement" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Resultat: $Downloaded/$FileCount fichiers telecharges" -ForegroundColor Cyan
