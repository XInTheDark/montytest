import hashlib
import io
import tempfile
import unittest
from types import SimpleNamespace

from montytest.nn_storage import (
    NNSizeLimitExceeded,
    NNValidationError,
    store_uploaded_nn,
)


class TestNNStorage(unittest.TestCase):
    def build_request(self, tempdir, upload_limit_mb=512):
        return SimpleNamespace(
            registry=SimpleNamespace(
                settings={
                    "montytest.nn_storage_path": tempdir,
                    "montytest.nn_upload_limit_mb": str(upload_limit_mb),
                }
            )
        )

    def test_store_uploaded_nn(self):
        payload = b"hello network"
        digest = hashlib.sha256(payload).hexdigest()[:12]
        filename = f"nn-{digest}.network"

        with tempfile.TemporaryDirectory() as tempdir:
            request = self.build_request(tempdir)
            path = store_uploaded_nn(request, filename, io.BytesIO(payload))

            self.assertTrue(path.is_file())
            self.assertEqual(path.read_bytes(), payload)

    def test_store_uploaded_nn_rejects_oversized_file(self):
        payload = b"x" * (1024 * 1024)
        digest = hashlib.sha256(payload).hexdigest()[:12]
        filename = f"nn-{digest}.network"

        with tempfile.TemporaryDirectory() as tempdir:
            request = self.build_request(tempdir, upload_limit_mb=1)

            with self.assertRaises(NNSizeLimitExceeded):
                store_uploaded_nn(request, filename, io.BytesIO(payload))

    def test_store_uploaded_nn_rejects_wrong_hash(self):
        payload = b"not the hash in the filename"
        filename = "nn-000000000000.network"

        with tempfile.TemporaryDirectory() as tempdir:
            request = self.build_request(tempdir)

            with self.assertRaises(NNValidationError):
                store_uploaded_nn(request, filename, io.BytesIO(payload))
