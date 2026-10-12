param([Parameter(Mandatory=$true)][string]$PlaywrightModule)
$ErrorActionPreference='Stop'
$taskRepo=(Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$taskBase=Split-Path $taskRepo
$taskPack=Split-Path $PSScriptRoot
$taskRuntime=Join-Path $taskBase 'runtime'
New-Item -ItemType Directory -Force -Path (Join-Path $taskRuntime 'tmp') | Out-Null
$env:TEMP=Join-Path $taskRuntime 'tmp';$env:TMP=$env:TEMP
$env:PLAYWRIGHT_MODULE=$PlaywrightModule
$env:WHISTON_SITE=Join-Path $taskRuntime 'standard-site'
function Run-TaskNode([string]$file){& node (Join-Path $PSScriptRoot $file);if($LASTEXITCODE -ne 0){throw "QA failed: $file"}}
$env:QA_BOOKS='preface,1,2,3,4,5';$env:QA_REPORT_FILE='CUMULATIVE_A_ENGLISH_QA.json';Run-TaskNode 'browser_qa.cjs'
$env:QA_BOOKS='6,7,8,9,10,11';$env:QA_REPORT_FILE='CUMULATIVE_B_ENGLISH_QA.json';Run-TaskNode 'browser_qa.cjs'
$env:QA_BOOKS='12,13,14,15';$env:QA_REPORT_FILE='CUMULATIVE_C_ENGLISH_QA.json';Run-TaskNode 'browser_qa.cjs'
$env:QA_BOOKS='16,17,18,19,20';$env:QA_REPORT_FILE='NEW_XVI_XX_ENGLISH_QA.json';Run-TaskNode 'browser_qa.cjs'
Remove-Item Env:QA_BOOKS;Remove-Item Env:QA_REPORT_FILE
foreach($file in @('structural_qa.cjs','regression_qa.cjs','bamberg_qa.cjs','special_qa.cjs','ui_qa.cjs','book_navigation_qa.cjs','auxiliary_qa.cjs')){Run-TaskNode $file}
Write-Output 'Fresh browser reproduction passed all 7,376 English intervals and containing/navigation/cross-work tests'
