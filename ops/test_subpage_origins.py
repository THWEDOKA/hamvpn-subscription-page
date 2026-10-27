import unittest
from verify_subpage_origins import script_paths, validate_ios


class OriginTests(unittest.TestCase):
    def test_reads_actual_frontend_entry_points(self):
        self.assertEqual(script_paths('<script type="module" src="/assets/index-abc.js"></script>'), ['/assets/index-abc.js'])

    def test_rejects_missing_and_duplicate_vpnet(self):
        for apps in [[], [{'name':'Happ'}], [{'name':'VPNET','blocks':[{}]}]*2]:
            with self.assertRaises(ValueError): validate_ios({'platforms':{'ios':{'apps':apps}}})

    def test_existing_clients_are_not_filtered_out(self):
        apps=[{'name':'Happ'},{'name':'VPNET','blocks':[{}]},{'name':'INCY'}]
        self.assertEqual(validate_ios({'platforms':{'ios':{'apps':apps}}}), ['Happ','VPNET','INCY'])


if __name__=='__main__': unittest.main()
