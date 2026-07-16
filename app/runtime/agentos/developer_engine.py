from pathlib import Path
import shutil

from app.runtime.agentos import developer_legacy


class DeveloperEngine:

    def backup(self, path: str):

        p = developer_legacy._resolve(path)

        backup = p.with_suffix(
            p.suffix + ".bak"
        )

        shutil.copy2(p, backup)

        return backup

    def restore(self, path: str, backup):

        p = developer_legacy._resolve(path)

        shutil.copy2(
            backup,
            p,
        )

    def write(self, path: str, content: str):

        p = developer_legacy._resolve(path)

        p.write_text(
            content,
            encoding="utf-8",
        )

    def compile(self):

        return developer_legacy.compile()

    def validate(self):

        return developer_legacy.validate()
