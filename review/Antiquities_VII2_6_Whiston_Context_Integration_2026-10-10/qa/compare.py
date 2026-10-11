from pathlib import Path
import json,csv
T=Path(r'C:/workspace/Antiquities-VII2-6-Whiston-Integration-runtime-20261010');b=json.loads((T/'baseline-NIESE.json').read_text());c=json.loads((T/'candidate-final-NIESE.json').read_text());assert b['result']==c['result']=='COMPLETE';assert len(b['rows'])==len(c['rows'])==7376 and not b['errors'] and not c['errors'];assert b['books']==c['books'];changes=[];matrix=[]
for x,y in zip(b['rows'],c['rows']):
 assert (x['book'],x['n'])==(y['book'],y['n']);assert x['duplicates']==y['duplicates']
 assert all(x['languages'][l]==y['languages'][l] for l in ['Latin','Greek'])
 if x!=y:changes.append({'book':y['book'],'n':y['n'],'before_English':x['languages']['English'],'after_English':y['languages']['English']})
 row={'book':y['book'],'niese':y['n'],'route':'/antiquities/?book='+y['book']+'&niese='+str(y['n']),'result':'PASS','intended_English_recovery':x!=y,'duplicates_unchanged':True}
 for l in ['Latin','Greek','English']:
  row[l+'_matches_baseline']=x['languages'][l]==y['languages'][l]
  for key in ['DOM','text','type','ids','notes']:row[l+'_'+key]=json.dumps(y['languages'][l][key],ensure_ascii=False) if key in ['ids','notes'] else y['languages'][l][key]
 matrix.append(row)
assert [(x['book'],x['n']) for x in changes]==[('7',n) for n in range(2,7)]
for x in changes:assert x['before_English']['ids']==[] and x['after_English']['ids']==['english-book07-num1'] and x['before_English']['notes']==x['after_English']['notes'] and x['after_English']['type']=='niese-context'
with (T/'EXHAUSTIVE_NIESE_MATRIX.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(matrix[0]),lineterminator='\n');w.writeheader();w.writerows(matrix)
result={'result':'PASS','rows':7376,'Proem':26,'Antiquities_I_XX':7350,'menus_identical':True,'Latin_Greek_all_rows_identical':True,'unchanged_rows':7371,'intended_changes':changes,'VII1_English_entire_DOM_unchanged':True,'VII7_English_entire_DOM_unchanged':True,'errors':[],'books':[{k:v for k,v in x.items() if k!='menu'} for x in c['books']]};(T/'NIESE_COMPARISON.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
focus={'preface':[1,24,25,26],'11':[302,311,312,313,325,326,327,341,342,343,347],'16':[294,295,350,351,352,353,354,355,356],'17':[24,25,75,76,299],'18':[7,94,215,216,217,218,257],'19':[188,292],'20':[1,25,26,*range(27,37),37,38,51,57,58,59,60,129,200,215,237,238,239,240,241,242,259,260,261,262,263,264,265,266,267,268]};protected=[{'book':y['book'],'n':y['n'],'result':'PASS','all_DOM_text_ID_notice_hashes_equal_fresh_baseline':True,'actual':y} for x,y in zip(b['rows'],c['rows']) if y['n'] in focus.get(y['book'],[])];assert all(x==y for x,y in zip(b['rows'],c['rows']) if y['n'] in focus.get(y['book'],[]));assert c['books'][-1]['last']==268
(T/'EXCEPTION_PROTECTION.json').write_text(json.dumps({'result':'PASS','method':'Preservation of all observed baseline exceptional content, fragments and notices. Fresh complete actual UI comparison; no new scholarly adjudication or facsimile inspection.','XX_269_absent':True,'rows':protected},indent=2)+'\n',encoding='utf-8',newline='\n');print('PASS 7376; exactly five English recoveries; all Latin/Greek and '+str(len(protected))+' exceptional controls unchanged.')
