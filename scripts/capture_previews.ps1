$ErrorActionPreference = "Stop"
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) { $chrome = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" }
$out = Split-Path -Parent $PSScriptRoot   # scripts/ -> repo root
$deck = Join-Path $out "examples\pitchcraft-demo\output\deck.html"
$prev = Join-Path $out "examples\pitchcraft-demo\output\preview"
New-Item -ItemType Directory -Force -Path $prev | Out-Null
$json = Get-Content (Join-Path $out "examples\pitchcraft-demo\output\deck.json") -Raw | ConvertFrom-Json
$total = $json.slides.Count
for ($i = 1; $i -le $total; $i++) {
  $n = "{0:D2}" -f $i
  $shot = Join-Path $prev "slide-$n.png"
  $url = "file:///" + ($deck -replace "\\", "/") + "#" + $i
  $udd = "$env:TEMP\pitchcraft-headless"
  $argline = "--headless=new --disable-gpu --no-first-run --user-data-dir=`"$udd`" --window-size=1280,720 --hide-scrollbars --screenshot=`"$shot`" `"$url`""
  Start-Process -FilePath $chrome -ArgumentList $argline -Wait -NoNewWindow | Out-Null
  Write-Host "captured slide-$n"
}
Write-Host ("previews: " + (Get-ChildItem $prev).Count)
