$logos = @{
    'python' = 'https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg'
    'powershell' = 'https://raw.githubusercontent.com/devicons/devicon/master/icons/powershell/powershell-original.svg'
    'pytest' = 'https://raw.githubusercontent.com/devicons/devicon/master/icons/pytest/pytest-original.svg'
    'git' = 'https://raw.githubusercontent.com/devicons/devicon/master/icons/git/git-original.svg'
    'windows' = 'https://raw.githubusercontent.com/devicons/devicon/master/icons/windows11/windows11-original.svg'
}

$outDir = Split-Path -Parent $MyInvocation.MyCommand.Path

foreach ($name in $logos.Keys) {
    $url = $logos[$name]
    $ext = if ($url -match '\.svg$') { 'svg' } else { 'png' }
    $outFile = Join-Path $outDir ($name + '.' + $ext)
    try {
        Invoke-WebRequest -Uri $url -OutFile $outFile -UseBasicParsing -TimeoutSec 15
        $size = (Get-Item $outFile).Length
        Write-Host "OK: $name -> $size bytes"
    } catch {
        Write-Host "FAIL: $name -> $($_.Exception.Message)"
    }
}

Write-Host "Done downloading logos"
