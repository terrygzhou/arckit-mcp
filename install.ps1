# arckit-mcp one-line installer (Windows PowerShell)
#
#   irm https://raw.githubusercontent.com/terrygzhou/arckit-mcp/main/install.ps1 | iex
#
# What it does (idempotent — re-run to upgrade):
#   1. Preflight: Python >= 3.11 and git on PATH
#   2. Clone (or pull) the repo into $ARCKIT_MCP_HOME
#      (default: %LOCALAPPDATA%\arckit-mcp\repo)
#   3. Create a venv next to the checkout and pip install the package
#   4. Register the bundled agent skill at ~/.claude/skills/arckit-mcp-agent-loop
#   5. Print the MCP client registration JSON
#
# Environment overrides:
#   $env:ARCKIT_MCP_REPO   git URL of the repo (default: the public GitHub URL)
#   $env:ARCKIT_MCP_HOME   where the clone + venv live
#   $env:ARCKIT_MCP_DEV    set to "1" to also install the [dev] extra (arckit + pytest)
#   $env:ARCKIT_SKILL_DIR where to register the skill (default: ~/.claude/skills)

$ErrorActionPreference = "Stop"

$Repo = if ($env:ARCKIT_MCP_REPO) { $env:ARCKIT_MCP_REPO } else {
    "https://github.com/terrygzhou/arckit-mcp.git" }
$Dest = if ($env:ARCKIT_MCP_HOME) { $env:ARCKIT_MCP_HOME } else {
    (Join-Path $env:LOCALAPPDATA "arckit-mcp\repo") }
$Dev = $env:ARCKIT_MCP_DEV -eq "1"

function Fail([string]$msg) {
    Write-Error "arckit-mcp install: $msg"
    exit 1
}

# --- 1. Preflight -----------------------------------------------------------
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Fail "python not found - install Python >= 3.11 from python.org"
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "git not found - install git for Windows"
}

$pyver = & python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"
& python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) { Fail "python is $pyver - arckit-mcp requires Python >= 3.11" }
Write-Host "arckit-mcp: python $pyver"

# --- 2. Clone or update -----------------------------------------------------
if (Test-Path (Join-Path $Dest ".git")) {
    Write-Host "arckit-mcp: updating $Dest ..."
    git -C $Dest pull --ff-only
    if ($LASTEXITCODE -ne 0) { Fail "git pull failed" }
} else {
    Write-Host "arckit-mcp: cloning $Repo into $Dest ..."
    New-Item -ItemType Directory -Force -Path (Split-Path $Dest) | Out-Null
    git clone --depth 1 $Repo $Dest
    if ($LASTEXITCODE -ne 0) { Fail "git clone failed" }
}

# --- 3. Venv + install --------------------------------------------------------
$venvDir = Join-Path $Dest ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "arckit-mcp: creating venv at $venvDir ..."
    & python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) { Fail "python -m venv failed" }
}

$extra = if ($Dev) { "[dev]" } else { "" }
Write-Host "arckit-mcp: installing (this can take a minute) ..."
& $pythonExe -m pip install -q --upgrade pip
& $pythonExe -m pip install -q -e "$Dest$extra"
if ($LASTEXITCODE -ne 0) { Fail "pip install failed" }

$bin = Join-Path $venvDir "Scripts\arckit-mcp.exe"
if (-not (Test-Path $bin)) {
    Fail "install finished but $bin is missing"
}

# --- 4. Register the agent skill (best effort) --------------------------------
# Copies the bundled skill where Claude Code / agent harnesses discover
# skills (~/.claude/skills). Idempotent: re-running replaces the contents.
# Non-fatal: the MCP server works without the skill being registered.
$skillSrc = Join-Path $Dest "arckit_mcp\skill"
$skillName = "arckit-mcp-agent-loop"
$skillDestDir = if ($env:ARCKIT_SKILL_DIR) { $env:ARCKIT_SKILL_DIR } else {
    (Join-Path $env:USERPROFILE ".claude\skills") }
if (Test-Path (Join-Path $skillSrc "SKILL.md")) {
    $skillTarget = Join-Path $skillDestDir $skillName
    New-Item -ItemType Directory -Force -Path $skillTarget | Out-Null
    Copy-Item -Path (Join-Path $skillSrc "SKILL.md") -Destination $skillTarget -Force
    $refs = Join-Path $skillSrc "references"
    if (Test-Path $refs) {
        Copy-Item -Path $refs -Destination $skillTarget -Recurse -Force
    }
    Write-Host "arckit-mcp: skill registered at $skillTarget"
} else {
    Write-Host "arckit-mcp: warning: skill not found at $skillSrc - skipping skill registration"
}

# --- 5. Done -----------------------------------------------------------------
Write-Host ""
Write-Host "arckit-mcp installed"
Write-Host ""
Write-Host "MCP client registration (paste into your MCP client config):"
Write-Host "  {`"mcpServers`": {`"arckit`": {`"command`": `"$bin`"}}}"
Write-Host ""
Write-Host "Verify: $bin   (boots the stdio server; Ctrl-C to stop)"
Write-Host "Upgrade later: re-run the same one-liner."
if ($Dev) {
    Write-Host "Dev extras installed: run tests with $pythonExe -m pytest (Join-Path $Dest 'tests') -q"
}
