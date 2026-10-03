param(
  [Parameter(Mandatory)][string]$MasterZip,
  [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent),
  [switch]$SelfTest,
  [switch]$NoWrite
)
# Independent acceptance gate: no importer functions or generated expectations.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -TypeDefinition @'
using System;
using System.Linq;
using System.Text;
using System.Xml;
public static class LodgeTree {
  public static string Signature(XmlNode n) {
    var b = new StringBuilder(); Walk(n,b); return b.ToString();
  }
  static void Token(StringBuilder b,string v) { b.Append(v.Length).Append(':').Append(v); }
  static void Walk(XmlNode n,StringBuilder b) {
    Token(b,((int)n.NodeType).ToString()); Token(b,n.LocalName); Token(b,n.NamespaceURI);
    if(n.Attributes != null) foreach(XmlAttribute a in n.Attributes.Cast<XmlAttribute>()
      .Where(a=>a.NamespaceURI!="http://www.w3.org/2000/xmlns/")
      .OrderBy(a=>a.NamespaceURI,StringComparer.Ordinal).ThenBy(a=>a.LocalName,StringComparer.Ordinal)) {
      Token(b,a.NamespaceURI); Token(b,a.LocalName); Token(b,a.Value);
    }
    b.Append('|'); Token(b,n.Value ?? "");
    foreach(XmlNode c in n.ChildNodes) Walk(c,b);
    b.Append(';');
  }
}
'@
$tei = 'http://www.tei-c.org/ns/1.0'; $xml = 'http://www.w3.org/XML/1998/namespace'
$expectedHash = '18a34bdbbfd199ab482b73ad442c19cd0fb5e70794e9d77aa0a74a1c7ad26fc0'
$checks = [Collections.Generic.List[string]]::new()
function Assert($condition, [string]$label) {
  if (!$condition) { throw "FAIL: $label" }
}
function Bytes([string]$entry) {
  $e = $zip.GetEntry($entry); Assert ($null -ne $e) "master entry $entry"
  $s = $e.Open(); $m = [IO.MemoryStream]::new()
  try { $s.CopyTo($m); return ,$m.ToArray() } finally { $s.Dispose(); $m.Dispose() }
}
function Hash([byte[]]$b) {
  return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($b)).ToLowerInvariant()
}
function Document([byte[]]$b) {
  $d = [Xml.XmlDocument]::new(); $d.PreserveWhitespace = $true; $d.XmlResolver = $null
  $m = [IO.MemoryStream]::new($b, $false)
  try { $d.Load($m) } finally { $m.Dispose() }
  return ,$d
}
function Namespace($d) {
  $n = [Xml.XmlNamespaceManager]::new($d.NameTable); $n.AddNamespace('t', $tei); $n.AddNamespace('xml', $xml)
  return ,$n
}
function Rows([byte[]]$b) {
  $lines = [Text.Encoding]::UTF8.GetString($b).TrimEnd([char]10,[char]13).Split([char]10)
  $keys = $lines[0].TrimEnd([char]13).Split([char]9)
  foreach ($line in $lines[1..($lines.Count-1)]) {
    $v = $line.TrimEnd([char]13).Split([char]9); Assert ($v.Count -eq $keys.Count) 'TSV columns'
    $r = @{}; for ($i=0; $i -lt $keys.Count; $i++) { $r[$keys[$i]]=$v[$i] }; [pscustomobject]$r
  }
}
function Verify-Book($candidate, $production, $latin, [int]$book) {
  $ns = Namespace $production; $cs = Namespace $candidate; $ls = Namespace $latin
  $pad = $book.ToString('00')
  $body = $production.SelectSingleNode('/t:TEI/t:text/t:body',$ns)
  Assert ($body.InnerText -ceq $candidate.SelectSingleNode('/t:TEI/t:text/t:body',$cs).InnerText) "book $book decoded text and whitespace"
  $chapters = @($body.SelectNodes('t:div1/t:div2',$ns))
  $ps = @($body.SelectNodes('.//t:p',$ns))
  $milestones = @($body.SelectNodes('.//t:milestone[@unit="niese"]',$ns))
  Assert ($chapters.Count -eq @(34,22,10,11,13,10,11)[$book-1]) "book $book chapter count"
  Assert ($ps.Count -eq @(234,143,88,78,65,50,46)[$book-1]) "book $book coarse count"
  Assert ($milestones.Count -eq @(673,654,542,663,572,442,455)[$book-1]) "book $book Niese count"
  for ($i=0; $i -lt $milestones.Count; $i++) {
    Assert ($milestones[$i].GetAttribute('n') -ceq [string]($i+1)) "book $book complete Niese order"
    Assert ($milestones[$i].GetAttribute('cert') -ceq 'high') "book $book HIGH"
    Assert (!$milestones[$i].HasAttribute('sameAs')) "book $book independent Niese layer"
  }
  $ids = @($production.SelectNodes('//*[@xml:id]',$ns) | ForEach-Object { $_.GetAttribute('id',$xml) })
  Assert (($ids | Sort-Object -Unique).Count -eq $ids.Count) "book $book unique IDs"
  $rows = @($coarse | Where-Object { [int]$_.book -eq $book })
  Assert ($rows.Count -eq $ps.Count) "book $book register coverage"
  $parentMap = @{}; $seen = @{}
  foreach ($row in $rows) {
    $p = $production.SelectSingleNode("//t:body//t:p[@xml:id='$($row.candidate_unit_id)']",$ns)
    $target = $latin.SelectSingleNode("//t:body//t:p[@xml:id='$($row.latin_unit_id)']",$ls)
    Assert ($p -and $target -and !$seen.ContainsKey($row.candidate_unit_id)) "book $book registered identity"
    $seen[$row.candidate_unit_id]=$true
    $uri = "../../Latin/book-$pad.xml#$($row.latin_unit_id)"
    Assert ($p.GetAttribute('sameAs') -ceq $uri) "book $book registered coarse sameAs"
    $resolved = [IO.Path]::GetFullPath((Join-Path $RepoRoot "assets/xml/bellum/English/Lodge1602/$($uri.Split('#')[0])"))
    Assert ($resolved -eq (Join-Path $RepoRoot "assets/xml/bellum/Latin/book-$pad.xml")) "book $book relative URI"
    Assert ($p.ParentNode.LocalName -eq 'div2' -and $target.ParentNode.LocalName -eq 'div2') "book $book actual parents"
    Assert ($p.ParentNode.GetAttribute('n') -ceq $row.project_chapter -and $target.ParentNode.GetAttribute('n') -ceq $row.project_chapter) "book $book register chapter"
    $cid = $p.ParentNode.GetAttribute('id',$xml); $tid = $target.ParentNode.GetAttribute('id',$xml)
    Assert (!$parentMap.ContainsKey($cid) -or $parentMap[$cid] -ceq $tid) "book $book consistent chapter"
    $parentMap[$cid]=$tid
  }
  foreach ($chapter in $chapters) {
    $cid=$chapter.GetAttribute('id',$xml)
    Assert ($parentMap.ContainsKey($cid) -and $chapter.GetAttribute('sameAs') -ceq "../../Latin/book-$pad.xml#$($parentMap[$cid])") "book $book actual chapter sameAs"
  }
  Assert (@($production.SelectNodes('//*[@sameAs]',$ns)).Count -eq ($ps.Count+$chapters.Count)) "book $book only authorized links"
  $copy = $production.CloneNode($true); $copyNs=Namespace $copy
  foreach ($node in $copy.SelectNodes('//t:body//*[@sameAs]',$copyNs)) { $node.RemoveAttribute('sameAs') }
  foreach ($spec in @(
    @('responsibility','/t:TEI/t:teiHeader/t:fileDesc/t:titleStmt','respStmt'),
    @('master','/t:TEI/t:teiHeader/t:fileDesc/t:sourceDesc','bibl'),
    @('encoding','/t:TEI/t:teiHeader/t:encodingDesc/t:editorialDecl','p'),
    @('change','/t:TEI/t:teiHeader/t:revisionDesc','change')
  )) {
    $id="lodge1602-production-b$book-$($spec[0])"
    $nodes=@($copy.SelectNodes("//*[@xml:id='$id']",$copyNs))
    Assert ($nodes.Count -eq 1 -and $nodes[0].LocalName -ceq $spec[2]) "book $book identified provenance"
    Assert ($nodes[0].ParentNode -eq $copy.SelectSingleNode($spec[1],$copyNs)) "book $book appended provenance parent"
    Assert ($nodes[0].NextSibling -eq $null) "book $book provenance is appended"
    if ($spec[0] -eq 'master') { Assert ($nodes[0].InnerText.Contains($expectedHash)) "book $book master provenance hash" }
    [void]$nodes[0].ParentNode.RemoveChild($nodes[0])
  }
  Assert ([LodgeTree]::Signature($copy.DocumentElement) -ceq [LodgeTree]::Signature($candidate.DocumentElement)) "book $book entire source tree, header, attributes, IDs and milestone offsets preserved"
  return [ordered]@{ book=$book; chapters=$chapters.Count; coarse=$ps.Count; niese=$milestones.Count; decoded_text_utf16=$body.InnerText.Length; production_sha256=(Hash ([IO.File]::ReadAllBytes((Join-Path $RepoRoot "assets/xml/bellum/English/Lodge1602/book-$pad.xml")))) }
}
$RepoRoot=[IO.Path]::GetFullPath($RepoRoot)
Assert ((Get-FileHash -LiteralPath $MasterZip -Algorithm SHA256).Hash.ToLowerInvariant() -ceq $expectedHash) 'master ZIP SHA-256'
$zip=[IO.Compression.ZipFile]::OpenRead($MasterZip)
try {
  $coarse=@(Rows (Bytes 'work/output/Lodge1602_Bellum_SUBCHAPTER_ALIGNMENT_704.tsv'))
  $sections=@(Rows (Bytes 'work/output/Lodge1602_Bellum_NIESE_SEGMENTATION_4001.tsv'))
  Assert ($coarse.Count -eq 704 -and @($coarse | Where-Object confidence -ne 'HIGH').Count -eq 0) '704 HIGH authority rows'
  Assert ($sections.Count -eq 4001 -and @($sections | Where-Object confidence -ne 'HIGH').Count -eq 0) '4001 HIGH authority rows'
  foreach ($name in @('Lodge1602_Bellum_SUBCHAPTER_ALIGNMENT_704.tsv','Lodge1602_Bellum_NIESE_SEGMENTATION_4001.tsv','Lodge1602_Bellum_SOURCE_MANIFEST.json','Lodge1602_Bellum_FINAL_HUMAN_ADJUDICATIONS.json','Lodge1602_Bellum_QA.json','SHA256SUMS.txt')) {
    Assert ((Hash ([IO.File]::ReadAllBytes((Join-Path $RepoRoot "_docs/lodge1602-bellum-source/$name")))) -ceq (Hash (Bytes "work/output/$name"))) "frozen evidence byte equality: $name"
  }
  $results=@()
  for ($b=1; $b -le 7; $b++) {
    $pad=$b.ToString('00')
    $candidate=Document (Bytes "work/output/Candidates/Lodge1602_Bellum_book-$pad.xml")
    $production=Document ([IO.File]::ReadAllBytes((Join-Path $RepoRoot "assets/xml/bellum/English/Lodge1602/book-$pad.xml")))
    $latin=Document ([IO.File]::ReadAllBytes((Join-Path $RepoRoot "assets/xml/bellum/Latin/book-$pad.xml")))
    $results+=Verify-Book $candidate $production $latin $b
    foreach ($pair in @(@('Latin','Latin_Cardwell'),@('Greek','Greek_Niese'),@('English','English_Whiston'))) {
      $original=Bytes "work/authorities/Lodge1602_Bellum_WorkBot_Input/Bellum/$($pair[1])/book-$pad.xml"
      Assert ((Hash $original) -ceq (Hash ([IO.File]::ReadAllBytes((Join-Path $RepoRoot "assets/xml/bellum/$($pair[0])/book-$pad.xml"))))) "unchanged $($pair[0]) book $b"
    }
    if ($b -eq 3) { $testCandidate=$candidate; $testProduction=$production; $testLatin=$latin }
    if ($b -eq 6) {
      $ns=Namespace $production
      foreach ($pair in @(@('3',''),@('427','latin-bellum6-num420'))) {
        $m=$production.SelectSingleNode("//t:body//t:milestone[@unit='niese'][@n='$($pair[0])']",$ns)
        if ($pair[0] -eq '3') {
          Assert ($m.NextSibling.LocalName -eq 'gap' -and $m.NextSibling.GetAttribute('reason') -eq 'omitted' -and $m.NextSibling.GetAttribute('unit') -eq 'niese-section' -and $m.NextSibling.NextSibling.GetAttribute('n') -eq '4') 'VI.3 exact empty omission'
        } else { Assert ($m.SelectSingleNode('ancestor::t:p',$ns).GetAttribute('sameAs').EndsWith('#'+$pair[1])) 'VI.427 in coarse 420' }
      }
    }
  }
  $ns=Namespace $testProduction
  Assert ($testProduction.SelectSingleNode("//t:milestone[@unit='niese'][@n='3']/ancestor::t:p",$ns).GetAttribute('sameAs').EndsWith('#latin-bellum3-num1')) 'III.3 in coarse 1'
  $selfTests=@()
  if ($SelfTest) {
    $mutations=[ordered]@{
      text={param($d,$n) $d.SelectSingleNode('//t:body//text()[normalize-space(.)!=""]',$n).Value+='x'}
      whitespace={param($d,$n) $d.SelectSingleNode('//t:body//text()',$n).Value+=' '}
      id={param($d,$n) $d.SelectSingleNode('//t:body//t:p',$n).SetAttribute('id',$xml,'corrupt')}
      coarse_link={param($d,$n) $d.SelectSingleNode('//t:body//t:p',$n).SetAttribute('sameAs','../../Latin/book-03.xml#latin-bellum3-num3')}
      chapter_link={param($d,$n) $d.SelectSingleNode('//t:body//t:div2',$n).SetAttribute('sameAs','../../Latin/book-03.xml#corrupt')}
      milestone_metadata={param($d,$n) $d.SelectSingleNode('//t:milestone[@unit="niese"]',$n).SetAttribute('cert','medium')}
      milestone_link={param($d,$n) $d.SelectSingleNode('//t:milestone[@unit="niese"]',$n).SetAttribute('sameAs','#corrupt')}
      header={param($d,$n) $d.SelectSingleNode('//t:teiHeader//t:title',$n).InnerText='corrupt'}
      extra_attribute={param($d,$n) $d.SelectSingleNode('//t:body//t:p',$n).SetAttribute('data-corrupt','1')}
    }
    foreach ($entry in $mutations.GetEnumerator()) {
      $d=$testProduction.CloneNode($true); $n=Namespace $d; & $entry.Value $d $n | Out-Null
      $rejected=$false
      try { Verify-Book $testCandidate $d $testLatin 3 | Out-Null } catch { $rejected=$true }
      Assert $rejected "independent corruption detection: $($entry.Key)"
      $selfTests+=$entry.Key
    }
  }
  $manifest=Get-Content -LiteralPath (Join-Path $RepoRoot '_docs/lodge1602-bellum-integration.json') -Raw | ConvertFrom-Json
  Assert (@($manifest.original_xml_sha256.PSObject.Properties).Count -eq 100) '100 historical XML recorded'
  foreach ($p in $manifest.original_xml_sha256.PSObject.Properties) {
    Assert ((Get-FileHash -LiteralPath (Join-Path $RepoRoot $p.Name) -Algorithm SHA256).Hash.ToLowerInvariant() -ceq $p.Value) "original XML unchanged: $($p.Name)"
  }
  foreach ($book in $results) { Assert ($book.production_sha256 -ceq $manifest.books[$book.book-1].production_sha256) 'production manifest hash' }
  $report=[ordered]@{
    schema='lodge1602-bellum-validation-v1'; date='2026-10-03'; status='PASS'; master_sha256=$expectedHash
    books=$results; chapters=111; coarse_links=704; niese=4001; HIGH=4001; MEDIUM=0; LOW=0
    exact_decoded_text_and_whitespace_preserved=$true; complete_source_tree_and_original_tcp_header_preserved=$true
    niese_ids_metadata_and_offsets_preserved=$true; frozen_human_history_byte_identical=$true
    original_bellum_xml_byte_identical=21; all_original_xml_byte_identical=100
    safeguards=@('I.24','III.3','III.182','III.183','VI.3','VI.267','VI.356','VI.427','VII.26')
    independent_corruption_tests_rejected=$selfTests
  }
  if (!$NoWrite) {
    [IO.File]::WriteAllText((Join-Path $RepoRoot '_docs/lodge1602-bellum-validation.json'),($report | ConvertTo-Json -Depth 10)+[char]10,[Text.UTF8Encoding]::new($false))
  }
  $report | ConvertTo-Json -Depth 10
} finally { $zip.Dispose() }
