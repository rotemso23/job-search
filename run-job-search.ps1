# Daily Job Search Runner
# Runs the job-search-agent via Claude Code CLI and sends results by email.

$userHome = $env:USERPROFILE
$env:PATH = "$userHome\.local\bin;" + $env:PATH

$workDir  = $PSScriptRoot
$date     = Get-Date -Format "yyyy-MM-dd"
$logFile  = "$workDir\job-results\${date}_search.md"
$debugLog = "$workDir\job-results\${date}_debug.log"

$configFile = "$workDir\config.ini"
$emailAddr  = (Select-String -Path $configFile -Pattern '^\s*email\s*=\s*(.+)$').Matches[0].Groups[1].Value.Trim()
$from       = $emailAddr
$to         = $emailAddr
$subject  = "Daily Job Search Results - $date"

Set-Location $workDir

New-Item -ItemType Directory -Force -Path "$workDir\job-results" | Out-Null

# -- 1. Run the job-search-agent ----------------------------------------------
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starting job-search-agent..."

# Allow claude to run even if a Claude Code session is already open
Remove-Item Env:\CLAUDECODE -ErrorAction SilentlyContinue


$prompt = @"
Run the job-search-agent for today's daily job search.
Today is $date.
Follow the full job-search-strategy playbook (all phases).
Save results to job-results/${date}_search.md and append all new jobs to the Excel tracker.
"@

$timeoutSeconds = 900  # 15 minutes
$currentPid = $PID

# Watchdog: kills only the claude process spawned by this script (not all claude processes)
$watchdog = [System.Threading.Timer]::new({
    param($state)
    $searcher = New-Object System.Management.ManagementObjectSearcher(
        "SELECT ProcessId FROM Win32_Process WHERE ParentProcessId = $state")
    foreach ($proc in $searcher.Get()) {
        & taskkill /F /T /PID ([int]$proc["ProcessId"]) 2>$null
    }
    "[TIMEOUT] Agent killed after $timeoutSeconds seconds." |
        Out-File -Append -FilePath $debugLog -Encoding UTF8
}, $currentPid, ($timeoutSeconds * 1000), [System.Threading.Timeout]::Infinite)

$writer = [System.IO.StreamWriter]::new($debugLog, $true, [System.Text.Encoding]::UTF8)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
try {
    & claude --dangerously-skip-permissions -p $prompt --output-format stream-json --verbose 2>&1 | ForEach-Object {
        $line = $_
        try {
            $obj = $line | ConvertFrom-Json
            # final result
            if ($obj.type -eq "result" -and $obj.result) {
                $writer.WriteLine($obj.result); $writer.Flush()
            }
            # intermediate assistant text
            $text = $obj.message.content | Where-Object { $_.type -eq "text" } | Select-Object -ExpandProperty text
            if ($text) { $writer.WriteLine($text); $writer.Flush() }
            # tool calls
            $tools = $obj.message.content | Where-Object { $_.type -eq "tool_use" }
            foreach ($tool in $tools) {
                $toolInput = $tool.input | ConvertTo-Json -Compress
                $writer.WriteLine("[TOOL] $($tool.name): $toolInput"); $writer.Flush()
            }
        } catch {
            $writer.WriteLine("[RAW] $line"); $writer.Flush()
        }
    }
} finally {
    $watchdog.Dispose()
    $writer.Close()
}

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Agent finished."

# -- 2. Read results file -----------------------------------------------------
if (Test-Path $logFile) {
    $body = Get-Content $logFile -Raw -Encoding UTF8
} else {
    $body = "Job search completed but results file was not found at:`n$logFile"
}

# -- 3. Build numbered quick-apply header -------------------------------------
$jobs = @()
$counter = 0
$body = ($body -split "`n" | ForEach-Object {
    if ($_ -match '^### (.+)$') {
        $title = $Matches[1].Trim()
        if ($title -notmatch '^Job \d+ of \d+$') {
            $counter++
            $jobs += $title
            "### $counter. $title"
        } else { $_ }
    } else { $_ }
}) -join "`n"

$jobList = ""
for ($i = 0; $i -lt $jobs.Count; $i++) {
    $jobList += "  $($i+1). $($jobs[$i])`n"
}

$header = @"
QUICK APPLY
-----------
Reply to this email with the numbers of jobs you want CV-tailored.
Example reply: "1, 3"

$jobList
-------------------------------------------

"@

$emailBody = $header + $body

# -- 4. Send email via Gmail SMTP ---------------------------------------------
$secretPath  = "$workDir\.credentials\gmail.secret"
$appPassword = (Get-Content $secretPath -Raw).Trim()
$securePass  = ConvertTo-SecureString $appPassword -AsPlainText -Force
$cred        = New-Object System.Management.Automation.PSCredential($from, $securePass)

Send-MailMessage `
    -SmtpServer "smtp.gmail.com" `
    -Port 587 `
    -UseSsl `
    -Credential $cred `
    -From $from `
    -To $to `
    -Subject $subject `
    -Body $emailBody `
    -Encoding UTF8

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Email sent to $to."
