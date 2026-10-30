"""Restore only empty public PEM components matching the installed fullchain."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    os.umask(0o077)
    parts=json.load(sys.stdin)
    assert set(parts)=={'cert.pem','chain.pem'}
    root=Path('/etc/letsencrypt/live/gos.hamgos.com')
    normalize=lambda text:''.join(text.split())
    assert normalize(parts['cert.pem']+parts['chain.pem'])==normalize((root/'fullchain.pem').read_text())
    backup=Path('/root/ham-sub-empty-chain-before-20261030')
    backup.mkdir(mode=0o700,exist_ok=False)
    for name,content in parts.items():
        path=root/name;resolved=path.resolve()
        assert resolved.parent==Path('/etc/letsencrypt/archive/gos.hamgos.com')
        assert path.stat().st_size==0,'Do not overwrite nonempty PEM components'
        shutil.copy2(path,backup/name)
        path.write_text(content)
        subprocess.run(['openssl','x509','-in',str(path),'-noout'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    print('EMPTY_PUBLIC_CHAIN_COMPONENTS_RESTORED_PRIVATE_KEY_UNCHANGED')


if __name__=='__main__':main()
