from gdo.base.Application import Application
from gdo.core.GDT_String import GDT_String
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.logs.LogFiles import LogFiles
from gdo.logs.method._user import UserMethod


class view(UserMethod):
    def gdo_parameters(self) -> list:
        return super().gdo_parameters() + [GDT_String('file').not_null().maxlen(255)]

    def gdo_execute(self):
        try:
            path = LogFiles.from_module(self._module).resolve(self.get_target_user(), self.param_val('file'))
        except (ValueError, FileNotFoundError):
            return self.error('err_log_file')
        size = path.stat().st_size
        if size > self._module.cfg_max_view_bytes():
            return self.error('err_log_file_too_large', (size, self._module.cfg_max_view_bytes()))
        Application.header('Content-Type', 'text/plain; charset=utf-8')
        Application.header('Content-Length', str(size))
        return GDT_FileOut().path(str(path))
