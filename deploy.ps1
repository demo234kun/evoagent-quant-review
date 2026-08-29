<#
.SYNOPSIS
  一键部署 coding-evoagent 到 VPS：构建镜像 -> 推 Docker Hub -> SSH 拉起 -> 自动健康检查
.DESCRIPTION
  前置条件：
    - 本机已 `docker login`（Docker Hub）
    - VPS 上已存在部署目录里的 .env.prod（含密钥与 EVOAGENT_IMAGE），本脚本不管理密钥
    - 本机有 OpenSSH 客户端（Win10+ 自带 ssh/scp）
  本脚本只做：重新构建并推送镜像、同步 docker-compose.prod.yml 与 Caddyfile、
  在 VPS 上 pull+up、最后自动探测 https://localhost/health。
.PARAMETER User      Docker Hub 用户名（必填）
.PARAMETER VPSHost   VPS 地址，IP 或域名（必填）
.PARAMETER VPSUser   VPS SSH 用户名（默认 root）
.PARAMETER SSHKey    SSH 私钥路径（无密码登录时需要）
.PARAMETER Tag       镜像 tag（默认 latest）
.PARAMETER RemoteDir VPS 上部署目录（默认 ~/evoagent）
.EXAMPLE
  .\deploy.ps1 -User myhub -VPSHost 1.2.3.4 -SSHKey C:\keys\vps.pem
#>
param(
    [Parameter(Mandatory = $true)]  [string]$User,
    [Parameter(Mandatory = $true)]  [string]$VPSHost,
    [string]$VPSUser   = "root",
    [string]$SSHKey    = "",
    [string]$Tag       = "latest",
    [string]$RemoteDir = "~/evoagent"
)

$ErrorActionPreference = "Stop"
$image  = "$User/coding-evoagent"
$sshOpt = @()
if ($SSHKey) { $sshOpt += "-i"; $sshOpt += $SSHKey }

function RunSSH($cmd) {
    & ssh @sshOpt "${VPSUser}@${VPSHost}" $cmd
    if ($LASTEXITCODE -ne 0) { throw "SSH 命令失败: $cmd" }
}

Write-Host "==> [1/5] 构建镜像 $($image):$Tag"
docker build -t "$($image):$Tag" .
if ($LASTEXITCODE -ne 0) { throw "docker build 失败" }

Write-Host "==> [2/5] 推送镜像到 Docker Hub"
docker push "$($image):$Tag"
if ($LASTEXITCODE -ne 0) { throw "docker push 失败（确认已 docker login 且 User 正确）" }

Write-Host "==> [3/5] 同步配置到 VPS $RemoteDir"
& ssh @sshOpt "${VPSUser}@${VPSHost}" "mkdir -p $RemoteDir"
if ($LASTEXITCODE -ne 0) { throw "无法 SSH 到 VPS（检查地址 / 密钥 / 22 端口是否开放）" }
& scp @sshOpt docker-compose.prod.yml Caddyfile "${VPSUser}@${VPSHost}:${RemoteDir}/"
if ($LASTEXITCODE -ne 0) { throw "scp 配置失败" }

Write-Host "==> [4/5] VPS 上拉取并启动"
RunSSH "cd $RemoteDir && docker compose --env-file .env.prod -f docker-compose.prod.yml pull"
RunSSH "cd $RemoteDir && docker compose --env-file .env.prod -f docker-compose.prod.yml up -d"

Write-Host "==> [5/5] 自动健康检查（最多重试 50s）"
$ok = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $r = RunSSH "curl -k -fsS https://localhost/health" 2>$null
        if ($r -match "ok") { $ok = $true; break }
    }
    catch { }
    Start-Sleep -Seconds 5
}
if (-not $ok) { throw "健康检查未通过：连续 10 次未从 https://localhost/health 拿到 ok" }

Write-Host ""
Write-Host "部署完成且健康检查通过。打开 https://$VPSHost/ 登录管理台。"

