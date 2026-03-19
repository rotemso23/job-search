# Daily Job Search Runner
# Runs the job-search-agent via Claude Code CLI and sends results by email.

$userHome = $env:USERPROFILE
$env:PATH = "$userHome\.local\bin;" + $env:PATH

$workDir  = $PSScriptRoot
$date     = Get-Date -Format "yyyy-MM-dd"
$logFile  = "$workDir\job-results\${date}_search.md"
$debugLog = "$workDir\job-results\${date}_debug.log"

$from     = "rotemso23@gmail.com"
$to       = "rotemso23@gmail.com"
$subject  = "Daily Job Search Results - $date"

Set-Location $workDir

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

$claudeOutput = & claude --dangerously-skip-permissions -p $prompt 2>&1
$claudeOutput | Out-File -FilePath $debugLog -Encoding UTF8 -Append

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Agent finished."

# -- 2. Read results file -----------------------------------------------------
if (Test-Path $logFile) {
    $body = Get-Content $logFile -Raw -Encoding UTF8
} else {
    $body = "Job search completed but results file was not found at:`n$logFile"
}

# -- 3. Build numbered quick-apply header -------------------------------------
$jobs = @()
$inJobListings = $false
foreach ($line in ($body -split "`n")) {
    if ($line -match '^## Job Listings') { $inJobListings = $true; continue }
    if ($line -match '^## '             ) { $inJobListings = $false }
    if ($inJobListings -and $line -match '^### (.+)$') {
        $jobs += $Matches[1]
    }
}

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
