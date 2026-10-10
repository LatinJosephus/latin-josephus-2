"""Persist only individually inspected Greek/Latin cuts and observed printed numerals."""
from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
def save(name,x):(D/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def cuts(items):
    x=json.loads((D/'review_choices.json').read_text(encoding='utf8'))
    for n,p,phrase,note in items:
        value=[f'latin-book11-num{p}',phrase,note]
        assert str(n) not in x['choices'] or x['choices'][str(n)]==value
        x['choices'][str(n)]=value
    save('review_choices.json',x)
def pages(items):
    x=json.loads((D/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
    for pdf,ns,pos in items:
        value=dict(PDF=pdf,print=pdf-72,identities=ns,position=pos,image=f'C:/workspace/Antiquities-Niese-11-runtime-20261009/Niese-body-{pdf:03}.jpg')
        assert not any(p['PDF']==pdf for p in x['pages'])
        x['pages'].append(value)
    x['pages'].sort(key=lambda p:p['PDF']);save('PRINT_OBSERVATIONS.json',x)
if __name__=='__main__':
 cuts([
 (26,26,'Post quam uero','Inherited start; Cambyses response and salutation.'),
 (27,26,'legens missos','Letter record search and rebellious-city account.'),
 (28,26,'Igitur praecipi','Prohibition command.'),(29,26,'cum has litteras','Receipt and journey to stop building.'),
 (30,26,'Quae quidem opera','Nine-year obstruction and Cambyses death; compressed but present.'),
 (31,31,'Post magorum','Inherited start; accession and vow.'),(32,31,'Contigit eodem','Zerubbabel arrival and appointment.'),
 (33,33,'Primo uero','Inherited feast opening; Latin omits separate Median-leader phrase without loss of an independent interval.'),
 (34,33,'Cum autem completis','End of feast, sleepless king and guards.'),(35,33,'permisitque','Rewards and royal kinship promise.'),
 (36,33,'Cum haec igitur','Three questions and return to sleep.'),(37,33,'Lucenscente autem','Morning audience and invitation to respond.'),
 (38,38,'Tuncprimus','Inherited opening and wine proposition.'),(39,38,'nam mutat','Wine changes reason and equates ranks.'),
 (40,38,'conuertit enim','Soul transformation, sorrow, debt and wealth claims.'),(41,38,'et reges magistratusque','Rulers and friendships forgotten; armament against friends.'),
 (42,38,'et cum ad sobrietatem','Sobering and conclusion.'),(43,43,'Post quam haec','Inherited transition to second guard.'),
 (44,43,'et dixit dum','Direct demonstration: humanity controls nature, kings humanity. Introductory et dixit retained here.'),
 (45,43,'unde et bella','Commands in war and delivery of booty.'),(46,43,'Hi quoque','Farmers and tribute.'),
 (47,43,'et quod dixerint','Compliance, luxury and guarded sleep.'),(48,43,'minime enim','Guards cannot leave and closing inference.'),
 (49,49,'isto quoque','Inherited third-guard transition; transmitted wording retained.'),(50,49,'Nam regem','Birth, vines, clothing and households.')
 ])
 pages([
 (81,list(range(25,32)),'Right margin of main narrative:25 near top;26 at II.2;27 in letter after salutation;28 prohibition;29 receipt;30 works delayed;31 at III.1 final line.'),
 (82,list(range(32,37)),'Left main margin:32 arrival clause;33 III.2 feast opening;34 end-of-feast clause;35 reward promise;36 questions on final narrative line.'),
 (83,list(range(37,43)),'Right main margin:37 morning audience;38 III.3 speech opening;39 reason clause;40 transformation;41 rulers/friends;42 sobering near foot.'),
 (84,list(range(43,48)),'Left main margin:43 III.4;44 on shared introductory/direct-speech line;45 shared previous-clause line;46 tribute sentence;47 compliance near foot.'),
 (85,list(range(48,53)),'Right main margin:48 guards near top;49 III.5;50 birth on shared line;51 dependence;52 abandonment of parents near foot.'),
 (86,list(range(53,57)),'Left main margin:53 first narrative line;54 king and concubine;55 III.6 truth speech;56 mortality at lower narrative line.')
 ])
