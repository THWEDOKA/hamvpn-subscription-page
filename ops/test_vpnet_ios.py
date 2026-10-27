import unittest
from copy import deepcopy
from vpnet_ios import add_vpnet, APP_STORE_URL


class VpnetTests(unittest.TestCase):
    def setUp(self):
        self.before = {'platforms': {'ios': {'apps': [{'name': 'Happ', 'featured': True}]}, 'android': {'apps': []}}, 'brandingSettings': {'name': 'HAMVPN'}}

    def test_only_app_is_added_without_mutation(self):
        original = deepcopy(self.before)
        result = add_vpnet(self.before)
        self.assertEqual(self.before, original)
        result['platforms']['ios']['apps'].pop()
        self.assertEqual(result, original)

    def test_uses_real_store_and_copy_not_invented_deep_link(self):
        app = add_vpnet(self.before)['platforms']['ios']['apps'][-1]
        self.assertFalse(app['featured'])
        self.assertEqual(app['blocks'][0]['buttons'][0]['link'], APP_STORE_URL)
        self.assertEqual(app['blocks'][1]['buttons'][0]['type'], 'copyButton')
        self.assertEqual(app['blocks'][1]['buttons'][0]['link'], '{{SUBSCRIPTION_LINK}}')
        self.assertEqual(len(app['blocks']), 3)

    def test_idempotent_reapply_refuses_duplicate(self):
        with self.assertRaises(ValueError): add_vpnet(add_vpnet(self.before))


if __name__ == '__main__': unittest.main()
