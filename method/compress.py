from gdo.core.GDT_Bool import GDT_Bool
from gdo.logs.method._user_file import UserFileMethod


class compress(UserFileMethod):

    def gdo_parameters(self) -> list:
        return super().gdo_parameters() + [GDT_Bool('remove').initial('0')]

    def gdo_has_permission(self, user) -> bool:
        return user.is_admin()

    def has_permission(self, user, display_error: bool = True) -> bool:
        allowed = user.is_admin()
        if not allowed and display_error:
            self.err('err_permissions')
        return allowed

    def gdo_execute(self):
        try:
            target = self.logs().compress(
                self.get_target_user(), self.param_val('file'), self.param_value('remove'))
        except (ValueError, FileNotFoundError):
            return self.error('err_log_file')
        return self.msg('msg_log_compressed', (target.name,))
