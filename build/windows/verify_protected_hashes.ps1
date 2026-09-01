$ErrorActionPreference = 'Stop'
$Expected = @{
    's3mapgen/generation/base.py' = 'b2df5cc0329be2e63ba27b06501a5661547ce23f2b2ea739d3ec23de497bce88'
    's3mapgen/generation/continental.py' = '29d2413a742e4b5f446fed0cb4eed5b362b1ead431632d4a0397c3f4ea32c4d2'
    's3mapgen/generation/validated.py' = 'cabcc24fc8a5eac99d2a9a9a5009d41addc1cc49d05815d2d3567e105f8277c5'
    'config/upgraded_768_v1.json' = '11a4feba38372a63d6dd32959d7578377ffc6da82a0e33fd918d597b15a5b441'
    'data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz' = 'fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d'
}

foreach ($Path in $Expected.Keys) {
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected[$Path]) {
        throw "Protected hash mismatch: $Path ($Actual)"
    }
}
Write-Host 'Upgraded compatibility hashes PASS 5/5'
