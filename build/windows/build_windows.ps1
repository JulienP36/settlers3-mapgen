param(
    [switch]$InstallDependencies
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$DistRoot = Join-Path $ProjectRoot 'dist\Settlers3MapGen'
$WorkRoot = Join-Path $ProjectRoot 'build\windows\work'
$ArtifactRoot = Join-Path $ProjectRoot 'artifacts'

Set-Location $ProjectRoot

$AppVersion = python -c "from s3mapgen.version import APP_VERSION; print(APP_VERSION)"
if ($LASTEXITCODE -ne 0) { throw 'Could not read the application version.' }
$ArtifactVersion = $AppVersion -replace '[^A-Za-z0-9]+', '_'
$ArtifactStem = "SETTLERS3_MAPGEN_V$ArtifactVersion`_WINDOWS_X64"
$ZipPath = Join-Path $ArtifactRoot ($ArtifactStem + '.zip')
$ReportPath = Join-Path $ArtifactRoot ($ArtifactStem + '_SELFTEST.json')

if ($InstallDependencies) {
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt -r build\windows\requirements-build.txt
}

python build\windows\generate_version_info.py
if ($LASTEXITCODE -ne 0) { throw 'Windows version metadata generation failed.' }

if (Test-Path $DistRoot) { Remove-Item -LiteralPath $DistRoot -Recurse -Force }
if (Test-Path $WorkRoot) { Remove-Item -LiteralPath $WorkRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path $ArtifactRoot | Out-Null
if (Test-Path $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }
if (Test-Path $ReportPath) { Remove-Item -LiteralPath $ReportPath -Force }

python -m PyInstaller --noconfirm --clean `
    --distpath (Join-Path $ProjectRoot 'dist') `
    --workpath $WorkRoot `
    build\windows\settlers3_mapgen.spec
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed.' }

Copy-Item -LiteralPath build\windows\README_FIRST.txt -Destination $DistRoot
$env:S3MAPGEN_SELFTEST_REPORT = $ReportPath
$SelfTest = Start-Process -FilePath (Join-Path $DistRoot 'Settlers3MapGen.exe') `
    -ArgumentList '--self-test' -Wait -PassThru
if ($SelfTest.ExitCode -ne 0) { throw "Packaged executable self-test failed with exit code $($SelfTest.ExitCode)." }

$Report = Get-Content -LiteralPath $ReportPath -Raw | ConvertFrom-Json
if ($Report.status -ne 'PASS' -or -not $Report.frozen) {
    throw 'Packaged executable did not validate as a frozen runtime.'
}

Compress-Archive -Path $DistRoot -DestinationPath $ZipPath -CompressionLevel Optimal
$Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZipPath).Hash
Set-Content -LiteralPath ($ZipPath + '.sha256') -Value ($Hash + '  ' + (Split-Path $ZipPath -Leaf)) -Encoding ascii
Write-Host "Created $ZipPath"
Write-Host "SHA-256 $Hash"
