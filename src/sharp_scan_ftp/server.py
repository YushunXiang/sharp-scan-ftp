from pathlib import Path

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.filesystems import AbstractedFS
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

SCAN_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".tif", ".tiff", ".png", ".txt",
                   ".xps", ".rtf", ".docx", ".xlsx", ".pptx"}


class ScanFilesystem(AbstractedFS):
    """Expose only scan files at the top level of the inbox."""

    def validpath(self, path):
        entry = Path(path)
        root = Path(self.root)
        if entry == root:
            return True
        return (entry.parent == root and not entry.name.startswith(".")
                and entry.suffix.lower() in SCAN_EXTENSIONS
                and not entry.is_symlink()
                and (not entry.exists() or entry.is_file()))

    def listdir(self, path):
        return [name for name in super().listdir(path)
                if self.validpath(Path(path) / name)]

    listdirinfo = listdir


def serve(inbox, config, password):
    authorizer = DummyAuthorizer()
    authorizer.add_user(config["username"], password, str(inbox), perm="elw")

    class ScanHandler(FTPHandler):
        abstracted_fs = ScanFilesystem

        def on_connect(self):
            local_ip = self.socket.getsockname()[0]
            if local_ip != config["mac_ip"] or self.remote_ip not in {
                config["mac_ip"], config["scanner_ip"]
            }:
                self.close()

    ScanHandler.authorizer = authorizer
    with FTPServer(("0.0.0.0", config["port"]), ScanHandler) as server:
        server.serve_forever()
