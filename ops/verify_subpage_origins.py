"""Verify every subscription origin with normal hostname/TLS validation.

Use only an operation-owned temporary account. Do not print or commit its URL,
cookies, HTML or session data. Production mirror caches must be checked one by
one; DNS round-robin is not a reliable release check.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
from urllib.parse import urlsplit


def script_paths(html):
    return re.findall(r'<script[^>]+src=[\"\']([^\"\']+)', html)


def validate_ios(config):
    apps = config['platforms']['ios']['apps']
    matches = [app for app in apps if app.get('name', '').casefold() == 'vpnet']
    if len(matches) != 1 or not matches[0].get('blocks'):
        raise ValueError('Expected exactly one usable VPNET card')
    return [app['name'] for app in apps]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url-file', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--origin-ip', action='append')
    args = parser.parse_args()
    os.umask(0o077)
    url = json.loads(Path(args.url_file).read_text())['url']
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname != 'gos.hamgos.com' or parsed.username:
        raise ValueError('Expected a HAMVPN HTTPS test URL')
    origins = args.origin_ip or sorted({row[4][0] for row in socket.getaddrinfo(parsed.hostname, 443)})
    output = Path(args.output_dir)
    output.mkdir(mode=0o700, parents=True, exist_ok=True)
    results = []
    for index, address in enumerate(origins):
        folder = output / str(index)
        folder.mkdir(mode=0o700, exist_ok=True)
        cookie = folder / 'cookies.txt'

        def fetch(target, name):
            target_url = urlsplit(target)
            if target_url.scheme != 'https' or target_url.hostname != parsed.hostname:
                raise ValueError('Cross-origin redirect/asset is out of scope')
            resolved = f'[{address}]' if ':' in address else address
            process = subprocess.run([
                'curl', '--silent', '--show-error', '--noproxy', '*',
                '--resolve', f'{parsed.hostname}:443:{resolved}',
                '--max-time', '30', '--user-agent', 'Mozilla/5.0 HAMVPN-Release-QA',
                '--header', 'Accept: text/html,application/json,*/*',
                '--cookie', str(cookie), '--cookie-jar', str(cookie),
                '--output', str(folder/name), '--write-out', '%{http_code}', target,
            ], capture_output=True, text=True)
            if process.returncode or process.stdout.strip() != '200':
                raise RuntimeError(f'Origin {address}: {name} failed (curl={process.returncode}, HTTP={process.stdout.strip()})')
            return (folder/name).read_bytes()

        html = fetch(url, 'page.html').decode()
        assets = script_paths(html)
        if not assets: raise ValueError(f'Origin {address}: no frontend bundle')
        for i, asset in enumerate(assets):
            if not asset.startswith('/assets/') or asset.startswith('//'):
                raise ValueError('Unexpected frontend asset path')
            fetch(f'https://{parsed.hostname}{asset}', f'asset-{i}.js')
        raw = fetch(f'https://{parsed.hostname}/assets/.app-config-v2.json?v=release-check', 'app-config.json')
        config = json.loads(raw)
        names = validate_ios(config)
        digest = hashlib.sha256(json.dumps(config, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        result = {'origin': address, 'iosApps': names, 'scripts': assets, 'configHash': digest, 'passed': True}
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    if len({row['configHash'] for row in results}) != 1:
        raise ValueError('Origins still serve different application configurations')
    (output/'results.json').write_text(json.dumps(results, ensure_ascii=False))
    print('ALL_SUBSCRIPTION_ORIGINS_VERIFIED')


if __name__ == '__main__': main()
