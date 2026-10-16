"""Regression tests for source binding, layout semantics and complete-token protection."""
import unittest,hashlib
from verify_mechanical import check_edits,protected_guard,structure
def patch(data,old,new):
 a=data.index(old.encode());return {'baseline_sha256':hashlib.sha256(data).hexdigest(),'byte_start':a,'byte_end':a+len(old.encode()),'old':old,'new':new,'old_bytes_hex':old.encode().hex(),'new_bytes_hex':new.encode().hex()}
class MechanicalPreservation(unittest.TestCase):
 def source(self,text):return ('<TEI><div type="book"><p xml:id="p1"><num>1</num>'+text+'</p></div></TEI>').encode()
 def test_missing_separator_at_cb(self):
  d=self.source('haud<cb n="2/2"/>sane');p=patch(d,'<cb n="2/2"/>',' <cb n="2/2"/>');n=check_edits(d,[p]);self.assertIn(b'haud <cb n="2/2"/>sane',n);self.assertEqual(structure(d),structure(n))
 def test_continuation_across_pb_and_cb(self):
  d=self.source('pro <pb n="2r"/><cb n="1/2"/> uidentia');p=patch(d,' <pb n="2r"/><cb n="1/2"/> ','<pb n="2r"/><cb n="1/2"/>');self.assertIn(b'pro<pb',check_edits(d,[p]))
 def test_inline_niese_outside_change_preserved(self):
  d=self.source('x <milestone unit="niese" n="2"/>haud<cb n="2/2"/>sane');p=patch(d,'<cb n="2/2"/>',' <cb n="2/2"/>');self.assertEqual(structure(d),structure(check_edits(d,[p])))
 def test_niese_crossing_rejected(self):
  d=self.source('a<milestone unit="niese" n="2"/>b');p=patch(d,'<milestone unit="niese" n="2"/>',' <milestone unit="niese" n="2"/>')
  with self.assertRaises(AssertionError):check_edits(d,[p])
 def test_wrong_source_hash_rejected(self):
  d=self.source('a<cb/>b');p=patch(d,'<cb/>',' <cb/>');p['baseline_sha256']='0'*64
  with self.assertRaises(AssertionError):check_edits(d,[p])
 def test_duplicate_or_overlapping_patches_rejected(self):
  d=self.source('a<cb/>b');p=patch(d,'<cb/>',' <cb/>')
  with self.assertRaises(AssertionError):check_edits(d,[p,p])
 def test_letter_substitution_rejected(self):
  d=self.source('uere');p=patch(d,'uere','uero')
  with self.assertRaises(AssertionError):check_edits(d,[p])
 def test_whole_token_addition_guard(self):
  d=self.source('ab<add>c</add><cb/>def');a=d.index(b'<cb/>');self.assertTrue(protected_guard(d,a,a+5)['blocked'])
 def test_whole_token_deletion_guard(self):
  d=self.source('ab<del>c</del><cb/>def');a=d.index(b'<cb/>');self.assertTrue(protected_guard(d,a,a+5)['blocked'])
 def test_uncertain_or_abbreviated_token_guard(self):
  for tag in ['unclear','supplied','abbr','note']:
   d=self.source('ab<'+tag+'>c</'+tag+'><cb/>def');a=d.index(b'<cb/>');self.assertTrue(protected_guard(d,a,a+5)['blocked'])
 def test_combining_mark_unicode_preserved(self):
  d=self.source('na\u0303 <pb n="2r"/> m');p=patch(d,' <pb n="2r"/> ','<pb n="2r"/>');n=check_edits(d,[p]);self.assertIn('na\u0303<pb'.encode(),n);self.assertNotIn('nã'.encode(),n)
 def test_other_protected_word_does_not_block(self):
  d=self.source('<add>x</add> haud<cb/>sane');p=patch(d,'<cb/>',' <cb/>');check_edits(d,[p])
 def test_marker_mutation_rejected(self):
  d=self.source('a<cb n="2/2"/>b');p=patch(d,'<cb n="2/2"/>','<cb n="1/2"/>')
  with self.assertRaises(AssertionError):check_edits(d,[p])
if __name__=='__main__':unittest.main(verbosity=2)
