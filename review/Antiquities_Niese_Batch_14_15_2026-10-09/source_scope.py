"""Validated assignment scope on top of the accepted mixed-content byte mapper.

Greek chronological summaries embedded in first narrative p remain byte-exact,
but are outside the narrative stream. All other accepted exclusions are unchanged.
"""
from pathlib import Path
import sys,re,bisect,copy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book as AcceptedBook, digest, fixtures
class Book(AcceptedBook):
    def __init__(self,path=None,raw=None):
        super().__init__(path=path,raw=raw)
        self.excluded_prefix=None;self.scope_exclusions=[]
        count=self.stream.index('. ')+2 if self.stream.startswith('περιέχει ἡ βίβλος χρόνον ἐτῶν ') else 0
        if count:self.excluded_prefix=dict(reason='source chronological contents conclusion before printed body I.1',text=self.stream[:count],source_locator=super().locate(0),source_codepoints=count)
        originals=self.nodes;kept=[];offset=0;unit_offsets={u['index']:0 for u in self.units}
        for node in originals:
            original_offset=node['book_start']; trim=count if original_offset==0 and count else 0
            xpath=re.sub(r'(?<=/)([A-Za-z][A-Za-z0-9]*)(?=\[)',r't:\1',node['path'].rsplit('/',1)[0])
            owner=self.tree.xpath(xpath,namespaces={'t':'http://www.tei-c.org/ns/1.0'})[0]
            ancestors=[owner,*owner.iterancestors()] if node['path'].endswith('/text()') else list(owner.iterancestors())
            marginal=next((x for x in ancestors if x.tag.endswith('}add') and (x.get('place') or '').startswith('margin')),None)
            if marginal is not None:
                value=''.join(marginal.itertext()).strip()
                if re.fullmatch(r'[IVXLCDM]+|[.·]+|nota|ss?',value):
                    self.scope_exclusions.append(dict(reason='source marginal label or annotation',text=node['text'],text_node_path=node['path'],raw_start=node['raw_positions'][0]));continue
            unit=self.units[node['unit']-1]
            if unit['id']=='latin-book15-num11' and re.match(r'^II\. ',node['text']):
                trim=4;self.scope_exclusions.append(dict(reason='literal source chapter label',text='II. ',text_node_path=node['path'],raw_start=node['raw_positions'][0]))
            if unit['id']=='latin-book14-num80' and node['text'].startswith(' X. '):
                trim=4;self.scope_exclusions.append(dict(reason='literal source chapter label',text=' X. ',text_node_path=node['path'],raw_start=node['raw_positions'][0]))
            if unit['id']=='latin-book15-num121' and node['text'].startswith('VII '):
                trim=4;self.scope_exclusions.append(dict(reason='literal source chapter label',text='VII ',text_node_path=node['path'],raw_start=node['raw_positions'][0]))
            n=dict(node,original_node_prefix=trim,source_unit_start=node['unit_start'],text=node['text'][trim:],raw_positions=node['raw_positions'][trim:],book_start=offset,unit_start=unit_offsets[node['unit']])
            if not n['text']:continue
            offset+=len(n['text']);unit_offsets[node['unit']]+=len(n['text']);kept.append(n)
        self.nodes=kept;self.stream=''.join(n['text'] for n in kept)
        all_positions=[v for n in kept for v in n['raw_positions']]
        for unit in self.units:
            unit['nodes']=[n for n in kept if n['unit']==unit['index']]
            unit['text']=''.join(n['text'] for n in unit['nodes'])
            unit['book_start']=bisect.bisect_left(all_positions,unit['raw_start'])
        for label in self.labels:
            label['book_offset']=bisect.bisect_left(all_positions,label['raw_start'])
            label['unit_offset']=label['book_offset']-self.units[label['unit']-1]['book_start']
        self.scope_prefix_codepoints=count
    def locate(self,offset):
        loc=super().locate(offset)
        # DOM offsets refer to original text/tail nodes; stream offsets exclude labels.
        node=next(n for n in self.nodes if n['book_start']<=offset<n['book_start']+len(n['text']))
        loc['node_offset']+=node['original_node_prefix']
        loc['source_unit_offset']=node['source_unit_start']+loc['node_offset']
        return loc
