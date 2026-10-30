import unittest
from harden_origin import nginx_dynamic_dns,with_tls12,dns_only_gos

class HardeningTests(unittest.TestCase):
    def test_dns_only_exception_is_exact_and_preserves_other_hosts(self):
        before='gos.hamgos.com, sub.hamvpn.ru {\n    @notCloudflare not remote_ip 127.0.0.1 173.245.48.0/20\n    respond @notCloudflare 403\n}\n'
        after=dns_only_gos(before)
        self.assertIn('not host gos.hamgos.com',after)
        self.assertIn('not remote_ip 127.0.0.1 173.245.48.0/20',after)
        self.assertIn('respond @notCloudflare 403',after)
        self.assertEqual(after,dns_only_gos(after))
    def test_nginx_dns_only_changes_target_upstream_and_is_idempotent(self):
        text='http {\n upstream subscription_backend {\n server remnawave-subscription-page:3010;\n keepalive 32;\n }\n # user guard unchanged\n}'
        after=nginx_dynamic_dns(text)
        self.assertIn('resolver 127.0.0.11',after);self.assertIn('3010 resolve;',after)
        self.assertIn('# user guard unchanged',after);self.assertEqual(after,nginx_dynamic_dns(after))
    def test_unexpected_nginx_is_not_rewritten(self):
        with self.assertRaises(ValueError):nginx_dynamic_dns('upstream other {}')
    def test_tls_cap_preserves_heap_limit_and_other_env(self):
        before='API_SECRET=private\nNODE_OPTIONS="--max-old-space-size=512"\nOTHER=yes\n'
        after=with_tls12(before)
        self.assertIn('--max-old-space-size=512',after);self.assertIn('--tls-max-v1.2',after)
        self.assertIn('API_SECRET=private',after);self.assertIn('OTHER=yes',after)
        self.assertEqual(after,with_tls12(after))

if __name__=='__main__':unittest.main()
