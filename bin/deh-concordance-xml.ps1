param(
  [ValidateSet('Corpus', 'Package')][string]$Mode = 'Corpus',
  [string]$RepoRoot,
  [string]$PackagePath
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$teiNamespace = 'http://www.tei-c.org/ns/1.0'
$xmlNamespace = 'http://www.w3.org/XML/1998/namespace'

function File-Sha256([string]$filePath) {
  $stream = [System.IO.File]::OpenRead($filePath)
  $sha = [System.Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
  finally { $stream.Dispose(); $sha.Dispose() }
}

if ($Mode -eq 'Package') {
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $archive = [System.IO.Compression.ZipFile]::OpenRead($PackagePath)
  try {
    $files = [ordered]@{}
    $hashes = [ordered]@{}
    foreach ($name in @('deh-parallels.json', 'source/workbook_values.json', 'editorial_decisions.json')) {
      $entry = $archive.GetEntry('DEH_Parallels_v0_2_2026-10-02/' + $name)
      if (!$entry) { throw "Missing package entry: $name" }
      $stream = $entry.Open()
      $buffer = [System.IO.MemoryStream]::new()
      try {
        $stream.CopyTo($buffer)
        $bytes = $buffer.ToArray()
        $files[$name] = [System.Text.Encoding]::UTF8.GetString($bytes)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try { $hashes[$name] = ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant() }
        finally { $sha.Dispose() }
      } finally { $stream.Dispose(); $buffer.Dispose() }
    }
    [ordered]@{files=$files; hashes=$hashes; sha256=(File-Sha256 $PackagePath)} | ConvertTo-Json -Depth 100 -Compress
  } finally { $archive.Dispose() }
  exit
}

function Read-Tei([string]$relativePath) {
  $document = [System.Xml.XmlDocument]::new()
  $document.XmlResolver = $null
  $document.Load((Join-Path $RepoRoot $relativePath))
  if ($document.DocumentElement.NamespaceURI -ne $teiNamespace) { throw "Unexpected TEI namespace: $relativePath" }
  return ,$document
}
function Body-Paragraphs($document) { return $document.SelectNodes("//*[local-name()='body']//*[local-name()='p']") }
function Xml-Id($node) { return $node.GetAttribute('id', $xmlNamespace) }
function Milestone-Numbers($document) {
  return @($document.SelectNodes("//*[local-name()='body']//*[local-name()='milestone'][@unit='niese'][@n]") |
    Where-Object { $_.GetAttribute('n') -match '^[1-9]\d*$' } | ForEach-Object { [int]$_.GetAttribute('n') })
}

$deh = @()
$englishTargets = @()
$allLatinIds = @()
foreach ($book in 1..5) {
  $suffix = $book.ToString('00')
  $latin = Read-Tei "assets/xml/deh/Latin/book-$suffix.xml"
  foreach ($paragraph in (Body-Paragraphs $latin)) {
    $id = Xml-Id $paragraph
    if ($id -notmatch "^latin-deh$book-num[1-9]\d*$") { continue }
    $allLatinIds += $id
    $labels = @($paragraph.SelectNodes("./*[local-name()='num']") | ForEach-Object { $_.InnerText.Trim() })
    if ($labels.Count -ne 1 -or $labels[0] -notmatch '^\[([^\]]+)\]$') { throw "Ambiguous DEH citation: $id" }
    $deh += [ordered]@{book=$book; citation=$Matches[1]; xml_id=$id}
  }
  $english = Read-Tei "assets/xml/deh/English/book-$suffix.xml"
  foreach ($paragraph in (Body-Paragraphs $english)) {
    foreach ($target in ($paragraph.GetAttribute('sameAs') -split '\s+')) {
      if ($target) { $englishTargets += ($target -split '#')[-1] }
    }
  }
}

$bellum = [ordered]@{}
foreach ($book in 1..7) {
  $suffix = $book.ToString('00')
  $sources = [ordered]@{}
  foreach ($language in @('Greek', 'Latin', 'English')) {
    $document = Read-Tei "assets/xml/bellum/$language/book-$suffix.xml"
    $numbers = @()
    if ($language -eq 'Greek') {
      foreach ($paragraph in (Body-Paragraphs $document)) {
        if ((Xml-Id $paragraph) -match "^greek-bellum$book-num([1-9]\d*)$") { $numbers += [int]$Matches[1] }
      }
    } else {
      $numbers = @(Milestone-Numbers $document)
      if ($language -eq 'Latin') {
        foreach ($paragraph in (Body-Paragraphs $document)) {
          if ((Xml-Id $paragraph) -match "^latin-bellum$book-num([1-9]\d*)$") {
            $number = [int]$Matches[1]
            if ($paragraph.InnerText -match "^\s*\[\s*$number\s*\]") { $numbers += $number }
          }
        }
      }
    }
    $sources[$language] = @($numbers)
  }
  $bellum["$book"] = $sources
}

$antiquities = [ordered]@{}
foreach ($book in 1..20) {
  $suffix = $book.ToString('00')
  $sources = [ordered]@{}
  foreach ($language in @('Latin', 'Greek')) {
    $document = Read-Tei "assets/xml/antiquities/$language/book-$suffix.xml"
    $numbers = @()
    foreach ($num in $document.SelectNodes("//*[local-name()='body']//*[local-name()='num']")) {
      $digits = [regex]::Matches($num.InnerText.Trim(), '\d+')
      if ($digits.Count) { $numbers += [int]$digits[$digits.Count - 1].Value }
    }
    if ($language -eq 'Latin') { $numbers += @(Milestone-Numbers $document) }
    $sources[$language] = @($numbers)
  }
  $antiquities["$book"] = $sources
}

$hashes = [ordered]@{}
foreach ($file in (Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'assets/xml') -Filter '*.xml' -Recurse -File | Sort-Object FullName)) {
  # Parse every canonical XML file, including sources not used for references.
  $relative = $file.FullName.Substring($RepoRoot.Length + 1).Replace('\', '/')
  $null = Read-Tei $relative
  $hashes[$relative] = File-Sha256 $file.FullName
}
[ordered]@{deh=$deh; latin_ids=$allLatinIds; english_targets=$englishTargets; bellum=$bellum; antiquities=$antiquities; xml_sha256=$hashes} | ConvertTo-Json -Depth 100 -Compress
