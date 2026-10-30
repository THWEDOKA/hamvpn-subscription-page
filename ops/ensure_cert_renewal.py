"""Restore scheduled renewal of the existing subscription certificate only."""
import os
from pathlib import Path
import shutil
import subprocess


def main():
    os.umask(0o077)
    assert Path('/etc/letsencrypt/renewal/gos.hamgos.com.conf').is_file()
    credentials=Path('/root/.secrets/cloudflare.ini')
    assert credentials.is_file() and credentials.stat().st_size>0
    credentials.chmod(0o600)
    log=Path('/root/ham-sub-cert-maintenance.log')
    with log.open('ab') as output:
        if not shutil.which('certbot'):
            env=os.environ|{'DEBIAN_FRONTEND':'noninteractive'}
            subprocess.run(['apt-get','update','-qq'],check=True,env=env,stdout=output,stderr=output)
            subprocess.run(['apt-get','install','-y','certbot','python3-certbot-dns-cloudflare'],check=True,env=env,stdout=output,stderr=output)
        subprocess.run(['certbot','renew','--cert-name','gos.hamgos.com','--no-random-sleep-on-renew','--quiet'],check=True,stdout=output,stderr=output)
    units=subprocess.check_output(['systemctl','list-unit-files','certbot.timer','--no-legend']).decode()
    if 'certbot.timer' in units:
        subprocess.run(['systemctl','enable','--now','certbot.timer'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        timer='certbot.timer'
    else:
        executable=shutil.which('certbot')
        service=Path('/etc/systemd/system/ham-sub-cert-renew.service')
        timer_path=service.with_suffix('.timer')
        expected={service:'[Unit]\nDescription=Renew existing HAMVPN subscription certificate\n[Service]\nType=oneshot\nExecStart='+executable+' renew --cert-name gos.hamgos.com --quiet\n',timer_path:'[Unit]\nDescription=Schedule HAMVPN subscription certificate renewal\n[Timer]\nOnCalendar=*-*-* 03,15:00:00\nRandomizedDelaySec=1800\nPersistent=true\n[Install]\nWantedBy=timers.target\n'}
        for path,text in expected.items():
            if path.exists() and path.read_text()!=text:raise RuntimeError('Preserve existing custom renewal unit')
            path.write_text(text)
        subprocess.run(['systemctl','daemon-reload'],check=True)
        timer='ham-sub-cert-renew.timer'
        subprocess.run(['systemctl','enable','--now',timer],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    subprocess.run(['systemctl','is-active','--quiet',timer],check=True)
    print('EXISTING_CERTIFICATE_RENEWAL_SCHEDULE_ACTIVE',timer)


if __name__=='__main__':main()
