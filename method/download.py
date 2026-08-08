from gdo.base.Application import Application
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.logs.UserFileMethod import UserFileMethod


class download(UserFileMethod):

    def gdo_execute(self):
        try:
            path = self.logs().resolve(self.get_target_user(), self.param_val('file'))
        except (ValueError, FileNotFoundError):
            return self.error('err_log_file')
        Application.header('Content-Type', 'application/octet-stream')
        Application.header('Content-Length', str(path.stat().st_size))
        Application.header('Content-Disposition', f'attachment; filename="{path.name}"')
        return GDT_FileOut().path(str(path))
