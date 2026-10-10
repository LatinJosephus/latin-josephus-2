import sys,json
sys.dont_write_bytecode=True
from review_batch import cuts,pages,save,D
cuts([
 (226,221,'Haec cum regina','Access law; Latin hic solus interi mitur lacks Greek negation, retained with a qualification.'),(227,221,'Mardocheus uero','Collective salvation and household warning.'),
 (228,221,'Hester autem','Fast and undertaking.'),(229,229,'Mardocheus autem','Inherited fast and prayer; transmitted non cessit retained.'),(230,229,'Non enim propter','Reason for danger and refusal to honour Haman.'),
 (231,229,'easdem etiam','People prayer and Esther mourning.'),(232,229,'Cibum autem','Fast and eloquence/beauty petition.'),(233,229,'ut ex utroque','Both forms of support and enemy hatred; latter survives in next paragraph before inherited234 label claim.'),
 (234,234,'sic deum per','True234 begins after Nam aman quoque regis odium concitaret, which completes233; visible inherited234 remains internal to233.'),
 (235,234,'etiam cum timore','Dependent fear phrase; the shared approach verb remains in234. Royal attire follows.'),(236,234,'uel auro','Gold, gems, threatening look and collapse.'),
 (237,234,'Rex autem','Changed royal mind and concern.'),(238,234,'Surrexit asella','Embrace, comfort and permission.'),(239,234,'Haec dicens','Sceptre action; transmitted syntax retained.'),
 (240,234,'illa uero respirans','Revival and speech.'),(241,234,'Uix illa','Anxiety and reassurance.'),(242,234,'Hester uero','Invitation and banquet inquiry.'),
 (243,234,'Nihil enim','Promise and deferred request.'),(244,244,'Cumque rex','Inherited Haman joy and anger.'),(245,244,'Tunc ingressus','Household account.'),(246,244,'Dicebat autem','Gallows proposal; Latin fifty cubits versus Greek sixty retained.'),
 (247,244,'Deus autem','Divine reversal and sleeplessness; preceding preparation is compressed into246.'),(248,244,'Qui nolens','Archival reading.'),(249,244,'Cumque detulisset','Previous rewards and conspiracy record.'),(250,244,'Et cum hoc','Royal inquiry into reward and hour.')
])
x=json.loads((D/'review_choices.json').read_text(encoding='utf8'));x['qualified'].update({'226':'transmitted-negation-divergence','229':'transmitted-wording-divergence','233':'cross-paragraph-correspondence','235':'dependent-compressed-correspondence','246':'transmitted-numerical-divergence'});save('review_choices.json',x)
pages([
 (117,list(range(214,218)),'Right narrative margin:214 compensation near top;215 VI.6;216 salutation on previous introduction-ending line;217 prior inquiry-ending line.'),
 (118,list(range(218,224)),'Left narrative margin:218 first line after prior hostile-monarchy clause;219 prior compliance-ending line;220 preceding peace-ending line;221 VI.7;222 preceding attire-ending line;223 refusal near foot.'),
 (119,list(range(224,228)),'Right narrative margin:224 disclosure;225 copy;226 reply;227 Mordecai on preceding salvation-ending line.')
])
