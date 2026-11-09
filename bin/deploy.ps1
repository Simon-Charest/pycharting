# bin/deploy.ps1
# Commits and pushes every change, then updates the server and restarts PyCharting there.
# Settings come from .env: DEPLOY_USER, DEPLOY_HOST, DEPLOY_DIR, DEPLOY_SERVICE, DEPLOY_REPOSITORY,
# and optionally DEPLOY_PORT (8000 by default) and DEPLOY_PASSWORD (the server's sudo password; asked for when absent).
# The database and .env are never in Git: copy them to the server by hand, once.
# At the end, a copy of the production database is kept in data/backups and replaces the local one.
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

    # 4. Bring back a copy of the production database: it is kept as a backup, and becomes the local one,
    #    so that development works on the same data. The server exports it while the site runs, still encrypted.
    $stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
    $remoteCopy = "data/backup-transfer.sqlite"
    $backup = "data/backups/database.$stamp.sqlite"
    $database = if ($settings.DATABASE_FILE) { $settings.DATABASE_FILE } else { "data/database.sqlite" }

    ssh $target "cd $dir && .venv/bin/python . backup $remoteCopy"

    if ($LASTEXITCODE -ne 0) { throw "Copying the production database on $($settings.DEPLOY_HOST) failed." }

    New-Item -ItemType Directory -Force (Split-Path $backup) | Out-Null
    scp -q "${target}:$dir/$remoteCopy" $backup

    if ($LASTEXITCODE -ne 0) { throw "Downloading the production database failed." }

    ssh $target "rm -f $dir/$remoteCopy"

    try {
        Copy-Item $backup $database -Force -ErrorAction Stop
        Write-Host "Production database saved to $backup and copied to $database."
    }
    catch {
        # A local server holding the database open can prevent the copy; the backup is safe either way
        Write-Warning "Production database saved to $backup, but $database could not be replaced: $($_.Exception.Message) Stop the local server, then copy it by hand."
    }
}
finally {
    Pop-Location
}
