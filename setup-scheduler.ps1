# Run this script ONCE as Administrator to register both scheduled tasks.
# Right-click PowerShell -> "Run as administrator", then run this file.

$workDir   = $PSScriptRoot
$folderTag = (Split-Path $workDir -Leaf) -replace '\s+', '_'

# ── Task 1: Daily job search ──────────────────────────────────────────────────
$searchAction = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$workDir\run-job-search.ps1`""

$searchTrigger  = New-ScheduledTaskTrigger -Daily -At "08:15"
$searchSettings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -WakeToRun
$searchSettings.DisallowStartIfOnBatteries = $false
$searchSettings.StopIfGoingOnBatteries = $false

Register-ScheduledTask `
    -TaskName    "DailyJobSearch_$folderTag" `
    -Description "Runs Claude job-search-agent daily at 08:15 and emails results" `
    -Action      $searchAction `
    -Trigger     $searchTrigger `
    -Settings    $searchSettings `
    -RunLevel    Highest `
    -Force

Write-Host "Task 1 registered: DailyJobSearch_$folderTag (runs daily at 08:15)"

# ── Task 2: Hourly reply checker (starts at 09:00, repeats every hour) ────────
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) {
    Write-Warning "Python not found in PATH. Update the task action manually with the correct python path."
    $python = "python"
}

$replyAction = New-ScheduledTaskAction `
    -Execute $python `
    -Argument "`"$workDir\check-reply.py`"" `
    -WorkingDirectory $workDir

# Start at 09:00, repeat every 1 hour indefinitely
$replyTrigger = New-ScheduledTaskTrigger -Daily -At "09:00"
$replyTrigger.Repetition = (New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Hours 1) -Once -At "09:00").Repetition

$replySettings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)
$replySettings.DisallowStartIfOnBatteries = $false
$replySettings.StopIfGoingOnBatteries = $false

Register-ScheduledTask `
    -TaskName    "DailyJobReplyChecker_$folderTag" `
    -Description "Checks Gmail hourly starting 09:00 for reply to job search email and runs CV tailor agent" `
    -Action      $replyAction `
    -Trigger     $replyTrigger `
    -Settings    $replySettings `
    -RunLevel    Highest `
    -Force

Write-Host "Task 2 registered: DailyJobReplyChecker_$folderTag (runs every hour starting 09:00)"
Write-Host ""
Write-Host "Setup complete."
