import sys
sys.dont_write_bytecode=True
from review_batch import cuts,pages,save,D
import json
cuts([
 (51,49,'et non possumus','Dependence on beauty and abandonment of riches.'),(52,49,'patres et altricem','Family, country and life abandoned; rhetorical bridge compressed.'),
 (53,49,'Nonne laborantes','Labour and earnings delivered to wives.'),(54,49,'regem quoque','Apame and royal submission; transmitted damaged syntax retained.'),
 (55,55,'Post haec','Inherited truth speech; omission of sun noun retained, not supplied.'),(56,55,'in super et cetera','Mortality versus immortal truth.'),
 (57,57,'Cum terminasset','Inherited response, applause and further reward.'),(58,57,'Tunc zorobabel','Vow reminder and request.'),
 (59,59,'Rex autem','Inherited royal response and escort orders.'),(60,59,'praeterea mandauit','Timber, city and freedom.'),
 (61,59,'prohibuit que','Exemption, territory, neighbouring villages and construction funds.'),(62,59,'Sacrificari quoque','Sacrifices, garments and instruments.'),
 (63,59,'a quibus domino','Relative continuation from62, city/temple guards, vessels and Cyrus decrees. Dependent opening retained.'),
 (64,59,'his omnibus a rege donatis','Receiving rewards belongs to64 before inherited [III.ix.64]; preserved label is internal, not an executable start.'),
 (65,64,'domino propitio','Dependent invocation follows nisi te in64; printed Greek65 likewise continues preceding prayer. Exact Latin word cut is qualified, with no reconstructed words.'),
 (66,64,'Audientes illi','Thanksgiving and seven-day celebration.'),(67,64,'Postea omnes','Leaders, family, journey and farewell.'),
 (68,68,'atilli','Inherited opening and author explanation. Early displaced singers/camels are separately owned by72.'),
 (69,68,'Summa uero','Census: transmitted figures and age differ; retain all wording.'),(70,68,'Praeter hos','Levites, gatekeepers, servants and uncertain genealogy.'),
 (71,68,'Repulsi uero','Priestly exclusions and genealogy.'),(72,68,'Mancipiorum uero','First canonical portion is servants; earlier singers/camels form second portion; pack animals third.'),
 (73,68,'Dux uero','Leaders and contributions.'),(74,68,'Sacerdotes autem','Settlement and return to villages.'),(75,75,'Cumque septimus','Inherited opening: summons, ending before construction clause.')
])
x=json.loads((D/'review_choices.json').read_text(encoding='utf8'))
x['additional_fragments']={'72':[["latin-book11-num68","Septem cantores",2,"Displaced singers and camels, physically before69; canonical continuation after servants."],["latin-book11-num68","Subiugalia quinque",3,"Pack animals after singers/camels in Greek72; physical adjacency to servants does not establish continuation rank."]]}
x['qualified']={'63':'dependent-continuation','65':'dependent-continuation','69':'transmitted-numerical-divergence','72':'fragmented-displaced-correspondence'}
save('review_choices.json',x)
pages([
 (87,list(range(57,62)),'Right narrative margin:57 III.7;58 vow reminder in shared line;59 III.8;60 timber instruction (numeral near trim);61 prohibition on final line.'),
 (88,list(range(62,68)),'Left narrative margin:62 sacrifices on shared line;63 on line ending Levites then instruments/relative continuation;64 III.9;65 invocation within quote;66 response;67 farewell ending and next-clause line.'),
 (89,list(range(68,73)),'Right narrative margin:68 III.10;69 census in shared line;70 Levites after preceding totals;71 exclusion after prior genealogy ending;72 servants near foot.')
])
