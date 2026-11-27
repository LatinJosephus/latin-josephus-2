import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('extract_froben_bellum',HERE.parent/'extract-froben-bellum.py')
extract=importlib.util.module_from_spec(spec);spec.loader.exec_module(extract)

def part(text,image,line):
    prefix=[0]
    for char in text:prefix.append(prefix[-1]+extract.u16(char))
    return ({'row':{'id':line,'text':text,'role':'paragraph'},'page':{'image':image,'id':f'page-{image}','display':f'Image {image}','facsimile':f'https://qa.invalid/{image}'},'prefix':prefix},0,len(text))

class FrobenBellumProjectionTests(unittest.TestCase):
    def test_explicit_page_continuation_keeps_both_original_locations(self):
        text,pieces,joins,raw=extract.project_text([part('con¬\n',1,'a'),part('tinuum\n',2,'b')])
        self.assertEqual(text,'continuum');self.assertEqual(raw,'con¬\ntinuum\n')
        self.assertEqual([p['image'] for p in pieces],[1,2])
        self.assertEqual([(p['recordStart'],p['recordEnd']) for p in pieces],[(0,3),(3,9)])
        self.assertEqual(joins,[{'marker':[1,'a',3],'following':[2,'b',0],'sourceText':'¬\n','wordContinuation':True}])

    def test_codepoint_source_and_utf16_search_coordinates_are_distinct(self):
        text,pieces,_,_=extract.project_text([part('A𐀀¬\n',1,'a'),part('B',2,'b')])
        self.assertEqual(text,'A𐀀B');self.assertEqual(len(text),3);self.assertEqual(extract.u16(text),4)
        self.assertEqual(pieces[0]['sourceEnd'],3);self.assertEqual(pieces[1]['recordStart'],3)

    def test_literal_hyphens_and_historical_spelling_survive(self):
        self.assertEqual(extract.project_text([part('  uita bon-heur ést\n',1,'a')])[0],'uita bon-heur ést')

    def test_repeated_continuation_marks_are_preserved_as_source_evidence(self):
        text,pieces,joins,raw=extract.project_text([part('Oce¬¬\n',732,'a'),part('ano',733,'b')])
        self.assertEqual(text,'Oceano');self.assertEqual(raw,'Oce¬¬\nano')
        self.assertEqual(joins[0]['sourceText'],'¬¬\n')
        self.assertEqual(joins[0]['marker'],[732,'a',3]);self.assertEqual(joins[0]['following'],[733,'b',0])
        self.assertEqual(pieces[1]['recordStart'],3)

    def test_accepted_break_before_ampersand_does_not_invent_a_word(self):
        text,_,joins,raw=extract.project_text([part('quin¬\n',773,'a'),part('& ciuitates',773,'b')])
        self.assertEqual(text,'quin& ciuitates');self.assertFalse(joins[0]['wordContinuation'])
        self.assertEqual(raw,'quin¬\n& ciuitates')

    def test_correspondence_metadata_does_not_duplicate_physical_text(self):
        data=json.loads((HERE.parents[2]/extract.SOURCE).read_bytes())
        before,_=extract.project(data,[1])
        extra=copy.deepcopy(data['frobenBooks'][1]);extra['id']='extra-context';extra['label']='Additional correspondence context'
        data['frobenBooks'].append(extra)
        after,_=extract.project(data,[1])
        self.assertEqual([(r['id'],r['text']) for r in before],[(r['id'],r['text']) for r in after])
        self.assertTrue(any(any(x['id']=='extra-context' for x in r['frobenSource']['printedBooks']) for r in after))

    def test_duplicate_source_span_cannot_pass_ownership_control(self):
        data=json.loads((HERE.parents[2]/extract.SOURCE).read_bytes())
        data['niese'][1]['spans']=copy.deepcopy(data['niese'][0]['spans'])
        with self.assertRaises(AssertionError):extract.project(data,[1])

if __name__=='__main__':unittest.main()
