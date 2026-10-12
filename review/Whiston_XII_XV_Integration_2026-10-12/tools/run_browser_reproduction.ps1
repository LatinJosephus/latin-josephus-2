param([Parameter(Mandatory=$true)][string]$PlaywrightModule, [string]$Python='python')
$ErrorActionPreference='Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$taskBase = Split-Path $taskRoot
$taskRuntime = Join-Path $taskBase 'runtime'
New-Item -ItemType Directory -Force -Path (Join-Path $taskRuntime 'tmp') | Out-Null
$env:TEMP=Join-Path $taskRuntime 'tmp'; $env:TMP=$env:TEMP
$env:PLAYWRIGHT_MODULE=$PlaywrightModule
$env:WHISTON_SITE=Join-Path $taskRuntime 'standard-site'
function Invoke-TaskNode([string]$file) {
 & node (Join-Path $PSScriptRoot $file)
 if($LASTEXITCODE -ne 0){throw "Failed: $file"}
}
# Operate only on an independently recovered candidate. Reports are generated there.
$env:QA_BOOKS='preface,1,2,3,4,5'; $env:QA_REPORT_FILE='CUMULATIVE_A_ENGLISH_QA.json'; Invoke-TaskNode 'browser_qa.cjs'
$env:QA_BOOKS='6,7,8,9,10,11'; $env:QA_REPORT_FILE='CUMULATIVE_B_ENGLISH_QA.json'; Invoke-TaskNode 'browser_qa.cjs'
$env:QA_BOOKS='12,13,14,15'; $env:QA_REPORT_FILE='NEW_XII_XV_ENGLISH_QA.json'; Invoke-TaskNode 'browser_qa.cjs'
Remove-Item Env:QA_BOOKS; Remove-Item Env:QA_REPORT_FILE
foreach($file in @('regression_qa.cjs','bamberg_qa.cjs','ui_qa.cjs','book_navigation_qa.cjs','auxiliary_qa.cjs')){Invoke-TaskNode $file}
& $Python (Join-Path $PSScriptRoot 'verify_candidate.py')
if($LASTEXITCODE -ne 0){throw 'Independent source/oracle verification failed'}
