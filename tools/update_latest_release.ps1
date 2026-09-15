$ErrorActionPreference = 'Stop'

$repo = 'JulienP36/settlers3-mapgen'
$apiUrl = "https://api.github.com/repos/$repo/releases/latest"
$root = Split-Path -Parent $PSScriptRoot
$updatesDir = Join-Path $root 'updates'

try {
    Write-Host 'Recherche de la derniere release STABLE sur GitHub...'
    $headers = @{
        'Accept' = 'application/vnd.github+json'
        'User-Agent' = 'Settlers3-MapGen-Updater'
        'X-GitHub-Api-Version' = '2022-11-28'
    }
    $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers

    if ($release.draft -or $release.prerelease) {
        throw "La release retournee n'est pas une release STABLE publiee."
    }

    $assets = @($release.assets | Where-Object {
        $_.name -match '^SETTLERS3_MAPGEN_.*\.zip$'
    })

    if ($assets.Count -eq 0) {
        throw 'Aucune archive SETTLERS3_MAPGEN_*.zip n''est attachee a cette release.'
    }

    # Prefer a STABLE archive if several ZIP assets are attached.
    $asset = $assets | Where-Object { $_.name -match '_STABLE_' } | Select-Object -First 1
    if ($null -eq $asset) {
        $asset = $assets | Select-Object -First 1
    }

    New-Item -ItemType Directory -Force -Path $updatesDir | Out-Null
    $destination = Join-Path $updatesDir $asset.name

    Write-Host ("Release : {0} - {1}" -f $release.tag_name, $release.name)
    Write-Host ("Archive : {0}" -f $asset.name)

    if (Test-Path $destination) {
        Write-Host 'Cette archive est deja presente dans updates\.'
        Write-Host ("Fichier : {0}" -f $destination)
        exit 0
    }

    Write-Host 'Telechargement...'
    Invoke-WebRequest -Uri $asset.browser_download_url -Headers @{ 'User-Agent' = 'Settlers3-MapGen-Updater' } -OutFile $destination

    if (-not (Test-Path $destination)) {
        throw 'Le telechargement ne semble pas avoir cree le fichier attendu.'
    }

    $sizeMiB = [Math]::Round((Get-Item $destination).Length / 1MB, 2)
    Write-Host ("OK : {0} MiB" -f $sizeMiB)
    Write-Host ("Enregistre dans : {0}" -f $destination)
    Write-Host ''
    Write-Host 'Aucune installation automatique n''a ete effectuee.'
    Write-Host 'L''installation actuelle reste intacte.'
    exit 0
}
catch {
    Write-Host ''
    Write-Host ("ERREUR : {0}" -f $_.Exception.Message) -ForegroundColor Red
    exit 1
}
