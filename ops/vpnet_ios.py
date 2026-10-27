"""Add VPNET instructions without assuming an undocumented deep-link scheme."""
from copy import deepcopy

APP_STORE_URL = 'https://apps.apple.com/ru/app/id6756558545'


def add_vpnet(config):
    result = deepcopy(config)
    apps = result['platforms']['ios']['apps']
    if any(app['name'].casefold() == 'vpnet' for app in apps):
        raise ValueError('VPNET already exists; review instead of overwriting')
    apps.append({
        'name': 'VPNET', 'featured': False, 'svgIconKey': 'Xray',
        'blocks': [
            {
                'title': {'ru': 'Установка VPNET', 'en': 'Install VPNET'},
                'description': {'ru': 'Установите VPNET из App Store. Требуется iOS 16 или новее.', 'en': 'Install VPNET from the App Store. Requires iOS 16 or later.'},
                'svgIconKey': 'DownloadIcon', 'svgIconColor': 'cyan',
                'buttons': [{'type': 'external', 'link': APP_STORE_URL, 'text': {'ru': 'Установить VPNET', 'en': 'Install VPNET'}, 'svgIconKey': 'ExternalLink'}],
            },
            {
                'title': {'ru': 'Добавление подписки', 'en': 'Add your subscription'},
                'description': {'ru': 'Скопируйте ссылку кнопкой ниже. Откройте VPNET и добавьте подписку из буфера обмена или по ссылке. Сохраните её и обновите список серверов.', 'en': 'Copy the link below. Open VPNET and add a subscription from the clipboard or by URL. Save it and update the server list.'},
                'svgIconKey': 'CloudDownload', 'svgIconColor': 'cyan',
                'buttons': [{'type': 'copyButton', 'link': '{{SUBSCRIPTION_LINK}}', 'text': {'ru': 'Скопировать ссылку подписки', 'en': 'Copy subscription link'}, 'svgIconKey': 'Plus'}],
            },
            {
                'title': {'ru': 'Подключение', 'en': 'Connect'},
                'description': {'ru': 'Выберите сервер и включите подключение. Если iOS запросит разрешение добавить VPN-конфигурацию, разрешите его. Откройте сайт в браузере и проверьте загрузку.', 'en': 'Choose a server and connect. Allow the VPN configuration when iOS asks. Open a website in your browser to check the connection.'},
                'svgIconKey': 'Check', 'svgIconColor': 'teal', 'buttons': [],
            },
        ],
    })
    return result
