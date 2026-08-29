$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$projectRoot = Split-Path -Parent $PSScriptRoot
$distPath = Join-Path $projectRoot "dist"

uv build $projectRoot --wheel --out-dir $distPath --clear
Copy-Item -LiteralPath (Join-Path $projectRoot "requirements.txt") -Destination $distPath
