from ftplib import FTP
from io import BytesIO
from uuid import uuid4

def check_upload(inbox, config, password):
    target = inbox / f"ftp-test-{uuid4().hex}.txt"
    content = b"Sharp FTP upload test\n"
    with FTP() as ftp:
        ftp.connect(config["mac_ip"], config["port"], timeout=8)
        ftp.login(config["username"], password)
        ftp.storbinary(f"STOR {target.name}", BytesIO(content))
    if target.read_bytes() != content:
        raise RuntimeError(f"Upload mismatch: {target}")
    target.unlink()
    print("Upload verified.")
