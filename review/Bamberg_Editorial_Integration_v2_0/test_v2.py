import copy,hashlib,unittest
from verify_v2 import AUTHORIZED,apply_fifteen,guardlib
def fixture(separator='',protected=False,combining=False):
 parts=['<TEI><div type="book">'];patches=[];left='alpha'+('\u0303' if combining else '')
 for cid,n in AUTHORIZED.items():
  marker=f'<cb n="case{n}"/>';label='[XVI.vi.430]' if n==430 else str(n);word='<add>'+left+'</add>' if protected else left
  parts.append(f'<p xml:id="p{n}"><num>{label}</num>{word}{separator}{marker}beta.</p>')
  patches.append({'candidate_id':cid,'book':13,'niese':n,'marker':marker,'old':'','new':' ','old_bytes_hex':'','new_bytes_hex':'20','left_word':left,'right_word':'beta.'})
 parts.append('</div></TEI>');data=''.join(parts).encode();digest=hashlib.sha256(data).hexdigest()
 for p in patches:p.update(baseline_sha256=digest,byte_start=data.index(p['marker'].encode()),byte_end=data.index(p['marker'].encode()))
 return data,patches
class FifteenScope(unittest.TestCase):
 def test_exact_fifteen_minimal_insertions_and_inverse(self):
  data,ps=fixture();after=apply_fifteen(data,ps);self.assertEqual(len(after),len(data)+15);self.assertEqual(guardlib.structure(data),guardlib.structure(after));self.assertIn(b'[XVI.vi.430]',after)
 def test_unlisted_candidate_rejected(self):
  data,ps=fixture();ps[0]['candidate_id']='UNAUTHORIZED'
  with self.assertRaises(AssertionError):apply_fifteen(data,ps)
 def test_missing_candidate_rejected(self):
  data,ps=fixture()
  with self.assertRaises(AssertionError):apply_fifteen(data,ps[:-1])
 def test_duplicate_insertion_point_rejected(self):
  data,ps=fixture();ps[-1]['byte_start']=ps[-1]['byte_end']=ps[0]['byte_start']
  with self.assertRaises(AssertionError):apply_fifteen(data,ps)
 def test_letter_or_two_spaces_rejected(self):
  for replacement in ['x','  ']:
   data,ps=fixture();ps[0]['new']=replacement;ps[0]['new_bytes_hex']=replacement.encode().hex()
   with self.assertRaises(AssertionError):apply_fifteen(data,ps)
 def test_existing_separator_not_duplicated(self):
  data,ps=fixture(separator=' ')
  with self.assertRaises(AssertionError):apply_fifteen(data,ps)
 def test_protected_complete_token_rejected(self):
  data,ps=fixture(protected=True)
  with self.assertRaises(AssertionError):apply_fifteen(data,ps)
 def test_wrong_source_hash_rejected(self):
  data,ps=fixture();ps[0]['baseline_sha256']='0'*64
  with self.assertRaises(AssertionError):apply_fifteen(data,ps)
 def test_wrong_niese_or_marker_rejected(self):
  for key,value in [('niese',999),('marker','<pb n="1r"/>')]:
   data,ps=fixture();ps[0][key]=value
   with self.assertRaises(AssertionError):apply_fifteen(data,ps)
 def test_combining_forms_not_normalized(self):
  data,ps=fixture(combining=True);after=apply_fifteen(data,ps);self.assertEqual(after.count('alpha\u0303'.encode()),15);self.assertEqual(after.count('alphã'.encode()),0)
if __name__=='__main__':unittest.main(verbosity=2)
