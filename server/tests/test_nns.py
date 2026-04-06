import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import util
from montytest.views import nn_delete
from pyramid import testing


class DeleteNNTest(unittest.TestCase):
    def setUp(self):
        self.rundb = util.get_rundb()
        self.config = testing.setUp()
        self.config.add_route("login", "/login")
        self.config.add_route("nns", "/nns")
        self.config.add_route("nn_delete", "/nns/delete")
        self.nn_name = "nn-0000000000a0.network"
        self.owner = "owner00"
        self.other_user = "other00"

    def tearDown(self):
        self.rundb.nndb.delete_many({})
        self.rundb.actiondb.actions.delete_many({"nn": self.nn_name})
        self.rundb.stop()
        testing.tearDown()

    def test_owner_can_delete_nn(self):
        self.rundb.upload_nn(self.owner, self.nn_name)

        with tempfile.TemporaryDirectory() as tempdir:
            Path(tempdir, self.nn_name).write_bytes(b"net")
            request = testing.DummyRequest(
                method="POST",
                POST={"nn": self.nn_name, "next": "/nns"},
                rundb=self.rundb,
                actiondb=self.rundb.actiondb,
                authenticated_userid=self.owner,
            )
            request.has_permission = lambda permission: False
            request.registry = SimpleNamespace(
                settings={"montytest.nn_storage_path": tempdir}
            )

            response = nn_delete(request)

            self.assertEqual(response.status_code, 302)
            self.assertIsNone(self.rundb.get_nn(self.nn_name))
            self.assertFalse(Path(tempdir, self.nn_name).exists())

    def test_other_user_cannot_delete_nn(self):
        self.rundb.upload_nn(self.owner, self.nn_name)

        with tempfile.TemporaryDirectory() as tempdir:
            Path(tempdir, self.nn_name).write_bytes(b"net")
            request = testing.DummyRequest(
                method="POST",
                POST={"nn": self.nn_name, "next": "/nns"},
                rundb=self.rundb,
                actiondb=self.rundb.actiondb,
                authenticated_userid=self.other_user,
            )
            request.has_permission = lambda permission: False
            request.registry = SimpleNamespace(
                settings={"montytest.nn_storage_path": tempdir}
            )

            response = nn_delete(request)

            self.assertEqual(response.status_code, 302)
            self.assertIsNotNone(self.rundb.get_nn(self.nn_name))
            self.assertTrue(Path(tempdir, self.nn_name).exists())
