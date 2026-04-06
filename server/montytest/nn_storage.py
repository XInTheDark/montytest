import hashlib
import os
import tempfile
from pathlib import Path


DEFAULT_NN_STORAGE_PATH = "~/montytest-nns"
DEFAULT_NN_UPLOAD_LIMIT_MB = 512
UPLOAD_CHUNK_SIZE = 1024 * 1024


class NNStorageError(Exception):
    pass


class NNValidationError(NNStorageError):
    pass


class NNSizeLimitExceeded(NNStorageError):
    def __init__(self, size_limit_bytes):
        self.size_limit_bytes = size_limit_bytes
        super().__init__(f"Network exceeds upload limit of {size_limit_bytes} bytes")


def _get_setting(request, setting_name, env_name, default):
    registry = getattr(request, "registry", None)
    settings = getattr(registry, "settings", None)
    if settings and settings.get(setting_name) not in (None, ""):
        return settings[setting_name]
    value = os.getenv(env_name)
    return default if value in (None, "") else value


def get_nn_storage_path(request):
    storage_path = _get_setting(
        request,
        "montytest.nn_storage_path",
        "MONTYTEST_NN_STORAGE_PATH",
        DEFAULT_NN_STORAGE_PATH,
    )
    return Path(storage_path).expanduser()


def get_nn_upload_limit_mb(request):
    return int(
        _get_setting(
            request,
            "montytest.nn_upload_limit_mb",
            "MONTYTEST_NN_UPLOAD_LIMIT_MB",
            DEFAULT_NN_UPLOAD_LIMIT_MB,
        )
    )


def get_nn_upload_limit_bytes(request):
    return get_nn_upload_limit_mb(request) * 1024 * 1024


def get_nn_path(request, filename):
    return get_nn_storage_path(request) / filename


def ensure_nn_storage_path(request):
    storage_path = get_nn_storage_path(request)
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def store_uploaded_nn(request, filename, fileobj):
    storage_path = ensure_nn_storage_path(request)
    final_path = storage_path / filename
    if final_path.exists():
        raise FileExistsError(filename)

    size_limit = get_nn_upload_limit_bytes(request)
    digest = hashlib.sha256()
    total_size = 0
    temp_path = None

    try:
        fd, temp_name = tempfile.mkstemp(
            dir=storage_path, prefix=f".{filename}.", suffix=".upload"
        )
        temp_path = Path(temp_name)
        with os.fdopen(fd, "wb") as output:
            while True:
                chunk = fileobj.read(UPLOAD_CHUNK_SIZE)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size >= size_limit:
                    raise NNSizeLimitExceeded(size_limit)
                digest.update(chunk)
                output.write(chunk)

        expected_prefix = filename[3:15]
        actual_prefix = digest.hexdigest()[:12]
        if actual_prefix != expected_prefix:
            raise NNValidationError(
                f"Wrong SHA256 hash: {actual_prefix} Filename: {expected_prefix}"
            )

        os.replace(temp_path, final_path)
        temp_path = None
        return final_path
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
