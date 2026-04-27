param(
    [string]$RepoName = "missional-youtube-insight",
    [string]$Description = "Streamlit app for missional YouTube insight analysis",
    [ValidateSet("public", "private")]
    [string]$Visibility = "public"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI(gh)가 설치되어 있지 않습니다. https://cli.github.com/ 에서 설치한 뒤 다시 실행하세요."
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git이 설치되어 있지 않습니다."
}

gh auth status | Out-Null

$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    git branch -M main
}

$repoExists = $false
try {
    gh repo view $RepoName | Out-Null
    $repoExists = $true
} catch {
    $repoExists = $false
}

if (-not $repoExists) {
    $visibilityFlag = "--$Visibility"
    gh repo create $RepoName --source . --remote origin --description $Description $visibilityFlag
} elseif (-not (git remote get-url origin 2>$null)) {
    $owner = gh api user --jq .login
    git remote add origin "https://github.com/$owner/$RepoName.git"
}

git push -u origin main

$repoUrl = gh repo view --json url --jq .url
Write-Host ""
Write-Host "GitHub 저장 완료: $repoUrl"
Write-Host "Streamlit Community Cloud 연결: https://share.streamlit.io/"
Write-Host "Main file path에는 streamlit_app.py를 지정하세요."
