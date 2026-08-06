from gdo.logs.method._user_file import UserFileMethod
from gdo.mail.GDT_Email import GDT_Email


class mail(UserFileMethod):

    def gdo_parameters(self) -> list:
        return super().gdo_parameters() + [GDT_Email('email').not_null()]

    def gdo_execute(self):
        try:
            self.logs().mail(self.get_target_user(), self.param_val('file'), self.param_val('email'))
        except (ValueError, FileNotFoundError):
            return self.error('err_log_file')
        return self.msg('msg_log_mailed')
