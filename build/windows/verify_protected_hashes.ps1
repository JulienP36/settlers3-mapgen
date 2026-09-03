$ErrorActionPreference = 'Stop'
$Expected = @{
    'config/legacy_768_v1.json' = 'bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85'
    'config/upgraded_768_v1.json' = 'bbd4be69dd27fa98ebd873a8a4ae1261e7b44539617072bd3c28bab837282ff3'
    'data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz' = 'fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d'
}

foreach ($Path in $Expected.Keys) {
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected[$Path]) {
        throw "Protected hash mismatch: $Path ($Actual)"
    }
}
Write-Host 'Protected compatibility hashes PASS 3/3'
