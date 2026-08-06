from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from gdo.core.GDO_User import GDO_User


@dataclass(frozen=True)
class LogFileInfo:
    name: str
    size: int
    mtime: float


class LogFiles:
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()

    @classmethod
    def from_module(cls, module) -> 'LogFiles':
        return cls(module.cfg_logs_path())

    def user_dir(self, user: GDO_User) -> Path:
        path = (self.root / user.get_server().get_name() / user.get_name()).resolve()
        self._contained(path, self.root)
        return path

    def list(self, user: GDO_User) -> list[LogFileInfo]:
        directory = self.user_dir(user)
        if not directory.is_dir():
            return []
        result = []
        for path in directory.iterdir():
            if path.is_file() and not path.is_symlink() and path.suffix == '.log':
                stat = path.stat()
                result.append(LogFileInfo(path.name, stat.st_size, stat.st_mtime))
        return sorted(result, key=lambda item: (-item.mtime, item.name))

    def resolve(self, user: GDO_User, filename: str) -> Path:
        if not filename or Path(filename).name != filename or not filename.endswith('.log'):
            raise ValueError('Invalid logfile.')
        directory = self.user_dir(user)
        path = (directory / filename).resolve()
        self._contained(path, directory)
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(filename)
        return path

    def old_files(self, days: int) -> list[Path]:
        cutoff = datetime.now().timestamp() - days * 86400
        result = []
        if not self.root.is_dir():
            return result
        for base, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d != 'archive']
            for name in files:
                if not name.endswith('.log'):
                    continue
                path = Path(base) / name
                if path.is_symlink() or path.stat().st_mtime >= cutoff:
                    continue
                resolved = path.resolve()
                self._contained(resolved, self.root)
                result.append(resolved)
        return sorted(result)

    def archive(self, files: list[Path], max_bytes: int = 0) -> Path:
        total = sum(path.stat().st_size for path in files)
        if max_bytes and total > max_bytes:
            raise ValueError(f'Log archive input exceeds limit: {total} > {max_bytes}.')
        archive_dir = self.root / 'archive'
        archive_dir.mkdir(parents=True, exist_ok=True)
        target = archive_dir / f'logs-{datetime.now():%Y%m%dT%H%M%S}.zip'
        try:
            with ZipFile(target, 'x', ZIP_DEFLATED) as archive:
                for path in files:
                    archive.write(path, path.relative_to(self.root))
            archive_size = target.stat().st_size
            if max_bytes and archive_size > max_bytes:
                target.unlink(missing_ok=True)
                raise ValueError(f'Log archive exceeds limit: {archive_size} > {max_bytes}.')
            return target
        except Exception:
            target.unlink(missing_ok=True)
            raise

    @staticmethod
    def remove(files: list[Path]):
        for path in files:
            path.unlink()

    @staticmethod
    def _contained(path: Path, root: Path):
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError('Path escapes log root.') from exc
