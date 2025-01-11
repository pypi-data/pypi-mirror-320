
from sqlite_utils import hookimpl
import sqlite_vec

__version__ = "0.1.7a1"
__version_info__ = tuple(__version__.split("."))

@hookimpl
def prepare_connection(conn):
  conn.enable_load_extension(True)
  sqlite_vec.load(conn)
  conn.enable_load_extension(False)
