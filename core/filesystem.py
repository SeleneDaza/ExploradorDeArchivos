from pathlib import Path


class FileSystem:
    def __init__(self):
        self.current_path = Path.home()

    def get_current_path(self):
        return str(self.current_path)

    def navigate_to(self, path: str):
        target = Path(path)
        if target.exists() and target.is_dir():
            self.current_path = target
            return True
        return False

    def go_up(self):
        parent = self.current_path.parent
        if parent != self.current_path:
            self.current_path = parent
            return True
        return False

    def get_home(self):
        return str(Path.home())

    def get_root(self):
        return "/"