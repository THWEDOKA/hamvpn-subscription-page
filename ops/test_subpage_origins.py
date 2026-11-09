import unittest
from verify_subpage_origins import script_paths, validate_ios
from rabbithole_ios import replace_vpnet


class OriginTests(unittest.TestCase):
    def test_reads_actual_frontend_entry_points(self):
        self.assertEqual(script_paths('<script type="module" src="/assets/index-abc.js"></script>'), ['/assets/index-abc.js'])

    def test_rejects_missing_unusable_or_duplicate_rabbithole(self):
        for apps in [[], [{'name':'VPNET'}], [{'name':'RabbitHole','blocks':[{}]}], [{'name':'RabbitHole'}]*2]:
            with self.assertRaises(ValueError): validate_ios({'platforms':{'ios':{'apps':apps}}})

    def test_existing_clients_are_not_filtered_out(self):
        apps=[{'name':'Happ'},{'name':'VPNET','blocks':[{}]},{'name':'INCY'}]
        config = {'platforms':{'ios':{'apps':apps}, 'android':{'apps':[{'name':'Happ'}]}}, 'baseSettings':{'metaTitle':'HAMVPN'}}
        result = replace_vpnet(config)
        self.assertEqual(validate_ios(result), ['Happ','RabbitHole','INCY'])
        self.assertEqual(result['platforms']['android'], config['platforms']['android'])
        self.assertEqual(result['baseSettings'], config['baseSettings'])
        self.assertEqual(apps[1]['name'], 'VPNET')

    def test_rejects_reapplying_migration(self):
        config = {'platforms':{'ios':{'apps':[{'name':'VPNET'}]}}}
        with self.assertRaises(ValueError): replace_vpnet(replace_vpnet(config))


if __name__=='__main__': unittest.main()
