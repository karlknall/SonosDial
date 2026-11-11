import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'installer'))
from app import check_device,VERSION
class MiniTests(unittest.TestCase):
 def test_only_s3_8mb(self):
  check_device('Chip is ESP32-S3\nDetected flash size: 8MB')
  for chip,size in [('ESP32-S3','16MB'),('ESP32-S3','4MB'),('ESP32-C3','8MB'),('ESP32-C6','8MB'),('ESP32','8MB')]:
   with self.subTest(chip=chip,size=size),self.assertRaises(RuntimeError):check_device(f'Chip is {chip}\nDetected flash size: {size}')
 def test_version_separates_old_firmware(self):
  self.assertEqual(VERSION,'1.2.0')
 def test_partition_layout(self):
  root=pathlib.Path(__file__).resolve().parents[1]
  previous_end=0x9000
  for line in (root/'partitions.csv').read_text().splitlines():
   if not line.strip() or line.startswith('#'):continue
   fields=[x.strip() for x in line.split(',')];start=int(fields[3],0);size=int(fields[4],0)
   self.assertGreaterEqual(start,previous_end);self.assertLessEqual(start+size,8*1024*1024);previous_end=start+size
