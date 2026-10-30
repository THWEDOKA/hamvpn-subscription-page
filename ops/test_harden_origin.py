import unittest
from harden_origin import nginx_dynamic_dns,with_tls12

class HardeningTests(unittest.TestCase):
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
