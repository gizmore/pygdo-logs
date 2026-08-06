import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from gdo.logs.LogFiles import LogFiles
from gdo.logs.method.cronjob import cronjob


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

    def test_list_accepts_dated_logger_format(self):
        dated = self.directory / '2026-08-06_message.log'
        dated.write_text('hello\n', encoding='utf-8')
        self.assertEqual(
            ['2026-08-06_message.log', '20260801_error.log'],
            [item.name for item in self.logs.list(self.user)],
        )

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

    def test_compresses_one_user_logfile_without_removing_it(self):
        target = self.logs.compress(self.user, self.file.name, remove=False, max_bytes=1024 * 1024)
        self.assertTrue(self.file.exists())
        with ZipFile(target) as archive:
            self.assertEqual(['www/gizmore/20260801_error.log'], archive.namelist())

    def test_compress_can_remove_the_source_logfile(self):
        target = self.logs.compress(self.user, self.file.name, remove=True, max_bytes=1024 * 1024)
        self.assertTrue(target.is_file())
        self.assertFalse(self.file.exists())

    def test_mails_one_user_logfile_as_attachment(self):
        class FakeMail:
            def recipient(self, email):
                self.recipient_address = email
                return self

            def subject(self, subject):
                self.mail_subject = subject
                return self

            def body(self, body):
                self.mail_body = body
                return self

            def attachment(self, path, name):
                self.attachment_path = Path(path)
                self.attachment_name = name
                return self

            def send(self):
                self.sent = True
                return True

        mail = FakeMail()
        with patch('gdo.logs.LogFiles.Mail.from_bot', return_value=mail):
            self.assertTrue(self.logs.mail(self.user, self.file.name, 'gizmore@example.test', 1024))
        self.assertEqual('gizmore@example.test', mail.recipient_address)
        self.assertEqual(self.file, mail.attachment_path)
        self.assertEqual(self.file.name, mail.attachment_name)
        self.assertTrue(mail.sent)

    def test_mail_rejects_file_larger_than_limit(self):
        with self.assertRaises(ValueError):
            self.logs.mail(self.user, self.file.name, 'gizmore@example.test', 1)

    def test_cronjob_archives_then_removes_old_files(self):
        old = Path(self.temp.name) / '2026-07-01_message.log'
        old.write_text('old log\n', encoding='utf-8')
        os.utime(old, (old.stat().st_atime, old.stat().st_mtime - 10 * 86400))

        class FakeModule:
            def cfg_logs_path(self):
                return self_root

            @staticmethod
            def cfg_archive_after_days():
                return 7

            @staticmethod
            def cfg_max_archive_bytes():
                return 1024 * 1024

            @staticmethod
            def cfg_archive_mail():
                return False

            @staticmethod
            def cfg_archive_keep():
                return True

        self_root = self.temp.name
        runner = object.__new__(cronjob)
        runner._module = FakeModule()
        runner.empty = lambda: None

        self.assertIsNone(runner.gdo_execute())
        self.assertFalse(old.exists())
        archives = list((Path(self.temp.name) / 'archive').glob('*.zip'))
        self.assertEqual(1, len(archives))


if __name__ == '__main__':
    unittest.main()
