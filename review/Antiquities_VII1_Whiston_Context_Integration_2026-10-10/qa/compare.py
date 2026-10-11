from pathlib import Path
import json,csv
T=Path(r'C:/workspace/Antiquities-VII1-Whiston-Integration-runtime-20261010');b=json.loads((T/'baseline-NIESE.json').read_text());c=json.loads((T/'candidate-final-NIESE.json').read_text());assert b['result']==c['result']=='COMPLETE';assert not b['errors'] and not c['errors'];assert len(b['rows'])==len(c['rows'])==7376;assert b['books']==c['books'];changes=[];matrix=[]
for x,y in zip(b['rows'],c['rows']):
 assert (x['book'],x['n'])==(y['book'],y['n']);assert x['duplicates']==y['duplicates']
 for lang in ['Latin','Greek']:assert x['languages'][lang]==y['languages'][lang],(x['book'],x['n'],lang)
 if x!=y:changes.append({'book':y['book'],'n':y['n'],'before':x['languages']['English'],'after':y['languages']['English']})
 row={'book':y['book'],'niese':y['n'],'route':'/antiquities/?book='+y['book']+'&niese='+str(y['n']),'result':'PASS','intended_English_recovery':x!=y,'duplicates_unchanged':True}
 for lang in ['Latin','Greek','English']:
  for key in ['DOM','text','type','ids','notes']:row[lang+'_'+key]=json.dumps(y['languages'][lang][key],ensure_ascii=False) if key in ['ids','notes'] else y['languages'][lang][key]
  row[lang+'_matches_fresh_baseline']=x['languages'][lang]==y['languages'][lang]
 matrix.append(row)
assert len(changes)==1 and changes[0]['book']=='7' and changes[0]['n']==1
ch=changes[0];assert ch['before']['ids']==[] and ch['after']['ids']==['english-book07-num1'];assert ch['before']['notes']==ch['after']['notes'];assert ch['after']['type']=='niese-context'
with (T/'EXHAUSTIVE_NIESE_MATRIX.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(matrix[0]),lineterminator='\n');w.writeheader();w.writerows(matrix)
result={'result':'PASS','rows':7376,'Proem':26,'Antiquities_I_XX':7350,'menus_identical':True,'Latin_Greek_all_rows_identical':True,'unchanged_rows':7375,'intended_changes':changes,'errors':[],'books':[ {k:v for k,v in x.items() if k!='menu'} for x in c['books']]}
(T/'NIESE_COMPARISON.json').write_text(json.dumps(result,indent=2)+'\n')
focus={'preface':[1,24,25,26],'11':[302,311,312,313,325,326,327,341,342,343,347],'16':[294,295,350,351,352,353,354,355,356],'17':[24,25,75,76,299],'18':[7,94,215,216,217,218,257],'19':[188,292],'20':[1,25,26,*range(27,37),37,38,51,57,58,59,60,129,200,215,237,238,239,240,241,242,259,260,261,262,263,264,265,266,267,268]}
protected=[{'book':y['book'],'n':y['n'],'result':'PASS','all_language_DOM_text_ID_notice_hashes_equal_baseline':True,'actual':y} for x,y in zip(b['rows'],c['rows']) if y['n'] in focus.get(y['book'],[])]
assert all(x==y for x,y in zip(b['rows'],c['rows']) if y['n'] in focus.get(y['book'],[]));assert c['books'][-1]['last']==268
(T/'EXCEPTION_PROTECTION.json').write_text(json.dumps({'result':'PASS','method':'Actual integrated uninstrumented reader snapshots equal independently rerun frozen canonical baseline, for every language, fragment ID, notice and duplicate state. Positive underlying editorial decisions are inherited; this verifies preservation, not fresh adjudication.','XX_269_absent':True,'rows':protected},indent=2)+'\n')
print('PASS: 7376 identities; sole VII.1 English recovery; '+str(len(protected))+' exceptional controls unchanged.')
