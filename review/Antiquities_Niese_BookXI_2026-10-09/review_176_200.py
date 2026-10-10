import sys,json
sys.dont_write_bytecode=True
from review_batch import cuts,save,D
cuts([
 (176,174,'Neemias autem nullo','Continued work and guards.'),(177,174,'Unde praecipit','Weapons, shields and signals.'),(178,174,'Ipse autem','Night rounds and necessities.'),
 (179,174,'quos labores','Construction duration: Latin twelve years versus Greek two; retained and qualified.'),(180,174,'Sed post quam','Dedication and hostile response.'),
 (181,174,'Neemias autem in','Priests relocation and housing.'),(182,174,'populum etiam','Tithes, compliance and population.'),(183,174,'Multa etiam','Death and appraisal.'),
 (184,184,'Defuncto uero','Inherited new reign and danger.'),(185,184,'Nam docet','Author explanation.'),(186,184,'Nam cum regnum','Satrapies and feast.'),
 (187,184,'Postea gentes','Seven-day feast and canopy.'),(188,184,'Ministrabatur uero','Vessels and drinking rules.'),(189,184,'Misit autem','Provincial holidays.'),
 (190,184,'Regina quoque','Queen feast and summons.'),(191,184,'quae pro legum','Refusal and repeated summons.'),(192,184,'Unde rex','Royal anger and accusation.'),
 (193,184,'preacepit ergo','Legal consultation and reply.'),(194,184,'Nullo enim','Example, penalty and dismissal.'),(195,195,'At ille','Inherited regret and advice.'),
 (196,195,'et quaereret','Search and replacement.'),(197,195,'hoc flexus','Selection order.'),(198,195,'Cum uero congragatae','Orphan and Mordecai background.'),
 (199,195,'Omnesque primas','Whole transmitted comparative clause belongs to Esther beauty; compressed social-rank wording is not split or emended.'),(200,195,'Quae tradita','Care, cosmetics and transmitted census.')
])
x=json.loads((D/'review_choices.json').read_text(encoding='utf8'));x['qualified']['179']='transmitted-numerical-divergence';save('review_choices.json',x)
p=json.loads((D/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
for row in p['pages']:
 if row['PDF']==107:row['identities']=list(range(157,163));row['position']+=' 162 grief begins on corpse-ending line near foot.'
 if row['PDF']==108:row['identities']=list(range(163,168));row['position']=row['position'].replace('162 prior corpse-ending line;','162 continues unnumbered at top;')
 if row['PDF']==109:row['identities']=list(range(168,174));row['position']+=' 173 appears on final narrative line.'
save('PRINT_OBSERVATIONS.json',p)
