param([ValidateSet('Bellum','Lodge')][string]$Part)
$ErrorActionPreference='Stop'
$taskRoot='C:\workspace\Whiston-XVI-XX-Integration-20261012'
$taskRepo=Join-Path $taskRoot 'candidate'
$taskRuntime=Join-Path $taskRoot 'runtime'
$taskPack=Join-Path $taskRepo 'review\Whiston_XVI_XX_Integration_2026-10-12'
$env:TEMP=Join-Path $taskRuntime 'tmp';$env:TMP=$env:TEMP
$moduleRoot='C:\Users\Pollard_R\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
$browserPath='C:\Program Files\Google\Chrome\Application\chrome.exe'
Set-Location -LiteralPath $taskRepo
New-Item -ItemType Directory -Force -Path (Join-Path $taskPack 'execution-logs') | Out-Null
if($Part -eq 'Bellum'){
 & node bin/bellum-greek-range-qa.mjs --site (Join-Path $taskRuntime 'standard-site') --out (Join-Path $taskRuntime 'native-bellum') --module-root $moduleRoot --browser $browserPath *> (Join-Path $taskPack 'execution-logs/native-bellum.log')
 if($LASTEXITCODE -ne 0){throw 'Complete native Bellum QA failed'}
 Write-Output 'Complete native Bellum Greek/Whiston/Lodge ranges PASS'
}else{
 & node (Join-Path $taskPack 'tools/native_lodge_qa.mjs') --site (Join-Path $taskRuntime 'standard-site') --module-root $moduleRoot --browser $browserPath *> (Join-Path $taskPack 'execution-logs/native-lodge.log')
 if($LASTEXITCODE -ne 0){throw 'Complete native Lodge browser QA failed'}
 & pwsh -NoProfile -File bin/lodge1602-bellum-qa.ps1 -MasterZip 'C:\Users\Pollard_R\Downloads\Lodge1602_Bellum_FINAL_ADJUDICATED_20261003.zip' -RepoRoot $taskRepo -SelfTest -NoWrite *> (Join-Path $taskPack 'execution-logs/lodge-master-negative.log')
 if($LASTEXITCODE -ne 0){throw 'Lodge master and corruption guard failed'}
 Write-Output 'Complete native Lodge and immutable master/corruption guards PASS'
}
