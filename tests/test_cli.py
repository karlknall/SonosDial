import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'installer'))
from app import parse_args
class CliTests(unittest.TestCase):
 def test_language_and_selftest_in_either_order(self):
  for argv in (['--lang','english','--self-test','result.json'],['--self-test','result.json','--lang','english']):
   with self.subTest(argv=argv):
    args=parse_args(argv);self.assertEqual(args.self_test,'result.json');self.assertEqual(args.lang,'english');self.assertIsNone(args.worker)
 def test_worker_and_normal_launch(self):
  args=parse_args(['--worker','version','unused','result.log']);self.assertEqual(args.worker,['version','unused','result.log'])
  self.assertIsNone(parse_args(['--lang','german']).self_test)
