"""Preserve deployed images/env while bounding logs and following Docker DNS."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path('/opt/remnawave/subscription')
STATE=Path('/root/ham-sub-hardening-20261030')
UNIT='ham-sub-hardening-rollback'


def nginx_dynamic_dns(text):
    if 'server remnawave-subscription-page:3010 resolve;' in text: return text
    needle='upstream subscription_backend {'
    if text.count(needle)!=1 or text.count('server remnawave-subscription-page:3010;')!=1:
        raise ValueError('Unexpected upstream; manual review required')
    text=text.replace(needle,needle+'\n        zone subscription_backend 64k;\n        resolver 127.0.0.11 valid=10s ipv6=off;\n        resolver_timeout 2s;')
    return text.replace('server remnawave-subscription-page:3010;','server remnawave-subscription-page:3010 resolve;')


def with_tls12(text):
    match=re.search(r'^NODE_OPTIONS=(.*)$',text,re.M)
    value=match.group(1).strip() if match else ''
    if len(value)>1 and value[0]==value[-1] and value[0] in ['\"',"'"]:value=value[1:-1]
    if '--tls-max-v1.2' not in value:value=(value+' --tls-max-v1.2').strip()
    line='NODE_OPTIONS='+json.dumps(value)
    return text[:match.start()]+line+text[match.end():] if match else text.rstrip()+'\n'+line+'\n'


def dns_only_gos(text):
    needle='    @notCloudflare not remote_ip '
    if '@notCloudflare {\n        not host gos.hamgos.com' in text:return text
    if text.count(needle)!=1:raise ValueError('Unexpected Caddy access policy')
    lines=text.splitlines()
    index=next(i for i,line in enumerate(lines) if line.startswith(needle))
    lines[index]='    @notCloudflare {\n        not host gos.hamgos.com\n        '+lines[index].strip().removeprefix('@notCloudflare ')+'\n    }'
    return '\n'.join(lines)+'\n'


def run(*args):return subprocess.run(args,check=True,cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['apply','rollback','accept']);parser.add_argument('--tls12-api',action='store_true');args=parser.parse_args()
    os.umask(0o077)
    if args.mode=='apply':
        assert not STATE.exists(),'Existing operation must be reviewed'
        STATE.mkdir(mode=0o700)
        config=json.loads(subprocess.check_output(['docker','compose','config','--format','json'],cwd=ROOT))
        names=[n for n in config['services'] if n in ['remnawave-subscription-page','subscription-filter','caddy']]
        assert 'remnawave-subscription-page' in names
        override=ROOT/'docker-compose.override.yml';assert not override.exists(),'Preserve and review pre-existing override'
        paths=[override]
        if (ROOT/'nginx.conf').exists():paths.append(ROOT/'nginx.conf')
        if args.tls12_api:paths.append(ROOT/'.env')
        manifest={str(p):{'exists':p.exists(),'before':digest(p)} for p in paths}
        for p in paths:
            if p.exists():shutil.copy2(p,STATE/p.name)
        shutil.copy2(__file__,STATE/'rollback.py')
        (STATE/'manifest.json').write_text(json.dumps(manifest))
        subprocess.run(['systemd-run','--unit='+UNIT,'--on-active=12m','/usr/bin/python3',str(STATE/'rollback.py'),'rollback'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if (ROOT/'nginx.conf').exists():
            path=ROOT/'nginx.conf';path.write_text(nginx_dynamic_dns(path.read_text()))
            run('docker','exec','remnawave-subscription-filter','nginx','-t')
            run('docker','exec','remnawave-subscription-filter','nginx','-s','reload')
        if args.tls12_api:
            path=ROOT/'.env';path.write_text(with_tls12(path.read_text()));path.chmod(0o600)
        override.write_text(json.dumps({'services':{n:{'logging':{'driver':'json-file','options':{'max-size':'10m','max-file':'3'}}} for n in names}},indent=2))
        for p in paths:manifest[str(p)]['after']=digest(p)
        (STATE/'manifest.json').write_text(json.dumps(manifest))
        run('docker','compose','config','--quiet')
        run('docker','compose','up','-d','--no-build','--pull','never')
        print('HARDENING_APPLIED_WITH_ROLLBACK')
    elif args.mode=='rollback':
        manifest=json.loads((STATE/'manifest.json').read_text())
        for name,info in manifest.items():
            path=Path(name)
            if info.get('after') is not None and digest(path)!=info['after']:raise RuntimeError('External change; refusing overwrite')
            if info['exists']:shutil.copy2(STATE/path.name,path)
            elif path.exists():path.unlink()
        run('docker','compose','up','-d','--no-build','--pull','never')
        if (ROOT/'nginx.conf').exists():run('docker','exec','remnawave-subscription-filter','nginx','-s','reload')
        print('SCOPED_CONFIG_ROLLBACK_COMPLETE')
    else:
        manifest=json.loads((STATE/'manifest.json').read_text())
        assert all(digest(Path(name))==info['after'] for name,info in manifest.items())
        info=json.loads(subprocess.check_output(['docker','inspect','remnawave-subscription-page']))[0]
        assert info['State']['Status']=='running' and info['State'].get('Health',{}).get('Status')=='healthy'
        run('systemctl','stop',UNIT+'.timer');print('HARDENING_ACCEPTED')


if __name__=='__main__':main()
