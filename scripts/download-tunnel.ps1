$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$projectRoot = Split-Path -Parent $PSScriptRoot
$dependenciesPath = Join-Path $projectRoot "dependencies"
$tunnelclientPath = Join-Path $projectRoot "dependencies" "openai-tunnel-client"
$archivePath = Join-Path $dependenciesPath "tunnel-client-runtime-cloudflared-v0.0.13-windows-amd64.zip"
$downloadUrl = "https://github.com/openai/tunnel-client/releases/download/v0.0.13/tunnel-client-runtime-cloudflared-v0.0.13-windows-amd64.zip"

New-Item -ItemType Directory -Path $dependenciesPath -Force | Out-Null
Invoke-WebRequest -Uri $downloadUrl -OutFile $archivePath
Expand-Archive -LiteralPath $archivePath -DestinationPath $tunnelclientPath -Force
