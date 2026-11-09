"""Replace only the iOS VPNET card in the live HAMVPN panel config."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

APP_STORE_URL = 'https://apps.apple.com/ru/app/rabbithole-vpn-client/id6683309629'
CONFIG_ID = '00000000-0000-0000-0000-000000000000'
STATE = Path('/root/ham-subpage-rabbithole-20261109')
TIMER = 'ham-subpage-rabbithole-20261109'


def replace_vpnet(config):
    result = deepcopy(config)
    apps = result['platforms']['ios']['apps']
    matches = [i for i, app in enumerate(apps) if app['name'].casefold() == 'vpnet']
    if len(matches) != 1 or any(a['name'].casefold() == 'rabbithole' for a in apps):
        raise ValueError('Expected exactly one VPNET card and no RabbitHole card')
    slot = matches[0]
    apps[slot] = {
        'name': 'RabbitHole', 'featured': apps[slot].get('featured', False), 'svgIconKey': 'Xray',
        'blocks': [
            {
                'title': {'ru': 'Установка RabbitHole', 'en': 'Install RabbitHole'},
                'description': {'ru': 'Установите RabbitHole из App Store на iPhone или iPad.', 'en': 'Install RabbitHole from the App Store on your iPhone or iPad.'},
                'svgIconKey': 'DownloadIcon', 'svgIconColor': 'cyan',
                'buttons': [{'type': 'external', 'link': APP_STORE_URL, 'text': {'ru': 'Открыть App Store', 'en': 'Open App Store'}, 'svgIconKey': 'ExternalLink'}],
            },
            {
                'title': {'ru': 'Добавление подписки', 'en': 'Add your subscription'},
                'description': {'ru': 'Скопируйте ссылку кнопкой ниже. Откройте RabbitHole и добавьте подписку по ссылке или из буфера обмена.', 'en': 'Copy the link below. Open RabbitHole and import the subscription by URL or from the clipboard.'},
                'svgIconKey': 'CloudDownload', 'svgIconColor': 'cyan',
                'buttons': [{'type': 'copyButton', 'link': '{{SUBSCRIPTION_LINK}}', 'text': {'ru': 'Скопировать ссылку подписки', 'en': 'Copy subscription link'}, 'svgIconKey': 'Plus'}],
            },
            {
                'title': {'ru': 'Подключение', 'en': 'Connect'},
                'description': {'ru': 'Выберите сервер и включите VPN. Если iOS запросит разрешение добавить VPN-конфигурацию, нажмите «Разрешить».', 'en': 'Choose a server and turn on VPN. If iOS asks to add a VPN configuration, tap Allow.'},
                'svgIconKey': 'Check', 'svgIconColor': 'teal', 'buttons': [],
            },
        ],
    }
    return result


def main(action):
    import httpx
    sys.path.insert(0, '/opt/hamvpn2')
    os.chdir('/opt/hamvpn2')
    import config
    os.umask(0o077)
    route = 'subscription-page-configs'
    with httpx.Client(base_url=config.REMWAVE_API_URL.rstrip('/')+'/api/', headers={'Authorization': 'Bearer '+config.REMWAVE_API_KEY}, timeout=25) as client:
        def request(method, path, body=None):
            response = client.request(method, path, json=body)
            if response.status_code != 200:
                raise RuntimeError(f'Panel {method} returned HTTP {response.status_code}')
            return response.json()['response']

        def current():
            return request('GET', route+'/'+CONFIG_ID)['config']

        def update(value):
            request('PATCH', route, {'uuid': CONFIG_ID, 'config': value})
            if current() != value:
                raise RuntimeError('Panel readback does not match requested configuration')

        before_path, after_path = STATE/'before.json', STATE/'after.json'
        if action == 'prepare':
            before = current()
            after = replace_vpnet(before)
            STATE.mkdir(mode=0o700)
            before_path.write_text(json.dumps(before))
            after_path.write_text(json.dumps(after))
            shutil.copy2(__file__, STATE/'operation.py')
            print('PRIVATE_BACKUP_READY')
            return
        before, after = (json.loads(p.read_text()) for p in (before_path, after_path))
        now = current()
        if action == 'apply':
            if now != before:
                raise RuntimeError('Live configuration changed since preparation')
            subprocess.run(['systemd-run', '--unit='+TIMER, '--on-active=15m', '/opt/hamvpn2/venv/bin/python', str(STATE/'operation.py'), 'rollback'], check=True, capture_output=True)
            update(after)
            print('PANEL_PATCH_VERIFIED')
        elif action == 'rollback':
            if now == after:
                update(before)
            elif now != before:
                raise RuntimeError('Concurrent panel edit; refusing to overwrite')
            print('PANEL_ORIGINAL_VERIFIED')
        elif action == 'accept':
            if now != after:
                raise RuntimeError('Unexpected live configuration')
            subprocess.run(['systemctl', 'stop', TIMER+'.timer'], check=True, capture_output=True)
            print('PANEL_RELEASE_ACCEPTED')
        else:
            raise ValueError('Unsupported action')


if __name__ == '__main__':
    main(sys.argv[1])
