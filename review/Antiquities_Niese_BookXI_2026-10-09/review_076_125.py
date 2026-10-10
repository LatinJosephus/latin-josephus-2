import sys
sys.dont_write_bytecode=True
from review_batch import cuts,pages,save,D
import json
cuts([
 (76,75,'construxerunt altare','Construction begins after qui sine dilatione, which completes75 summons.'),(77,75,'Caelebrauerunt autem','Feasts and sacrifices through first day of seventh month.'),
 (78,75,'coeperunt etiam','Temple construction, payments, food and timber.'),(79,79,'qui secundo anno','Inherited relative opening and supervision appointments.'),
 (80,79,'Itaque templum','Completion and praise.'),(81,79,'Cum sacerdotes','Older temple recalled; grief.'),(82,79,'Populus uero','Popular joy without comparison.'),
 (83,79,'uincebat uero','Lament outvoices trumpets.'),(84,84,'Cumque dangores','Inherited Samaritan approach and construction request.'),
 (85,84,'Nam non colimus','Shared worship and migration speech.'),(86,84,'Post quam hae','Response rejecting shared building.'),(87,84,'adorare uero','Permission to worship.'),
 (88,88,'Post quam uero','Inherited anger and renewed obstruction.'),(89,88,'Peridem tempus','Officials arrival and questioning.'),(90,88,'Zorobabel et princeps','Reply and first temple history.'),
 (91,88,'sed cum sui','Sin, destruction and captivity.'),(92,88,'Cyrus autem','Restoration decree and vessels.'),(93,88,'hoc enim mandauerat','Instruction to Sabasyrum and unfinished work.'),
 (94,88,'Igitur si uultis','Request for archival inquiry.'),(95,95,'haec dicente','Inherited answer. Latin lacks Greek negation in uetandam iudicauerunt; preserve and explicitly qualify transmitted divergence.'),
 (96,95,'Tunc iudaei','Fear, prophets and continuing work.'),(97,97,'Dario uero','Inherited accusation and Cambyses letters.'),
 (98,97,'Cognoscens rem','Threat and archival search.'),(99,97,'et inuentus est','Ecbatana record and dimensions.'),(100,97,'Sumptus autem','Expenses and vessels.'),
 (101,97,'quorum cura','Officials and permission.'),(102,97,'Iussit quoque','Aid, sacrifices and prayers.'),(103,97,'Eos uero','Penalties and imprecation.'),
 (104,104,'Haec inueniens','Inherited royal reply.'),(105,104,'Igitur epistolam','Compliance and assistance; distinguished from both Bellum IV105 insertions.'),
 (106,104,'et procedebat','Prophecy, kings and seven-year construction.'),(107,104,'Nono autem','Dedication and offerings; transmitted month/figures retained.'),
 (108,104,'Sacerdotes uero','Gatekeepers and porticoes.'),(109,109,'Ueniente autem','Inherited feast gathering.'),(110,109,'Sacrificium etiam','Passover and thanksgiving.'),
 (111,109,'Quibus rebus','Sacrifices and aristocratic government.'),(112,109,'Nam ante captiuitate','Earlier government and chronology.'),(113,109,'haec quidem reductis','Closing summary.'),
 (114,114,'Samaritae uero','Inherited hostility.'),(115,114,'Nam quanta','Withheld subsidies and other harms.'),(116,114,'Placuit igitur','Embassy.'),(117,114,'Cum uero crimina','Royal reception and response.'),
 (118,114,'quae huius modi','Letter introduction, salutation and complaint.'),(119,114,'Uolo igitur','Supply decree and conclusion.'),
 (120,120,'Dario autem','Inherited Xerxes transition.'),(121,120,'Per illus tempus','High priest and Ezra.'),(122,120,'Ad hierosolimam autem','Ezra request.'),
 (123,120,'Rex autem ad','Royal letter and permission.'),(124,120,'quam ad modum','Seven counsellors, inspection and gifts.'),(125,120,'aurum etiam','Precious metals and offerings.')
])
x=json.loads((D/'review_choices.json').read_text(encoding='utf8'));x['qualified']['95']='transmitted-negation-divergence';save('review_choices.json',x)
pages([
 (90,list(range(73,77)),'Left narrative margin:73 on pack-animal line, interpreted leaders clause follows;74 on contribution line before settlement;75 IV.1;76 shared diligence/building line.'),
 (91,list(range(77,82)),'Right narrative margin:77 tabernacles at top;78 construction;79 IV.2;80 completion on shared line;81 final narrative line.'),
 (92,list(range(82,87)),'Left narrative margin:82 joy on previous-ending line;83 lament on previous-ending line;84 IV.3;85 worship speech on shared line;86 response on shared line.'),
 (93,list(range(87,93)),'Right narrative margin:87 permission at top;88 IV.4;89 officials;90 reply;91 destruction;92 Cyrus on final line.'),
 (94,list(range(93,97)),'Left narrative margin:93 Sabases decree on prior-ending line;94 archival request on prior-ending line;95 IV.5;96 fear on shared letter-ending line.')
])
