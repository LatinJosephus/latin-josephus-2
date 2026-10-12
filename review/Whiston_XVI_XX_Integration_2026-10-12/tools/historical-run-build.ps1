$ErrorActionPreference = 'Stop'
$integrationRoot = 'C:\workspace\Whiston-XVI-XX-Integration-20261012'
$integrationRepo = Join-Path $integrationRoot 'candidate'
$integrationRuntime = Join-Path $integrationRoot 'runtime'
$env:TEMP = Join-Path $integrationRuntime 'tmp'
$env:TMP = $env:TEMP
$env:GEM_HOME = Join-Path $integrationRuntime 'gems'
$env:GEM_PATH = "$env:GEM_HOME;C:\workspace\Whiston-I-XI-Integration-runtime-20261011\gems;C:\Ruby33-x64\lib\ruby\gems\3.3.0;C:\Users\Pollard_R\.local\share\gem\ruby\3.3.0"
$env:BUNDLE_USER_HOME = Join-Path $integrationRuntime 'bundle-user'
New-Item -ItemType Directory -Path $env:TEMP,$env:GEM_HOME,$env:BUNDLE_USER_HOME -Force | Out-Null
Set-Location -LiteralPath $integrationRepo
& 'C:\Ruby33-x64\bin\bundle.bat' check *> (Join-Path $integrationRuntime 'bundle-check.log')
if ($LASTEXITCODE -ne 0) { throw 'Bundle check failed' }
& 'C:\Ruby33-x64\bin\bundle.bat' exec jekyll build --destination (Join-Path $integrationRuntime 'standard-site') --disable-disk-cache *> (Join-Path $integrationRuntime 'standard-build.log')
if ($LASTEXITCODE -ne 0) { throw 'Standard build failed' }
& node bin/prepare-reader-publication.mjs --site (Join-Path $integrationRuntime 'standard-site') *> (Join-Path $integrationRuntime 'generated-source-verification.json')
if ($LASTEXITCODE -ne 0) { throw 'Generated-source preparation failed' }
& node bin/reader-corpus-qa.mjs --site (Join-Path $integrationRuntime 'standard-site') *> (Join-Path $integrationRuntime 'reader-corpus-guard.json')
if ($LASTEXITCODE -ne 0) { throw 'Production corpus guard failed' }
Write-Output 'Standard full-plugin build and approved corpus guards PASS'
