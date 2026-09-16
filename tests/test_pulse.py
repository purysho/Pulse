import unittest
from pulse.app import format_bytes
from pulse.models import ConnectionInfo,ProcessInfo
from pulse.providers import _json_list

class PulseTests(unittest.TestCase):
    def test_format_bytes(self):self.assertEqual(format_bytes(0),"0 B"); self.assertEqual(format_bytes(1024),"1 KB"); self.assertEqual(format_bytes(1024*1024),"1.0 MB")
    def test_models(self):
        c=ConnectionInfo(10,"127.0.0.1:80","0.0.0.0:0","Listen"); p=ProcessInfo(10,1,"demo.exe",connections=[c]); d=p.to_dict(); self.assertEqual(d["pid"],10); self.assertEqual(d["connections"][0]["state"],"Listen")
    def test_json_single_object_becomes_list(self):self.assertEqual(_json_list('{"Id":1}'),[{"Id":1}]); self.assertEqual(_json_list(""),[])
if __name__=="__main__":unittest.main()
