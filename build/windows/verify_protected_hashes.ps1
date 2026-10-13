$ErrorActionPreference = 'Stop'
$Expected = @{
    'config/legacy_768_v1.json' = 'bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85'
    'data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz' = 'fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d'
}

foreach ($Path in $Expected.Keys) {
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected[$Path]) {
        throw "Protected hash mismatch: $Path ($Actual)"
    }
}
Write-Host 'Protected compatibility hashes PASS 2/2'
