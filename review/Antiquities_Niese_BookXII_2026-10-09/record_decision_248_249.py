"""Record the human adjudication and recompute adjoining extents, without editing XML."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Antiquities_Niese_Batch_12_13_2026-10-09'))
from record_review import *
d=packet(12);c=json.loads((d/'LATIN_REVIEW_CHOICES.json').read_text(encoding='utf8'))
notices={
246:'The dating material corresponding to Greek XII.248 (Olympiad 153, day 25 and the named month) occurs here in Latin paragraph latin-book12-num246, before “Capit eam sine conflictione”. The Latin attaches it to the first capture. See XII.248 for the displaced correspondence.',
247:'This Latin interval contains the opening counterpart of Greek XII.247. Its ending, “multasque abeo auferens pecunias ad antiochiam reuersus est”, resumes later within the Latin interval displayed at XII.249. The transmitted order is preserved.',
248:'No independent Latin interval. Dating material corresponding to this Greek section survives earlier within XII.246, in latin-book12-num246: “centesima quinquagesima tertia olimpiade. uicesimo et quinto mensis chasleu quem mache dones appelleon nominant.” This is displaced correspondence. The distinct second-capture notice has no identifiable counterpart in the reviewed Latin context. Greek and English remain independently accessible.',
249:'Partial and reordered correspondence. The opening clause “nec non etiam eos qui portas aperientes ciuitatem ei tradiderunt propter templi diuitias interficit” corresponds to Greek XII.249. The following “multasque abeo auferens pecunias ad antiochiam reuersus est” resumes Greek XII.247. The entire displayed Latin interval does not correspond exclusively to Greek XII.249; the transmitted order is preserved.'}
for n in [246,247,248,249]:
 c[str(n)]['status']='USER_APPROVED';c[str(n)]['notice']=notices[n];c[str(n)]['limits']=notices[n];c[str(n)]['correspondence']='DISPLACED_NO_INDEPENDENT_INTERVAL' if n==248 else 'PRESENT_WITH_RECORDED_ALIGNMENT_LIMITS'
c['249']['phrase']='nec non etiam eos'
c['249']['paragraph']='latin-book12-num246'
save(d/'LATIN_REVIEW_CHOICES.json',c)
save(d/'EDITORIAL_DECISIONS.json',{'date':'2026-10-09','source':'Direct user reply to decision packet XII.248–249','decision':'Approve A, conditional on the correspondence documented in the packet. XII.248 has no independent Latin interval; XII.249 starts at nec non etiam eos. Explicit reciprocal qualifications required at 246,247,248,249; preserve all wording, punctuation, markup and transmitted order; Greek and English remain independently addressable.','condition_verification':'The full Latin clause nec non etiam eos qui portas aperientes ciuitatem ei tradiderunt propter templi diuitias interficit explicitly states killing those who opened the gates and handed over the city, for the temple wealth. Greek249 states not sparing those who admitted him because of the temple wealth. Both full clauses and adjoining 242–256 context are in DECISION_XII_248_249.json. Condition satisfied.','approved_notices':notices,'corpus_change':'None at this adjudication checkpoint; implementation follows completed review.'})
apply(12)
