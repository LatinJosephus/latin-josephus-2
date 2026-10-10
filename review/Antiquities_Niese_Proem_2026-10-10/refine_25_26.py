from prepare import *
def main():
    history=PACK/'history/before-final-25-26-refinement';history.mkdir(exist_ok=False)
    names=['DECISION_REGISTER.json','EXPECTED_INTERVALS.json','AUTHORIZED_ADDITIONS.json','IMPLEMENTED_LOCATORS.json','PROEM_BROWSER_QA.json','PLAIN_READER_QA.json','FINAL_PROTECTED_BROWSER.json','READER_FINAL_PRIOR_RESULTS.json','READER_XI_RESULTS.json','CANDIDATE_BUILD.json','FINAL_BUILD.json','BUILD_CONTEXT.json','BYTE_CERTIFICATION.json','PRODUCTION_PRESERVATION.json','BOUNDARIES.csv']
    for name in names:shutil.copyfile(PACK/name,history/name)
    p=ROOT/'assets/xml/antiquities/Latin/preface.xml';raw=p.read_bytes();marker=b'<milestone unit="niese" n="26" xml:id="niese-latin-preface-26"/>'
    assert raw.count(marker)==1
    old=marker+b'Quod ego nunc quidem adrerum narrationem';new=b'Quod ego nunc quidem '+marker+b'adrerum narrationem'
    assert raw.count(old)==1;raw=raw.replace(old,new);p.write_bytes(raw)
    import review_sources
    review_sources.main()
    rows=json.loads((PACK/'DECISION_REGISTER.json').read_text(encoding='utf-8'));additions=json.loads((PACK/'AUTHORIZED_ADDITIONS.json').read_text());a=next(a for a in additions if a['number']==26 and a.get('role')!='exclusive_narrative_end');a['offset']=rows[-1]['Latin_start']['raw_UTF8_byte_offset'];save(PACK/'AUTHORIZED_ADDITIONS.json',additions)
    regpath=ROOT/'assets/xml/antiquities/niese/preface.json';registry=json.loads(regpath.read_text(encoding='utf-8'))
    registry['sections'][24]['Latin']['note']='The future-treatise promise is not independently identifiable in the present Bamberg transcription. The surviving opening “Quod ego nunc quidem” is retained.'
    registry['sections'][25]['Latin']['note']='The present Bamberg transcription has no separately identifiable equivalent of the Greek opening verb or final transition formula; its surviving narrative text is retained.'
    save(regpath,registry)
    control=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\Transkribus Project\Froben\Preface\froben_preface.xml')
    doc=etree.fromstring(control.read_bytes());text=' '.join(doc.xpath('//t:body//text()',namespaces=NS));phrase=text[text.index('Volentibus autem'):]
    save(PACK/'FINAL_25_26_SOURCE_REVIEW.json',dict(status='RESOLVED_SECURE_SEMANTIC_CUT',old_cut='Before Quod ego nunc quidem',adopted_cut='Before adrerum narrationem',primary_Greek_25='ἣν ἐγὼ νῦν μὲν ὑπερβάλλομαι, θεοῦ δὲ διδόντος ἡμῖν χρόνον πειράσομαι μετὰ ταύτην γράψαι τὴν πραγματείαν.',primary_Greek_26='τρέψομαι δὲ ἐπὶ τὴν ἀφήγησιν ἤδη τῶν πραγμάτων μνησθεὶς πρότερον',approved_Latin='Volentius autem etiam causas rerum singulas considerare contemplatio multa nimis et ualde philosopha repperitur. Quod ego nunc quidem | adrerum narrationem reminiscens primitus eorum quae demundi fabrica moses dixit, haec autem in sacris libris [comperi] ita conscripta',decision='Quod ego nunc quidem is the surviving opening of Greek §25’s relative clause, not the opening of §26. Keep those words with §25 and begin §26 at the independently identifiable narrative phrase adrerum narrationem. No modern Latin words or implied verbs supplied.',Froben_control=dict(source=info(control),text=phrase,role='Independent semantic comparison only; cannot establish Bamberg manuscript readings or justify a content import'),cause_neutral_status='Missing material is not independently identifiable in approved transcription. No assertion of manuscript loss versus version compression versus transcription omission.',pending_editorial_question=False))
    print('Moved only §26 Latin marker after Quod ego nunc quidem; all source words preserved')
if __name__=='__main__':main()
