param(
  [Parameter(Mandatory)][string]$MasterZip,
  [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent)
)
# Deterministic production derivative generator. The scholarly master is read-only.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$masterHash = '18a34bdbbfd199ab482b73ad442c19cd0fb5e70794e9d77aa0a74a1c7ad26fc0'
$baseline = '57b89a9d107bb76a2b30c146e401a2c76e25e4c3'
$teiNs = 'http://www.tei-c.org/ns/1.0'
$xmlNs = 'http://www.w3.org/XML/1998/namespace'
$RepoRoot = [IO.Path]::GetFullPath($RepoRoot).TrimEnd('\', '/')
function Hash-Bytes([byte[]]$bytes) {
  $h = [Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($h.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant() }
  finally { $h.Dispose() }
}
function Entry-Bytes([string]$name) {
  $entry = $archive.GetEntry($name)
  if (!$entry) { throw "Missing master entry: $name" }
  $s = $entry.Open(); $m = [IO.MemoryStream]::new()
  try { $s.CopyTo($m); return ,$m.ToArray() } finally { $s.Dispose(); $m.Dispose() }
}
function Entry-Text([string]$name) { return [Text.Encoding]::UTF8.GetString((Entry-Bytes $name)) }
function Parse-Rows([string]$text) {
  $lines = $text.TrimEnd([char]13, [char]10).Split([char]10)
  $keys = $lines[0].TrimEnd([char]13).Split([char]9)
  foreach ($line in $lines[1..($lines.Count - 1)]) {
    $values = $line.TrimEnd([char]13).Split([char]9)
    if ($values.Count -ne $keys.Count) { throw 'Invalid TSV column count' }
    $row = [ordered]@{}
    for ($j = 0; $j -lt $keys.Count; $j++) { $row[$keys[$j]] = $values[$j] }
    [pscustomobject]$row
  }
}
function Load-Xml([string]$text) {
  $d = [Xml.XmlDocument]::new(); $d.PreserveWhitespace = $true; $d.XmlResolver = $null
  $d.LoadXml($text); return ,$d
}
function Ns-Manager($d) {
  $n = [Xml.XmlNamespaceManager]::new($d.NameTable)
  $n.AddNamespace('t', $teiNs); $n.AddNamespace('xml', $xmlNs)
  return ,$n
}
function Write-Restricted([string]$relative, [byte[]]$bytes) {
  $path = [IO.Path]::GetFullPath((Join-Path $RepoRoot $relative))
  if (!$path.StartsWith($RepoRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Output escapes worktree' }
  if ($relative -notmatch '^(assets/xml/bellum/English/Lodge1602/book-0[1-7]\.xml|_docs/lodge1602-bellum-source/[^/]+|_docs/lodge1602-bellum-integration\.json)$') { throw "Unauthorized output: $relative" }
  [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($path)) | Out-Null
  [IO.File]::WriteAllBytes($path, $bytes)
}
function Append-Provenance($d, $ns, [int]$book) {
  $prefix = "lodge1602-production-b$book-"
  $node = $d.CreateElement('respStmt', $teiNs)
  [void]$node.SetAttribute('id', $xmlNs, ($prefix + 'responsibility'))
  $resp = $d.CreateElement('resp', $teiNs)
  $resp.InnerText = 'LatinJosephus structural correspondence and accepted Niese alignment; production transformation of the frozen scholarly master.'
  [void]$node.AppendChild($resp)
  $name = $d.CreateElement('name', $teiNs); $name.InnerText = 'LatinJosephus'; [void]$node.AppendChild($name)
  [void]$d.SelectSingleNode('/t:TEI/t:teiHeader/t:fileDesc/t:titleStmt', $ns).AppendChild($node)
  $node = $d.CreateElement('bibl', $teiNs)
  [void]$node.SetAttribute('id', $xmlNs, ($prefix + 'master')); [void]$node.SetAttribute('type', 'digital-source')
  foreach ($pair in @(
    @('source-package', 'Lodge1602_Bellum_FINAL_ADJUDICATED_20261003.zip'),
    @('SHA-256', $masterHash),
    @('TCP-source-SHA-256', '3ca2646644d8c91cf35e8575a6ffbdeb5ecbd378c502f53fd9445d7da7431de6')
  )) {
    $id = $d.CreateElement('idno', $teiNs); [void]$id.SetAttribute('type', $pair[0]); $id.InnerText = $pair[1]; [void]$node.AppendChild($id)
  }
  [void]$d.SelectSingleNode('/t:TEI/t:teiHeader/t:fileDesc/t:sourceDesc', $ns).AppendChild($node)
  $node = $d.CreateElement('p', $teiNs); [void]$node.SetAttribute('id', $xmlNs, ($prefix + 'encoding'))
  $node.InnerText = "This Book $book derivative publishes the selected Bellum material from EEBO-TCP A04680, under the LatinJosephus canonical book, Cardwell chapter/coarse-unit and independent Niese hierarchy. The retained TCP header describes the original source volume. Thomas Lodge's 1602 title describes the English translation as translated out of the Latin, and French. Structural sameAs attributes come exclusively from the frozen 704-unit register and actual Cardwell chapter membership. The accepted Lodge text, TCP source markup, 4001 Niese boundaries and human decision history are preserved. Production provenance is recorded in _docs/lodge1602-bellum-integration.json."
  [void]$d.SelectSingleNode('/t:TEI/t:teiHeader/t:encodingDesc/t:editorialDecl', $ns).AppendChild($node)
  $node = $d.CreateElement('change', $teiNs); [void]$node.SetAttribute('id', $xmlNs, ($prefix + 'change')); [void]$node.SetAttribute('when', '2026-10-03')
  $node.InnerText = 'Added production structural correspondence and provenance from the accepted frozen Lodge master; retained all original TCP header material and all accepted Niese placement metadata.'
  [void]$d.SelectSingleNode('/t:TEI/t:teiHeader/t:revisionDesc', $ns).AppendChild($node)
}
if ((Get-FileHash -LiteralPath $MasterZip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $masterHash) { throw 'Scholarly master ZIP hash differs' }
& git -C $RepoRoot merge-base --is-ancestor $baseline HEAD
if ($LASTEXITCODE -ne 0) { throw 'Worktree does not descend from the approved baseline' }
$archive = [IO.Compression.ZipFile]::OpenRead([IO.Path]::GetFullPath($MasterZip))
try {
  $sums = (Entry-Text 'work/output/SHA256SUMS.txt').Trim().Split([char]10)
  foreach ($line in $sums) {
    $parts = $line.TrimEnd([char]13) -split '  ', 2
    if ((Hash-Bytes (Entry-Bytes ('work/output/' + $parts[1]))) -ne $parts[0]) { throw "Frozen checksum mismatch: $($parts[1])" }
  }
  $registerName = 'Lodge1602_Bellum_SUBCHAPTER_ALIGNMENT_704.tsv'
  $rows = @(Parse-Rows (Entry-Text ('work/output/' + $registerName)))
  if ($rows.Count -ne 704 -or @($rows | Where-Object confidence -ne 'HIGH').Count) { throw 'Invalid frozen coarse register' }
  $originalHashes = [ordered]@{}
  $tracked = @(& git -C $RepoRoot ls-tree -r --name-only $baseline -- assets/xml)
  foreach ($path in $tracked) {
    if (!$path.EndsWith('.xml')) { continue }
    $blob = (& git -C $RepoRoot rev-parse ($baseline + ':' + $path)).Trim()
    $currentBlob = (& git -C $RepoRoot hash-object --path=$path (Join-Path $RepoRoot $path)).Trim()
    if ($blob -ne $currentBlob) { throw "Original XML differs from baseline: $path" }
    $originalHashes[$path] = (Get-FileHash -LiteralPath (Join-Path $RepoRoot $path) -Algorithm SHA256).Hash.ToLowerInvariant()
  }
  $documents = @(); $books = @(); $chapterLinks = @()
  for ($book = 1; $book -le 7; $book++) {
    $pad = $book.ToString('00')
    $input = "work/output/Candidates/Lodge1602_Bellum_book-$pad.xml"
    $doc = Load-Xml (Entry-Text $input); $ns = Ns-Manager $doc
    $latinPath = "assets/xml/bellum/Latin/book-$pad.xml"
    $latin = Load-Xml ([IO.File]::ReadAllText((Join-Path $RepoRoot $latinPath)))
    $lns = Ns-Manager $latin
    $parents = @{}; $unitSeen = @{}
    foreach ($row in @($rows | Where-Object { [int]$_.book -eq $book })) {
      $p = $doc.SelectSingleNode("//t:body//t:p[@xml:id='$($row.candidate_unit_id)']", $ns)
      $target = $latin.SelectSingleNode("//t:body//t:p[@xml:id='$($row.latin_unit_id)']", $lns)
      if (!$p -or !$target -or $unitSeen.ContainsKey($row.candidate_unit_id)) { throw 'Missing or repeated register identity' }
      if ($p.ParentNode.LocalName -ne 'div2' -or $target.ParentNode.LocalName -ne 'div2' -or $p.ParentNode.GetAttribute('n') -ne $row.project_chapter -or $target.ParentNode.GetAttribute('n') -ne $row.project_chapter) { throw "Chapter disagreement: $($row.candidate_unit_id)" }
      [void]$p.SetAttribute('sameAs', "../../Latin/book-$pad.xml#$($row.latin_unit_id)")
      $cid = $p.ParentNode.GetAttribute('id', $xmlNs); $tid = $target.ParentNode.GetAttribute('id', $xmlNs)
      if ($parents.ContainsKey($cid) -and $parents[$cid] -ne $tid) { throw "Ambiguous chapter correspondence: $cid" }
      $parents[$cid] = $tid; $unitSeen[$row.candidate_unit_id] = $true
    }
    foreach ($chapter in $doc.SelectNodes('/t:TEI/t:text/t:body/t:div1/t:div2', $ns)) {
      $cid = $chapter.GetAttribute('id', $xmlNs)
      if (!$parents.ContainsKey($cid)) { throw "Unregistered chapter: $cid" }
      $uri = "../../Latin/book-$pad.xml#$($parents[$cid])"; [void]$chapter.SetAttribute('sameAs', $uri)
      $chapterLinks += [ordered]@{ book = $book; lodge_chapter_id = $cid; cardwell_chapter_id = $parents[$cid]; sameAs = $uri }
    }
    Append-Provenance $doc $ns $book
    $settings = [Xml.XmlWriterSettings]::new()
    $settings.Encoding = [Text.UTF8Encoding]::new($false); $settings.Indent = $false; $settings.NewLineHandling = [Xml.NewLineHandling]::None
    $memory = [IO.MemoryStream]::new(); $writer = [Xml.XmlWriter]::Create($memory, $settings)
    try { $doc.Save($writer); $writer.Flush(); $bytes = $memory.ToArray() } finally { $writer.Dispose(); $memory.Dispose() }
    $output = "assets/xml/bellum/English/Lodge1602/book-$pad.xml"
    $documents += [pscustomobject]@{ path = $output; bytes = $bytes }
    $books += [ordered]@{ book = $book; candidate_entry = $input; candidate_sha256 = (Hash-Bytes (Entry-Bytes $input)); production_path = $output; production_sha256 = (Hash-Bytes $bytes) }
  }
  if ($chapterLinks.Count -ne 111) { throw 'Incorrect chapter link total' }
  $evidenceNames = @($registerName, 'Lodge1602_Bellum_NIESE_SEGMENTATION_4001.tsv', 'Lodge1602_Bellum_SOURCE_MANIFEST.json', 'Lodge1602_Bellum_FINAL_HUMAN_ADJUDICATIONS.json', 'Lodge1602_Bellum_QA.json', 'SHA256SUMS.txt')
  $evidence = [ordered]@{}
  foreach ($name in $evidenceNames) {
    $bytes = Entry-Bytes ('work/output/' + $name); $path = '_docs/lodge1602-bellum-source/' + $name
    $evidence[$path] = Hash-Bytes $bytes
  }
  $manifest = [ordered]@{
    schema = 'lodge1602-bellum-production-v1'; date = '2026-10-03'; baseline_commit = $baseline
    master = [ordered]@{ file = 'Lodge1602_Bellum_FINAL_ADJUDICATED_20261003.zip'; sha256 = $masterHash }
    source_key = 'lodge1602'; label = 'Lodge (1602)'; language = 'English'
    translation_source_description = 'translated out of the Latin, and French'
    tcp_id = 'A04680'; licence = 'CC0 1.0 Universal'; licence_url = 'https://creativecommons.org/publicdomain/zero/1.0/'
    source_xml_sha256 = '3ca2646644d8c91cf35e8575a6ffbdeb5ecbd378c502f53fd9445d7da7431de6'
    generator = [ordered]@{ path = 'bin/lodge1602-bellum-import.ps1'; sha256 = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant() }
    permitted_changes = @('sameAs on the 704 coarse p elements', 'sameAs on the 111 chapter div2 elements', 'four identified appended production header provenance nodes per book')
    counts = [ordered]@{ books = 7; chapters_including_preface = 111; coarse_units = 704; niese = 4001; HIGH = 4001; MEDIUM = 0; LOW = 0 }
    frozen_evidence_sha256 = $evidence; books = $books; chapter_links = $chapterLinks
    original_xml_sha256 = $originalHashes
    provenance_note = 'The master and copied editorial authorities remain frozen. Production SHA-256 values identify structural derivatives; Niese milestones and original Lodge/TCP text are unchanged.'
  }
  foreach ($item in $documents) { Write-Restricted $item.path $item.bytes }
  foreach ($name in $evidenceNames) { Write-Restricted ('_docs/lodge1602-bellum-source/' + $name) (Entry-Bytes ('work/output/' + $name)) }
  Write-Restricted '_docs/lodge1602-bellum-integration.json' ([Text.UTF8Encoding]::new($false).GetBytes(($manifest | ConvertTo-Json -Depth 20) + [char]10))
  [ordered]@{ status = 'generated'; books = 7; coarse_links = 704; chapter_links = 111; master_sha256 = $masterHash } | ConvertTo-Json -Compress
} finally { $archive.Dispose() }
