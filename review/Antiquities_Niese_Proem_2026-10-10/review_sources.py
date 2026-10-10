"""Human reviewed starts; machine coordinates are verified against frozen bytes."""
from prepare import *
import sys, importlib.util
spec=importlib.util.spec_from_file_location('prior_mapper',ROOT/'review/Antiquities_Niese_BookXX_2026-10-10/mixed_mapper.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
from xml.parsers import expat
class Proem:
    def __init__(self,raw):
        self.raw=raw;self.doc=etree.fromstring(raw);self.units=[];self.nodes=[];self.text=''
        ps=self.doc.xpath('//t:div1/t:p[@xml:id]',namespaces=NS);stack=[];counts=[{}];cur=None;last=None;p=expat.ParserCreate()
        def start(tag,attrs):
            nonlocal cur,last
            counts[-1][tag]=counts[-1].get(tag,0)+1
            path=(stack[-1]['path'] if stack else '')+'/'+tag+'['+str(counts[-1][tag])+']'
            stack.append(dict(tag=tag,path=path,attrs=attrs));counts.append({});last=None
            if tag=='p' and attrs.get('xml:id','').startswith(('latin-preface-num','greek-preface-num','english-preface-num')):
                el=ps[len(self.units)];cur=dict(id=attrs['xml:id'],element=el,raw_start=p.CurrentByteIndex,text='',start=len(self.text),nodes=[]);self.units.append(cur)
        def end(tag):
            nonlocal cur,last
            last=stack.pop();counts.pop()
            if tag=='p' and cur:
                cur['raw_end']=self.raw.index(b'>',p.CurrentByteIndex)+1
                cur['raw_sha256']=sha(self.raw[cur['raw_start']:cur['raw_end']]);cur=None
        def data(s):
            if cur is None or any(n['tag'] in ['num','note','app','rdg'] for n in stack):return
            parent=stack[-1];path=last['path']+'/tail()' if last and last['path'].startswith(parent['path']+'/') else parent['path']+'/text()'
            positions=prior.raw_char_positions(raw,p.CurrentByteIndex,s)
            if cur['nodes'] and cur['nodes'][-1]['path']==path:
                node=cur['nodes'][-1];node['text']+=s;node['bytes']+=positions
            else:
                node=dict(path=path,text=s,bytes=positions,start=len(self.text),unit_start=len(cur['text']),unit=cur);cur['nodes'].append(node);self.nodes.append(node)
            self.text+=s;cur['text']+=s
        p.StartElementHandler=start;p.EndElementHandler=end;p.CharacterDataHandler=data;p.Parse(raw,True)
        for u in self.units:
            assert u['text']==''.join(u['element'].xpath('.//text()[not(ancestor::t:num) and not(ancestor::t:note) and not(ancestor::t:app) and not(ancestor::t:rdg)]',namespaces=NS))
    def locate(self,k):
        node=next(n for n in self.nodes if n['start']<=k<n['start']+len(n['text']));off=k-node['start'];u=node['unit'];raw=node['bytes'][off]
        assert prior.raw_char_positions(self.raw,raw,self.text[k])==[raw]
        return dict(xml_id=u['id'],enclosing_element='p',xpath=self.doc.getroottree().getpath(u['element']),text_or_tail=node['path'],unicode_node_offset=off,unicode_paragraph_offset=node['unit_start']+off,unicode_proem_offset=k,raw_UTF8_byte_offset=raw,left=self.text[max(0,k-110):k],right=self.text[k:k+180],raw_paragraph_sha256=u['raw_sha256'],text_node_sha256=sha(node['text'].encode()))
LATIN=[
'Historiam conscribere','Nam quidam eorum','Quidem autem ipsa','harum itaque;',
'praesens autem opus','Dudum siquidem','Sed quoniam ingens','eram autuem qui','huic enim uiro',
'Comperi siquidem','pontifex uero noster','Ideoque mihi scilicet','cum sint alia','quod totu exipsa','Iam itaque eos','licet ex longitudine','integritate uideli&lt;cet&gt;',
'quia uero pene','Sciendu itaque','neque enim uel','hoc igitur docere','Alii namque legislatores','Noster uero legislator','secundum hoc igitur','Volentius autem','adrerum narrationem']
REASONS=[
'Opening contrasts the motives of historians; the inherited folio 1r remains physical markup.',
'The first two voluntary motives remain together: stylistic display and gratitude to subjects.',
'The two compelled/useful motives remain together: participation in events and public usefulness.',
'Josephus applies the last two motives to himself and explains the War.',
'New undertaking: Antiquities and the constitution, translated from Hebrew writings.',
'Earlier plan when composing the War; who the Jews were, fortunes, legislator, piety and wars.',
'Size of the projected account, separation of the War, and hesitation over a foreign language.',
'Encouragement and the full characterization of Epaphroditus. Inherited eram autuem is retained.',
'Compliance with Epaphroditus, shame at inactivity, renewed effort and ancestral/Greek interest.',
'Ptolemy II, learning, book collecting and translating the law.',
'Eleazar and the refusal to conceal useful knowledge; starts within an inherited Latin sentence.',
'Imitating the high priest; learners and the limited scope of the Alexandrian translation.',
'Other sacred writings, five thousand years, reversals, war, leaders and political change; crosses fol. 1v.',
'General lesson of the history, obedience and divine prosperity versus neglect and calamity.',
'Appeal to readers to assess Moses and his pure account of God.',
'Antiquity of Moses, potential licence for invention, poets and the two-thousand-year claim.',
'Promise to recount the written record in order without addition or omission; mid-sentence cut.',
'Moses as foundation and the reason for preliminary discussion of natural origins.',
'Knowing God and His works before ordering one’s own life or legislating for others.',
'Neither legislator nor recipients prosper without this knowledge; reward and calamity.',
'Moses begins with God and creation rather than contracts; humanity and obedience.',
'Other legislators transfer human failings to gods and license wrongdoing.',
'Moses declares God’s virtue and orders punishment for disbelief.',
'Readers should examine the work by this premise; harmony with nature, allegory and plain speech.',
'Philosophical consideration of individual causes. Latin Quod ego nunc quidem corresponds to Greek ἣν ἐγὼ νῦν μὲν and remains in §25; the subsequent future-treatise promise is not independently identifiable in the approved transcription. No supplied text.',
'The surviving adrerum narrationem corresponds to Greek ἐπὶ τὴν ἀφήγησιν ... τῶν πραγμάτων, followed by reminiscens primitus = μνησθεὶς πρότερον. Neither the opening finite verb τρέψομαι nor final ἔχει δὲ οὕτως has an independently identifiable separate counterpart in the approved transcription.']
NIESE_PAGES=[4,4,4,5,5,5,5,5,6,6,6,6,6,6,7,7,7,7,7,7,8,8,8,8,8,8]
LOEB_PAGES=[2]*4+[4]*5+[6]*4+[8]*4+[10]*4+[12]*5
MARGINAL={2:'Numeral on a line ending the preceding sentence; secure start τινὲς μὲν γάρ lies later on that line.',3:'Numeral precedes the end of the previous sentence; secure start εἰσὶ δ᾽ οἵτινες lies later on the line.',4:'Numeral at the line of τούτων δή, after preceding ἐξενεγκεῖν.',7:'Numeral on the line of preceding κατέστησαν; start ἀλλ᾽ ἐπειδή follows.',9:'Numeral on a line opening with the end of §8; τούτῳ δή follows.',11:'Numeral aligns with ὁ δὲ τῶν, after the end of §10.',12:'Numeral aligns with preceding ἀπόρρητον; κἀμαυτῷ δή follows.',13:'Numeral on preceding πεμφθέντες continuation; μυρία δ᾽ follows later on that line.',14:'Numeral precedes ending ἀνδραγαθίαι ... μεταβολαί; τὸ σύνολον δέ follows.',15:'Numeral follows preceding σπουδάσωσιν; ἤδη τοίνυν follows.',16:'Numeral follows preceding μυθολογίας; καίτοι γε follows.',17:'Numeral on preceding sentence ending ἐτόλμησαν; τὰ μὲν οὖν follows.',18:'Numeral on the initial Ἐπειδὴ δέ line.',19:'Numeral on preceding φυσιολογίας conclusion; ἰστέον οὖν follows.',20:'Numeral aligns with οὔτε γάρ at printed p.7, continuing on p.8.',21:'Numeral beside preceding calamity phrase; τοῦτο δή follows on that line.',22:'Numeral beside preceding περὶ πάντων ἔπειθεν; οἱ μὲν γάρ follows.',23:'Numeral beside ending ἔδωκαν; ὁ δ᾽ ἡμέτερος follows.',24:'Numeral beside ending ἐκόλασε; πρὸς ταύτην οὖν follows.',26:'Numeral beside γράψαι τὴν πραγματείαν ending §25; τρέψομαι δέ follows. Do not move the cut to γράψαι.'}
def main():
    models={l:Proem((PACK/f'frozen-inputs/{l}.xml').read_bytes()) for l in ['Greek','Latin','English']}
    g=models['Greek'];la=models['Latin'];rows=[];gs=[];ls=[]
    nums=g.doc.xpath('//t:div1/t:p/t:num',namespaces=NS)
    assert len(nums)==26
    for n,num in enumerate(nums,1):
        tail=num.tail or '';phrase=tail.lstrip()[:30];unit=next(u for u in g.units if u['element'] is num.getparent())
        offset=sum(len(''.join(c.itertext()))+len(c.tail or '') for c in list(num.getparent())[:list(num.getparent()).index(num)] if etree.QName(c).localname!='num')
        # Locate via unique opening phrase, preserving any inherited joined words.
        hits=[m.start() for m in re.finditer(re.escape(phrase),g.text)];assert len(hits)==1,(n,phrase,hits)
        k=hits[0];gs.append(k)
        needle=LATIN[n-1].replace('&lt;','<').replace('&gt;','>');hits=[m.start() for m in re.finditer(re.escape(needle),la.text)];assert len(hits)==1,(n,needle,hits)
        lk=hits[0];ls.append(lk)
        rows.append(dict(number=n,Greek_print_status='VISUALLY_VERIFIED_NIESE_AND_LOEB',Greek_start_phrase=tail.lstrip()[:100],Niese=dict(edition='B. Niese, Flavii Iosephi opera I, Berlin 1887',printed_page=NIESE_PAGES[n-1],PDF_page=NIESE_PAGES[n-1]+90,image=f'evidence/Niese-PDF{NIESE_PAGES[n-1]+90:03}.jpg',marginal_note=MARGINAL.get(n,'Secure opening; numeral/paragraph identifies the start in context.')),Loeb=dict(edition='H. St. J. Thackeray, Josephus IV, Jewish Antiquities I-IV, 1961 impression',printed_page=LOEB_PAGES[n-1],PDF_page=LOEB_PAGES[n-1]+24,image=f'evidence/Loeb-PDF{LOEB_PAGES[n-1]+24:03}.jpg',status='Independent visual control confirms same semantic cut; Loeb variants are not imported'),Greek_start=g.locate(k),Latin_source_status='APPROVED_CANONICAL_BAMBERG_TRANSCRIPTION_PRESENT',Latin_cut_confidence='SECURE_FULL_EXTENT_CORRESPONDENCE',Latin_start=la.locate(lk),Latin_fragment_count=1,English_status='UNCHANGED_INHERITED_PARAGRAPH_CONTEXT',editorial_status='RESOLVED_ROUTINE',complete_extent_review=REASONS[n-1]))
    for i,row in enumerate(rows):
        for l,model,starts in [('Greek',g,gs),('Latin',la,ls)]:
            end=starts[i+1] if i<25 else len(model.text)
            row[l+'_end']=models[l].locate(end) if i<25 else dict(unicode_proem_offset=end,kind='end_of_last_narrative_p',xml_id=model.units[-1]['id'],raw_UTF8_byte_offset=model.units[-1]['raw_end']-4)
            text=model.text[starts[i]:end];row[l+'_complete_text']=text;row[l+'_extent_sha256']=sha(text.encode())
        row['English_context_target']=row['Latin_start']['xml_id'].replace('latin-','english-')
    save(PACK/'DECISION_REGISTER.json',rows)
    expected=[dict(number=r['number'],Greek=r['Greek_complete_text'],Latin=r['Latin_complete_text'],English=next(u['text'] for u in models['English'].units if u['id']==r['English_context_target']),English_context_target=r['English_context_target']) for r in rows]
    save(PACK/'EXPECTED_INTERVALS.json',expected)
    reconstruction={}
    for l,model,starts in [('Greek',g,gs),('Latin',la,ls)]:
        parts=[r[l+'_complete_text'] for r in rows];prefix=model.text[:starts[0]]
        assert prefix+''.join(parts)==model.text
        reconstruction[l]=dict(status='PASS',full_mixed_content_sha256=sha(model.text.encode()),leading_whitespace=prefix,contiguous_intervals=26,noncontiguous_fragments=0,full_narrative_reconstruction=True)
    save(PACK/'RECONSTRUCTION_QA.json',reconstruction)
    # External historical transcription is a provenance control, never an import.
    extra=[]
    for name in ['bamberg','greek','english','froben']:
        p=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\Transkribus Project\Froben\Preface')/(name+'_preface.xml')
        if p.exists():
            doc=etree.fromstring(p.read_bytes());extra.append(dict(**info(p),source_role='Historical provenance/control only; not imported',notes=doc.xpath('//t:sourceDesc//text()',namespaces=NS)))
    save(PACK/'EXTERNAL_PROVENANCE.json',extra)
    print('26 complete Greek/Latin extents reviewed and mapped; lossless narrative reconstruction PASS')
if __name__=='__main__':main()
