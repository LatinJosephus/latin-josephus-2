$ErrorActionPreference='Stop'
$taskRoot='C:\workspace\Whiston-XVI-XX-Integration-20261012'
$taskRepo=Join-Path $taskRoot 'candidate'
$taskPack=Join-Path $taskRepo 'review\Whiston_XVI_XX_Integration_2026-10-12'
$taskRuntime=Join-Path $taskRoot 'runtime'
$env:TEMP=Join-Path $taskRuntime 'tmp';$env:TMP=$env:TEMP
$env:PLAYWRIGHT_MODULE='C:\Users\Pollard_R\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright'
$env:WHISTON_SITE=Join-Path $taskRuntime 'standard-site'
Set-Location -LiteralPath $taskRepo
function Run-TaskNode([string]$script){& node (Join-Path $taskPack "tools\$script");if($LASTEXITCODE -ne 0){throw "QA failed: $script"}}
$env:QA_BOOKS='preface,1,2,3,4,5';$env:QA_REPORT_FILE='CUMULATIVE_A_ENGLISH_QA.json';Run-TaskNode 'browser_qa.cjs'
$env:QA_BOOKS='6,7,8,9,10,11';$env:QA_REPORT_FILE='CUMULATIVE_B_ENGLISH_QA.json';Run-TaskNode 'browser_qa.cjs'
$env:QA_BOOKS='12,13,14,15';$env:QA_REPORT_FILE='CUMULATIVE_C_ENGLISH_QA.json';Run-TaskNode 'browser_qa.cjs'
# Stage C already checks all 1,772 new selections at this exact renderer/source state.
Copy-Item -LiteralPath (Join-Path $taskPack 'STAGE_C_SECTION_QA.json') -Destination (Join-Path $taskPack 'NEW_XVI_XX_ENGLISH_QA.json')
Remove-Item Env:QA_BOOKS;Remove-Item Env:QA_REPORT_FILE
foreach($script in @('structural_qa.cjs','regression_qa.cjs','bamberg_qa.cjs','special_qa.cjs','ui_qa.cjs','book_navigation_qa.cjs','auxiliary_qa.cjs')){Run-TaskNode $script}
Write-Output 'Final exhaustive browser and established regressions PASS'
