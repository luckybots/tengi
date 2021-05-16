import hashlib
from typing import Any, Optional
import base64
import logging

from tengi.setup.config import Config

logger = logging.getLogger(__file__)


class Hasher:
    def __init__(self, config: Config):
        self.config = config

    def trimmed(self, v: Any, hash_bytes=None) -> Optional[str]:
        """
        param hash_bytes: how many bytes to hake for the trimmed hash, 10 bytes of data -> 16 symbols string
        """
        if v is None:
            return None

        s = str(v)
        salt = self.config.try_get_warny('hash_salt', operation_name='improve hashed data protection')
        if (salt is not None) and (salt != ''):
            s = s + salt

        if hash_bytes is None:
            hash_bytes = self.config.try_get_warny('hash_bytes', operation_name='reduce hashes length')

        if hash_bytes <= 0:
            logger.warning(f'Hash bytes value should be >0, but not "{hash_bytes}", ignoring it')
            hash_bytes = None

        s_bytes = s.encode('utf-8')
        hash_result = hashlib.sha1(s_bytes)
        bytes_taken = hash_result.digest() if hash_bytes is None else hash_result.digest()[-hash_bytes:]
        result = base64.b32encode(bytes_taken).decode('utf-8').rstrip('=')
        return result
