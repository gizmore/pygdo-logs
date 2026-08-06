import html
from datetime import datetime

from gdo.base.util.href import href
from gdo.logs.LogFiles import LogFiles
from gdo.logs.method._user import UserMethod
from gdo.message.GDT_HTML import GDT_HTML


class list(UserMethod):
    def gdo_execute(self):
        target = self.get_target_user()
        rows = []
        for item in LogFiles.from_module(self._module).list(target):
            url = href('logs', 'view', f'&user={target.get_id()}&file={item.name}')
            rows.append(f'<tr><td><a href="{url}">{html.escape(item.name)}</a></td><td>{item.size}</td><td>{datetime.fromtimestamp(item.mtime):%Y-%m-%d %H:%M}</td></tr>')
        body = ''.join(rows) or '<tr><td colspan="3">No logfiles.</td></tr>'
        return GDT_HTML().html(f'<table><thead><tr><th>File</th><th>Bytes</th><th>Modified</th></tr></thead><tbody>{body}</tbody></table>')
