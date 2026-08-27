from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.util.href import href
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Int import GDT_Int
from gdo.core.GDT_Path import GDT_Path
from gdo.file.GDT_FileSize import GDT_FileSize
from gdo.mail.GDT_Email import GDT_Email
from gdo.ui.GDT_Link import GDT_Link


from typing_extensions import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User


class module_logs(GDO_Module):

    def gdo_dependencies(self) -> list:
        return ['mail']

    def gdo_module_config(self) -> list:
        return [
            GDT_Path('logs_path').not_null().initial(Application.config('dir.logs')).existing_dir(),
            GDT_Int('archive_after_days').min(1).initial('7'),
            GDT_Bool('archive_mail').initial('0'),
            GDT_Email('archive_mail_address').initial(Application.config('mail.errors_to')),
            GDT_Bool('archive_keep').initial('1'),
            GDT_FileSize('max_view_bytes').min(1024).initial_value((8 * 1024 * 1024)),
            GDT_FileSize('max_archive_bytes').min(1024).initial_value((128 * 1024 * 1024)),
            GDT_FileSize('max_mail_bytes').min(1024).initial_value((20 * 1024 * 1024)),
        ]

    def cfg_logs_path(self) -> str:
        return self.get_config_val('logs_path')

    def cfg_archive_after_days(self) -> int:
        return int(self.get_config_val('archive_after_days'))

    def cfg_archive_mail(self) -> bool:
        return self.get_config_val('archive_mail') == '1'

    def cfg_archive_mail_address(self) -> str:
        return self.get_config_val('archive_mail_address') or ''

    def cfg_archive_keep(self) -> bool:
        return self.get_config_val('archive_keep') == '1'

    def cfg_max_view_bytes(self) -> int:
        return self.get_config_value('max_view_bytes')

    def cfg_max_archive_bytes(self) -> int:
        return self.get_config_value('max_archive_bytes')

    def cfg_max_mail_bytes(self) -> int:
        return self.get_config_value('max_mail_bytes')

    def gdo_subscribe_events(self):
        Application.EVENTS.subscribe('user_profile_links', self.on_user_profile_links)

    def on_user_profile_links(self, user: 'GDO_User', links):
        """Keep the private log action beside the avatar, not in profile data."""
        from gdo.core.GDO_User import GDO_User
        viewer = GDO_User.current()
        if viewer.get_id() == user.get_id() or viewer.is_admin():
            links.add_field(
                GDT_Link('view_logs').href(href('logs', 'files', f'&user={user.get_id()}')).icon('view').text('view_logs')
            )
