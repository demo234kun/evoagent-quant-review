$base = "http://127.0.0.1:18080"

function Probe($path, $method="GET", $body=$null, $token=$null) {
    $url = $base + $path
    $h = @{}
    if ($token) { $h["Authorization"] = "Bearer $token" }
    if ($body) { $h["Content-Type"] = "application/json" }
    try {
        if ($method -eq "POST") {
            $resp = Invoke-WebRequest -Uri $url -Method $method -Headers $h -Body $body -TimeoutSec 150 -UseBasicParsing
        } else {
            $resp = Invoke-WebRequest -Uri $url -Method $method -Headers $h -TimeoutSec 30 -UseBasicParsing
        }
        $status = [int]$resp.StatusCode
        $text = $resp.Content
    } catch {
        $resp = $_.Exception.Response
        $status = if ($resp) { [int]$resp.StatusCode } else { 0 }
        $text = if ($resp) { try { (New-Object System.IO.StreamReader($resp.GetResponseStream())).ReadToEnd() } catch { "" } } else { $_.Exception.Message }
    }
    return [PSCustomObject]@{status=$status; text=$text}
}

Write-Host "=== 0. browser/render tool availability ==="
$browser = (Get-Command chromium-browser -ErrorAction SilentlyContinue) -or (Get-Command google-chrome -ErrorAction SilentlyContinue) -or (Get-Command chrome -ErrorAction SilentlyContinue)
try { $pw = (python -c "import playwright; print('ok')" 2>$null) } catch { $pw = $null }
Write-Host ("  headless browser: " + $(if ($browser) { "found" } else { "NOT available" }))
Write-Host ("  playwright(py): " + $(if ($pw) { "found" } else { "NOT available" }))

Write-Host "=== 1. page + assets ==="
$h = Probe "/"
Write-Host ("  GET /                  -> " + $h.status + "  bank-nav=" + $h.text.Contains('data-view="bank"') + "  view-bank=" + $h.text.Contains('id="view-bank"'))
$c = Probe "/assets/app.css"
Write-Host ("  GET /assets/app.css    -> " + $c.status + "  .stats-grid=" + $c.text.Contains('.stats-grid'))
$j = Probe "/assets/app.js"
Write-Host ("  GET /assets/app.js     -> " + $j.status + "  loadBank=" + $j.text.Contains('function loadBank') + "  dispatch=" + $j.text.Contains('if (view === "bank") loadBank();'))

Write-Host "=== 2. login ==="
$l = Probe "/v1/auth/login" "POST" '{"username":"admin","password":"evoagent-local-admin"}'
$token = ($l.text | ConvertFrom-Json).access_token
Write-Host ("  POST /v1/auth/login    -> " + $l.status + "  token_len=" + $token.Length)

Write-Host "=== 3. every endpoint each tab calls ==="
$d = Probe "/api/dashboard" "GET" $null $token
Write-Host ("  GET /api/dashboard     -> " + $d.status)
$t = Probe "/api/tasks" "GET" $null $token
Write-Host ("  GET /api/tasks         -> " + $t.status)
$s = Probe "/api/skills" "GET" $null $token
Write-Host ("  GET /api/skills        -> " + $s.status)
$e = Probe "/v1/evolution/status" "GET" $null $token
Write-Host ("  GET /v1/evolution/status-> " + $e.status)
$b = Probe "/v1/findings-bank?limit=1" "GET" $null $token
$before = ($b.text | ConvertFrom-Json).stats
Write-Host ("  GET /v1/findings-bank  -> " + $b.status + "  total=" + $before.total + "  strategies_scanned=" + $before.strategies_scanned + "  rules=" + $before.by_rule.Count)

Write-Host "=== 4. LIVE review through web API -> must ingest into bank ==="
$diff = @"
diff --git a/test_strategy.py b/test_strategy.py
new file mode 100644
--- /dev/null
+++ b/test_strategy.py
@@ -0,0 +1,3 @@
+import jqdata
+print("debug info")
+order_target("000001.XSHE", 1)
"@
$body = @{repository="quant/web-test"; diff=$diff; mode="rules-only"} | ConvertTo-Json -Compress
$r = Probe "/v1/reviews" "POST" $body $token
$rj = $r.text | ConvertFrom-Json
$nf = ($rj.report.findings | Measure-Object).Count
Write-Host ("  POST /v1/reviews       -> " + $r.status + "  new_findings=" + $nf)

Start-Sleep -Seconds 1
$b2 = Probe "/v1/findings-bank?limit=1" "GET" $null $token
$after = ($b2.text | ConvertFrom-Json).stats
Write-Host ("  GET /v1/findings-bank  -> " + $b2.status + "  total=" + $after.total + " (was " + $before.total + ")  strategies_scanned=" + $after.strategies_scanned)

Write-Host "=== SUMMARY ==="
$ok = ($h.status -eq 200 -and $c.status -eq 200 -and $j.status -eq 200 -and $l.status -eq 200 -and $d.status -eq 200 -and $t.status -eq 200 -and $s.status -eq 200 -and $e.status -eq 200 -and $b.status -eq 200 -and $r.status -eq 201 -and $b2.status -eq 200 -and $after.total -gt $before.total)
Write-Host ("  ALL GREEN: " + $ok)

