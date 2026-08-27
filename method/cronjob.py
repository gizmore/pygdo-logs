from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Trans import t
from gdo.core.MethodCronjob import MethodCronjob
from gdo.logs.LogFiles import LogFiles
from gdo.mail.Mail import Mail


class cronjob(MethodCronjob):
    def gdo_connectors(self) -> str:
        return 'web'

    def gdo_run_at(self) -> str:
        return self.run_daily_at(0, 17)

    def gdo_execute(self) -> GDT:
        mod = self._module
        service = LogFiles.from_module(mod)
        files = service.old_files(mod.cfg_archive_after_days())
        if not files:
            return self.empty()

        try:
            archive = service.archive(files, mod.cfg_max_archive_bytes())
        except (OSError, ValueError) as ex:
            Logger.exception(ex, 'Cannot archive old logfiles.')
            return self.empty()

        success = True
        if mod.cfg_archive_mail():
            recipient = mod.cfg_archive_mail_address()
            if archive.stat().st_size > mod.cfg_max_mail_bytes():
                Logger.error('Log archive is too large for mail delivery.')
                success = False
            else:
                success = bool(recipient) and self.mail_archive(archive, recipient)

        if success:
            service.remove(files)
            if not mod.cfg_archive_keep():
                archive.unlink()
        return self.empty()

    def mail_archive(self, archive, recipient: str) -> bool:
        return (Mail.from_bot()
                .recipient(recipient)
                .subject(t('mail_logs_archive_subject'))
                .body(t('mail_logs_archive_body'))
                .attachment(str(archive), archive.name)
                .send())
