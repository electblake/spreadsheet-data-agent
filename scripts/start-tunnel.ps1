$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$projectRoot = Split-Path -Parent $PSScriptRoot
$tunnelClientPath = Join-Path $projectRoot "dependencies" "openai-tunnel-client" "tunnel-client-runtime-cloudflared.exe"
$tunnelId = "tunnel_6a9322f737d08191919fbc67b920e63b"
$mcpCommand = "uv run python -m spreadsheet_data_agent.mcp.server"

& $tunnelClientPath run `
    --cloudflared.managed `
    --control-plane.tunnel-id $tunnelId `
    --mcp.command $mcpCommand
