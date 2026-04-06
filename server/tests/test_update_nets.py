import unittest
from types import SimpleNamespace

import util
from montytest.views import update_nets


class UpdateNetsTest(unittest.TestCase):
    def setUp(self):
        self.rundb = util.get_rundb()
        self.net_name = "nn-0000000000a0.network"
        self.user = "user00"
        self.request = SimpleNamespace(rundb=self.rundb, host_url="https://example.com")

    def tearDown(self):
        self.rundb.nndb.delete_many({})
        self.rundb.stop()

    def test_update_nets_sets_dates_before_marking_master(self):
        self.rundb.upload_nn(self.user, self.net_name)
        run = {
            "_id": "64e74776a170cb1f26fa3930",
            "base_same_as_master": True,
            "args": {
                "base_nets": [self.net_name],
                "new_nets": [],
            },
        }

        update_nets(self.request, run)

        net = self.rundb.get_nn(self.net_name)
        self.assertTrue(net["is_master"])
        self.assertIn("first_test", net)
        self.assertIn("last_test", net)
        self.assertEqual(net["first_test"]["id"], str(run["_id"]))
        self.assertEqual(net["last_test"]["id"], str(run["_id"]))
