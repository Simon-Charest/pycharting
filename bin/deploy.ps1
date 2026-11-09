# bin/deploy.ps1
# Commits and pushes every change, then updates the server and restarts PyCharting there.
# Settings come from .env: DEPLOY_USER, DEPLOY_HOST, DEPLOY_DIR, DEPLOY_SERVICE, DEPLOY_REPOSITORY,
# and optionally DEPLOY_PORT (8000 by default) and DEPLOY_PASSWORD (the server's sudo password; asked for when absent).
# The database and .env are never in Git: copy them to the server by hand, once.
$ErrorActionPreference = "Stop"
Push-Location (Split-Path $PSScriptRoot -Parent)

try {
    $settings = @{}

    foreach ($line in Get-Content .env) {
        if ($line -match '^\s*([A-Z_]+)\s*=\s*(.*)$') {
            $settings[$Matches[1]] = $Matches[2].Trim()
        }
    }

    foreach ($name in "DEPLOY_USER", "DEPLOY_HOST", "DEPLOY_DIR", "DEPLOY_SERVICE", "DEPLOY_REPOSITORY") {
        if (-not $settings[$name]) {
            throw "$name must be set in .env."
        }
    }

    $target = "$($settings.DEPLOY_USER)@$($settings.DEPLOY_HOST)"
    $dir = $settings.DEPLOY_DIR
    $port = if ($settings.DEPLOY_PORT) { $settings.DEPLOY_PORT } else { "8000" }

    # 1. Commit and push everything that changed; .gitignore keeps .env and the database out
    git add -A
    git diff --cached --quiet

    if ($LASTEXITCODE -ne 0) {
        git commit -m "Automated deploy"

        if ($LASTEXITCODE -ne 0) { throw "git commit failed." }
    }
    else {
        Write-Host "Nothing new to commit."
    }

    git push

    if ($LASTEXITCODE -ne 0) { throw "git push failed." }

    # 2. Clone the repository on the server, or bring it up to date
    ssh $target "if [ -d $dir/.git ]; then git -C $dir pull --ff-only; else git clone $($settings.DEPLOY_REPOSITORY) $dir; fi"

    if ($LASTEXITCODE -ne 0) { throw "Updating $dir on $($settings.DEPLOY_HOST) failed." }

    # 3. Install and restart the service. The sudo password goes through SSH's input, never on a command line;
    #    without it, -t lets sudo ask for it
    $command = "bash $dir/bin/server-deploy.sh $($settings.DEPLOY_SERVICE) $port"

    if ($settings.DEPLOY_PASSWORD) {
        $settings.DEPLOY_PASSWORD | ssh $target $command
    }
    else {
        ssh -t $target $command
    }

    if ($LASTEXITCODE -ne 0) { throw "Starting $($settings.DEPLOY_SERVICE) on $($settings.DEPLOY_HOST) failed." }

    Write-Host "Deployed. Public address: https://pycharting.slcti.ca"
}
finally {
    Pop-Location
}
