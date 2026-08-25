$ErrorActionPreference = 'Stop'
$Expected = @{
    's3mapgen/generator_v15.py' = '3bbc9180719ebfae2bc37b29d81025731dc821e861c7b0e66894f7460f296090'
    's3mapgen/generator.py' = '1b73f2536c6db75dfb3856a1667d0b619d3462d9c0efa14f406c78a05556be77'
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
