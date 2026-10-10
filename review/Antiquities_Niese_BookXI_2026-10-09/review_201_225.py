import sys,json
sys.dont_write_bytecode=True
from review_batch import cuts,pages,save,D
cuts([
 (201,195,'Cumque putasset','Readiness and daily admission.'),(202,195,'qui post concubitum','Return, Esther marriage and chronology; transmitted twelfth year differs from Greek seventh.'),
 (203,195,'Destinauit autem','Wedding proclamation, feast, crown and concealed origin.'),(204,195,'transiens autem','Mordecai residence and inquiry.'),
 (205,205,'Cumque legem','Inherited access law; Greek armed throne guards are absent from this Latin account.'),(206,205,'se debet itaque','Sceptre and conclusion; preserve transmitted spelling.'),
 (207,207,'Interiecto uero','Inherited conspiracy and report.'),(208,207,'Rex autem','Investigation, execution and record.'),(209,209,'Quo tempore','Inherited Haman honour.'),
 (210,209,'Mardocheum uero','Refusal and anger.'),(211,209,'et punire','Collective vengeance and Amalek.'),(212,209,'Audiens ergo','Accusation speech.'),
 (213,209,'Sed siuis','Destruction proposal.'),(214,209,'Uerum tamen','Compensation; transmitted numerical difference retained.'),(215,215,'Post quam amari','Inherited grant and dispatch.'),
 (216,215,'Rex maximus','Royal salutation, peace and inquiry, including quaerentem autem...quomodo hoc possit impleri.'),(217,215,'unus qui sapientia','Haman answer and hostile description.'),
 (218,215,'Quod cum didicissemus','Latin recap before command is retained with218; no duplication of217.'),(219,215,'quarto decimo','Date and peace clause.'),(220,215,'Hoc per ciuitates','Delivery, preparations and turmoil.'),
 (221,221,'quod mardocheus','Inherited mourning and barred entry.'),(222,221,'idem etiam','General mourning and Esther clothing mission.'),(223,221,'quo nolente','Refusal and eunuch inquiry.'),
 (224,221,'Tunc mardocheus','Cause, decree and money.'),(225,221,'harum etiam','Copy, petition and Haman explanation.')
])
x=json.loads((D/'review_choices.json').read_text(encoding='utf8'));x['qualified'].update({'202':'transmitted-chronological-divergence','205':'partial-correspondence','218':'expanded-recap'});save('review_choices.json',x)
pages([
 (110,list(range(174,178)),'Left narrative margin:174 V.8;175 prior assassination-clause ending;176 prior withdrawal-ending line;177 prior wall-ending line.'),
 (111,list(range(178,185)),'Right narrative margin:178 first narrative line;179 duration;180 completion;181 population;182 tithe;183 death;184 VI.1 final line.'),
 (112,list(range(185,189)),'Left narrative margin:185 prior explanation-ending line;186 prior rescue-ending line;187 feast-duration line;188 preceding canopy-ending line.'),
 (113,list(range(189,196)),'Right narrative margin:189 first line;190 queen;191 beauty/refusal line;192 royal anger;193 legal inquiry;194 reply;195 VI.2 near foot.'),
 (114,list(range(196,203)),'Left narrative margin:196 preceding memory line;197 prior affection-ending line;198 previous command-ending line;199 prior rank-ending line;200 care;201 prior census-ending line;202 final narrative line.'),
 (115,list(range(203,208)),'Right narrative margin:203 dispatch;204 Mordecai;205 VI.3;206 prior throne-guard line;207 VI.4 near foot.'),
 (116,list(range(208,214)),'Left narrative margin:208 prior disclosure-ending line;209 VI.5;210 prior honour-ending line;211 preceding refusal-ending line;212 accusation;213 prior universal-hostility ending.')
])
