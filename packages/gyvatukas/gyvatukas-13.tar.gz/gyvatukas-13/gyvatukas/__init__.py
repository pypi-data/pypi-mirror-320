"""
.. include:: ../README.md
"""
from .utils.bool import is_true, value_to_bool, is_false
from .utils.crypto import validate_password, hash_password
from .utils.dict_ import dict_remove_matching_values, dict_get_by_path
from .utils.dt import get_dt_utc_now, get_utc_today
from .utils.env import get_env
from .utils.fs import (
    get_path_without_filename,
    get_path_extension,
    get_path_filename,
    dir_exists,
    file_exists,
    write_file,
    read_file,
)
from .utils.generators import get_random_secure_string
from .utils.ip import get_my_ipv4, get_ipv4_meta, get_ip_country
from .utils.json_ import get_pretty_json, read_json, write_json
from .utils.lithuania import (
    validate_lt_id,
    validate_lt_tel_nr,
)
from .utils.validators import is_email_valid
from .utils.sql import get_inline_sql, get_conn_cur, init_db, close_connections
from .utils.decorators import timer
from .utils.db import DirDB, JsonDB

from .services.iptoolkit import IpToolKit

__all__ = [
    # bool.py
    "is_true",
    "is_false",
    "value_to_bool",
    # crypo.py
    "validate_password",
    "hash_password",
    # dict_.py
    "dict_remove_matching_values",
    "dict_get_by_path",
    # dt.py
    "get_dt_utc_now",
    "get_utc_today",
    # env.py
    "get_env",
    # fs.py
    "get_path_without_filename",
    "get_path_extension",
    "get_path_filename",
    "dir_exists",
    "file_exists",
    "write_file",
    "read_file",
    # generators.py
    "get_random_secure_string",
    # ip.py
    "get_my_ipv4",
    "get_ipv4_meta",
    "get_ip_country",
    # json_.py
    "get_pretty_json",
    "read_json",
    "write_json",
    # lithuania.py
    "validate_lt_id",
    "validate_lt_tel_nr",
    # validators.py
    "is_email_valid",
    # sql.py
    "get_inline_sql",
    "get_conn_cur",
    "init_db",
    "close_connections",
    # services.iptoolkit.py
    "IpToolKit",
    # decorators.py
    "timer",
    # db.py
    "DirDB",
    "JsonDB",
]
