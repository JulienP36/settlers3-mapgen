$ErrorActionPreference = 'Stop'
$Expected = @{
    's3mapgen/generation/base.py' = '5d828abe18c8b84f9845221f588eb8e6583fad99955465ce940cc09ce914ee4b'
    's3mapgen/generation/continental.py' = '57cb7ce7c45a05906ef60b2d9b1c4306fae40a26c60fa93cde2e481823976e86'
    'config/legacy_768_v1.json' = 'bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85'
    'config/upgraded_768_v1.json' = '11a4feba38372a63d6dd32959d7578377ffc6da82a0e33fd918d597b15a5b441'
    'data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz' = 'fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d'
}

foreach ($Path in $Expected.Keys) {
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected[$Path]) {
        throw "Protected hash mismatch: $Path ($Actual)"
    }
}
Write-Host 'Protected hashes PASS 5/5'
