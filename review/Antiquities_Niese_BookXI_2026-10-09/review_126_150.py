import sys
sys.dont_write_bytecode=True
from review_batch import cuts,save,D
import json
cuts([
 (126,120,'Uasa etiam','Vessels and royal expenses.'),(127,120,'Scripsi etiam','Officials, divine anger and grain.'),(128,120,'ut sacerdotibus','Clerical exemption follows grain instruction; dependent ut retained.'),
 (129,120,'Sed etiam tu','Judges and legal instruction.'),(130,120,'Et siquis','Offences and sanctions.'),(131,131,'Tunc esdras','Inherited reception and circulation.'),
 (132,131,'Hi uero','Goodwill and journey plans.'),(133,131,'Totus autem','Two tribes and ten tribes census.'),(134,131,'Uenerunt etiam','Priests, gathering and fast.'),
 (135,131,'Nam esdras','No escort, departure and arrival.'),(136,131,'et ilico','Treasury and vessel census.'),(137,131,'Cumque ezras','Sacrifices; transmitted thirteen bulls against Greek twelve retained.'),
 (138,131,'Regis quoque','Letters and assistance.'),(139,139,'Haec igitur','Inherited closing appraisal.'),(140,139,'quem pauco','Complaint about foreign marriages; retain transmitted dependent syntax.'),
 (141,139,'petebant ut','Appeal and Ezra grief.'),(142,139,'Exeastimans quia','Anticipated resistance and gathering mourners.'),(143,139,'Cum autem ezras','Prayer opening and ancestral memory.'),
 (144,139,'Rogabat uero','Prayer and mercy; Latin compresses restoration and Persian compassion clauses, while retaining an independent prayer counterpart.'),
 (145,145,'qui post quam','Inherited prayer-end and Achonius advice.'),(146,145,'Flexus igitur','Oaths.'),(147,145,'Suscipiens uero','Withdrawal and fast.'),
 (148,145,'Facta autem','Assembly proclamation. Latin lacks Greek non-arrival negation in qui ante...occurrissent; retain and qualify.'),(149,145,'Cumque in superiori','Assembly and address; transmitted zeal/cold difference retained.'),(150,145,'Cumque omnes','Consent and winter scheduling.')
])
x=json.loads((D/'review_choices.json').read_text(encoding='utf8'));x['qualified'].update({'144':'compressed-correspondence','148':'transmitted-negation-divergence'});save('review_choices.json',x)
