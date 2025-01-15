from sandlerprops.properties import Properties as P
import unittest
import os
import shutil

class Test_db(unittest.TestCase):
   def test_read(self):
      expected_columns=['Formula', 'Name', 'Molwt', 'Tfp', 'Tb', 'Tc', 'Pc',
         'Vc', 'Zc', 'Omega', 'Dipm', 'CpA', 'CpB', 'CpC', 'CpD', 'dHf', 'dGf',
         'Eq', 'VpA', 'VpB', 'VpC', 'VpD', 'Tmin', 'Tmax', 'Lden', 'Tden']
      self.assertTrue(all([x==y for x,y in zip(P.properties,expected_columns)]))
   def test_get_compound(self):
      methane=P.get_compound('methane')
      self.assertEqual(methane.Formula,'CH4')
      no_cmp=P.get_compound('fake-compound')
      self.assertEqual(no_cmp,None)
    