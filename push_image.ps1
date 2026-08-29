# 把 coding-evoagent 构建并推送到 Docker Hub
# 用法（先在本机执行 `docker login`）：
#   .\push_image.ps1 -User yourdockerhubuser -Tag latest
param(
    [string]$User = "yourdockerhubuser",
    [string]$Tag  = "latest"
)

$ErrorActionPreference = "Stop"
$image = "$User/coding-evoagent"

Write-Host "==> docker build -t $image`:$Tag ."
docker build -t "$image`:$Tag" .

Write-Host "==> docker push $image`:$Tag"
docker push "$image`:$Tag"

Write-Host ""
Write-Host "完成。VPS 上请把 .env.prod 里的 EVOAGENT_IMAGE 设为： $image`:$Tag"

