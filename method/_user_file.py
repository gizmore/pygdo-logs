from gdo.base.Method import Method
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_User import GDT_User
from gdo.logs.LogFiles import LogFiles


class UserFileMethod(Method):

    def gdo_user_type(self) -> str:
        return 'member,guest,link'

    def gdo_parameters(self) -> list:
        return [
            GDT_User('user').not_null().myself(),
            GDT_String('file').not_null().maxlen(255),
        ]

    def get_target_user(self) -> GDO_User:
        return self.param_value('user')

    def has_permission(self, user: GDO_User, display_error: bool = True) -> bool:
        """Parameter-sensitive check; do not use WithPermissionCheck's class/user cache."""
        target = self.get_target_user()
        allowed = bool(target) and (user.get_id() == target.get_id() or user.is_admin())
        if not allowed and display_error:
            self.err('err_permissions')
        return allowed

    def logs(self) -> LogFiles:
        return LogFiles.from_module(self.module_logs())

    def module_logs(self):
        return self._module
