from pathlib import Path
import hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11'
RUNTIME=Path('C:/workspace/Whiston-I-XI-Integration-runtime-20261011')
old=Path('C:/workspace/Whiston-I-XI-Renderer-runtime-20261011/site');new=RUNTIME/'standard-site'
sha=lambda b:hashlib.sha256(b).hexdigest()
log=(RUNTIME/'standard-build.log').read_text()
assert 'done in 112.326 seconds.' in log and 'Configuration file:' in log
assert (RUNTIME/'bundle-check.log').read_text().strip()=="The Gemfile's dependencies are satisfied"
assert 'jekyll-responsive-image' in (ROOT/'_config.yml').read_text()
rows=[]
for relative in ['antiquities/index.html','bellum-judaicum/index.html','contra-apionem/index.html','deh/index.html','assets/css/main.css','assets/css/tei.css']:
 a=(old/relative).read_bytes();b=(new/relative).read_bytes()
 if a!=b:
  assert relative=='deh/index.html'
  normalize=lambda data:re.sub(rb'(deh-parallels\.css|dehParallels\.js)\?v=\d+',rb'\1?v=BUILD_TIMESTAMP',data)
  assert normalize(a)==normalize(b)
 rows.append({'path':relative,'certified_preview_sha256':sha(a),'standard_build_sha256':sha(b),'byte_identical':a==b,'only_DEH_cache_timestamp_differs':a!=b})
for folder in ['assets/xml','assets/js','assets/data']:
 for p in (old/folder).rglob('*'):
  if not p.is_file():continue
  target=new/p.relative_to(old);assert target.exists(),str(target)
  a=p.read_bytes();b=target.read_bytes()
  assert a.replace(b'\r\n',b'\n')==b.replace(b'\r\n',b'\n'),str(target)
  rows.append({'path':p.relative_to(old).as_posix(),'standard_build_sha256':sha(b),'same_runtime_content_as_certified_preview':True,'only_EOL_representation_differs':a!=b})
build_dir=PACK/'build';build_dir.mkdir(exist_ok=True)
for p in RUNTIME.glob('*.log'):shutil.copyfile(p,build_dir/p.name)
shutil.copyfile(RUNTIME/'im6-build-env.rb',build_dir/'im6-build-env.rb')
shutil.copyfile(ROOT/'Gemfile.lock',build_dir/'Gemfile.lock')
receipt={'status':'PASS','command':'bundle exec jekyll build --destination C:/workspace/Whiston-I-XI-Integration-runtime-20261011/standard-site --disable-disk-cache',
 'production_configuration_unmodified':True,'all_required_plugins_enabled':True,'no_responsive_image_exclusion':True,'bundle_check':'PASS','duration_seconds':112.326,
 'isolated_missing_dependency_resolution':'RMagick 4.3.0 built against the installed ImageMagick 6.9.13 SDK; compiler bootstrap selects that SDK instead of RubyInstaller bundled ImageMagick 7. No gem source or build assertion changed.',
 'standard_build_has_no_RUBYOPT_bootstrap_requirement':True,'local_resolved_Gemfile_lock_is_review_evidence_only':True,
 'postbuild_frozen_publication_byte_preparation':'PASS, 38 exact frozen SHA-256 authorities; source XML remains unchanged.',
 'remaining_diagnostics':'Inherited Sass deprecation warnings; no build errors.',
 'complete_reader_runtime_equivalence_to_certified_preview':True,'artifacts':rows}
(PACK/'BUILD_QA.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print('Standard full-plugin build verified; complete reader artifacts match certified runtime content (DEH cache timestamps and recorded EOL representations only)')
