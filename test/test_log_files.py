import os
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from gdo.logs.LogFiles import LogFiles


class FakeServer:
    def get_name(self):
        return 'www'


class FakeUser:
    def get_server(self):
        return FakeServer()

    def get_name(self):
        return 'gizmore'


class LogFilesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.logs = LogFiles(self.temp.name)
        self.user = FakeUser()
        self.directory = Path(self.temp.name) / 'www' / 'gizmore'
        self.directory.mkdir(parents=True)
        self.file = self.directory / '20260801_error.log'
        self.file.write_text('alpha\nbeta\n', encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def test_list_and_resolve(self):
        self.assertEqual(['20260801_error.log'], [item.name for item in self.logs.list(self.user)])
        self.assertEqual(self.file.resolve(), self.logs.resolve(self.user, self.file.name))

    def test_rejects_traversal(self):
        for filename in ('../error.log', '/etc/passwd', '..', 'a/b'):
            with self.assertRaises(ValueError):
                self.logs.resolve(self.user, filename)

    def test_old_files_uses_mtime(self):
        old = 10 * 86400
        os.utime(self.file, (self.file.stat().st_atime, self.file.stat().st_mtime - old))
        self.assertEqual([self.file.resolve()], self.logs.old_files(7))

    def test_archive_preserves_path_and_limit(self):
        target = self.logs.archive([self.file.resolve()], 1024 * 1024)
        with ZipFile(target) as archive:
            self.assertEqual(['www/gizmore/20260801_error.log'], archive.namelist())
        with self.assertRaises(ValueError):
            self.logs.archive([self.file.resolve()], 1)


if __name__ == '__main__':
    unittest.main()
