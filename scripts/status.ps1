$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
Write-Host "Docker services" -ForegroundColor Cyan
docker compose ps
foreach ($item in @(
    @{Name='Frontend'; Port=3000; Url='http://127.0.0.1:3000'},
    @{Name='Backend'; Port=8000; Url='http://127.0.0.1:8000/health'},
    @{Name='PostgreSQL'; Port=5433; Url=$null},
    @{Name='Ollama'; Port=11434; Url='http://127.0.0.1:11434/api/tags'}
)) {
    $open = Test-NetConnection 127.0.0.1 -Port $item.Port -InformationLevel Quiet -WarningAction SilentlyContinue
    $color = if ($open) { 'Green' } else { 'Yellow' }
    Write-Host ("[{0}] {1} port {2}" -f $(if($open){'UP'}else{'DOWN'}), $item.Name, $item.Port) -ForegroundColor $color
}
