from gdo.base.Method import Method
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_User import GDT_User


class UserMethod(Method):
    def gdo_user_type(self) -> str:
        return 'member,guest,link'

    def gdo_parameters(self) -> list:
        return [GDT_User('user').not_null().myself()]

    def get_target_user(self) -> GDO_User:
        return self.param_value('user')

    def has_permission(self, user: GDO_User, display_error: bool = True) -> bool:
        # Keep all framework checks: user type, connector, context and disabled methods.
        if not super().has_permission(user, display_error):
            return False
        target = self.get_target_user()
        allowed = bool(target) and (user.get_id() == target.get_id() or user.is_admin())
        if not allowed and display_error:
            self.err('err_permissions')
        return allowed
