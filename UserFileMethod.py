from gdo.core.GDT_String import GDT_String
from gdo.logs.LogFiles import LogFiles
from gdo.logs.UserMethod import UserMethod


class UserFileMethod(UserMethod):

    def gdo_parameters(self) -> list:
        return super().gdo_parameters() + [
            GDT_String('file').not_null().maxlen(255),
        ]

    def logs(self) -> LogFiles:
        return LogFiles.from_module(self.module_logs())

    def module_logs(self):
        return self._module
