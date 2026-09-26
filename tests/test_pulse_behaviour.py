import os, platform, shutil, socket, unittest
from unittest import mock

from pulse import providers
from pulse.app import format_bytes
from pulse.providers import ProviderError, _json_list, collect_macos, collect_processes


class ParsingTests(unittest.TestCase):
    def test_format_bytes_scales(self):
        self.assertEqual(format_bytes(512), '512 B')
        self.assertEqual(format_bytes(5 * 1024 ** 3), '5.0 GB')
        self.assertEqual(format_bytes(3 * 1024 ** 5), '3072.0 TB')

    def test_json_list_drops_non_objects(self):
        self.assertEqual(_json_list('[{"a":1}, 2, "x", {"b":2}]'), [{'a': 1}, {'b': 2}])
        self.assertEqual(_json_list('42'), [])

    def test_linux_connections_keeps_established_sockets(self):
        sample = ('tcp   LISTEN 0 128 127.0.0.1:9001 0.0.0.0:* users:(("python3",pid=100,fd=3))\n'
                  'tcp   ESTAB  0 0   127.0.0.1:51000 127.0.0.1:9001 users:(("python3",pid=200,fd=4))\n'
                  'udp   UNCONN 0 0   0.0.0.0:5353 0.0.0.0:*\n')
        with mock.patch.object(providers, '_run', return_value=sample) as run:
            conns = providers._linux_connections()
        self.assertNotIn('l', run.call_args.args[0][1].lstrip('-'), 'ss must not be limited to listening sockets')
        self.assertEqual(conns[100][0].state, 'LISTEN')
        self.assertEqual((conns[200][0].state, conns[200][0].remote), ('ESTAB', '127.0.0.1:9001'))

    def test_macos_ps_output_is_parsed(self):
        sample = '  1     0  1024  0:01.00 /sbin/launchd\n  42    1  2048  0:00.10 /Applications/My App.app/Contents/MacOS/My App\n  bad line\n'
        with mock.patch.object(providers, '_run', return_value=sample):
            procs = collect_macos()
        by_pid = {p.pid: p for p in procs}
        self.assertEqual(by_pid[42].name, 'My App'); self.assertEqual(by_pid[42].memory_bytes, 2048 * 1024)
        self.assertEqual(by_pid[42].ppid, 1)

    def test_unsupported_platform_is_reported(self):
        with mock.patch.object(platform, 'system', return_value='Plan9'):
            with self.assertRaises(ProviderError):
                collect_processes()


@unittest.skipUnless(platform.system() == 'Linux', 'reads /proc')
class LiveLinuxTests(unittest.TestCase):
    def test_current_process_is_found_with_its_parent(self):
        me = {p.pid: p for p in collect_processes()}[os.getpid()]
        self.assertEqual(me.ppid, os.getppid()); self.assertGreater(me.memory_bytes, 0)

    @unittest.skipUnless(shutil.which('ss'), 'needs ss')
    def test_established_connection_is_attributed_to_this_process(self):
        server = socket.socket(); server.bind(('127.0.0.1', 0)); server.listen()
        client = socket.create_connection(server.getsockname()); peer, _ = server.accept()
        try:
            me = {p.pid: p for p in collect_processes()}[os.getpid()]
            states = {c.state for c in me.connections}
            self.assertIn('ESTAB', states); self.assertIn('LISTEN', states)
        finally:
            for s in (peer, client, server): s.close()


if __name__ == '__main__':
    unittest.main()
