<#
test comment
#>param([string]$x)
function RunSSH($cmd){ & echo $cmd }
Write-Host $x
