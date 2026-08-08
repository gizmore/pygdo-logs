from gdo.core.GDT_Bool import GDT_Bool
from gdo.logs.UserFileMethod import UserFileMethod


class compress(UserFileMethod):

    def gdo_parameters(self) -> list:
        return super().gdo_parameters() + [GDT_Bool('remove').initial('0')]

    def gdo_has_permission(self, user) -> bool:
        return user.is_admin()

    def gdo_execute(self):
        try:
            target = self.logs().compress(
                self.get_target_user(),
                self.param_val('file'),
                self.param_value('remove'),
                self._module.cfg_max_archive_bytes(),
            )
        except (ValueError, FileNotFoundError):
            return self.error('err_log_file')
        return self.msg('msg_log_compressed', (target.name,))
