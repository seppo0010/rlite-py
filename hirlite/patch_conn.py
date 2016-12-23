import hirlite
from contextlib import contextmanager

try:
    import redis
    no_redis = False
    from redis.connection import Connection
    from redis.connection import ConnectionPool
except ImportError:
    Connection = object
    ConnectionPool = object
    no_redis = True

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


# ============================================================================
orig_classes = None


# ============================================================================
class RliteConnection(Connection):
    """
    A subclass of redis-py Connection object to allow using redis-py interface
    with rlite-py

    """
    filename = ':memory:'

    @classmethod
    def set_file(cls, filename):
        cls.filename = filename

    def __init__(self, *args, **kwargs):
        super(RliteConnection, self).__init__(*args, **kwargs)
        self.rlite = hirlite.Rlite(path=self.filename)
        self.q = Queue()

        if self.db:
            self.send_command('SELECT', self.db)
            self.read_response()

    def can_read(self):
        return True

    def send_command(self, *args):
        args = [self.encode(arg) for arg in args]

        # implement SCAN via a KEYS call as rlite does not
        # currently support SCAN
        if args[0] == b'SCAN':
            args = (b'KEYS', args[3])
            result = self.rlite.command(*args)
            result = [b'0', result]
        else:
            result = self.rlite.command(*args)

        if isinstance(result, hirlite.HirliteError):
            print(result)
            raise result
        else:
            self.q.put(result)

    def pack_commands(self, *args):
        return args

    def send_packed_command(self, command):
        for cmd in command[0]:
            self.send_command(*cmd)

    def read_response(self):
        resp = self.q.get()
        if type(resp) == bool:
            return 'OK'

        if self.decode_responses and self.encoding:
            resp = self._do_decode(resp)

        return resp

    def _do_decode(self, resp):
        if isinstance(resp, list):
            return [self._do_decode(item) for item in resp]
        elif isinstance(resp, bytes):
            return resp.decode(self.encoding)
        else:
            return resp


# ============================================================================
class RliteConnectionPool(ConnectionPool):
    """
    ConnectionPool subclass that defaults to RliteConnection
    """
    def __init__(self, **kwargs):
        kwargs['connection_class'] = RliteConnection
        super(RliteConnectionPool, self).__init__(**kwargs)


# ============================================================================
def patch_connection(filename=':memory:'):
    """
    ``filename``: rlite filename to store db in, or memory
    Patch the redis-py Connection and the
    static from_url() of Redis and StrictRedis to use RliteConnection
    """

    if no_redis:
        raise Exception("redis package not found, please install redis-py via 'pip install redis'")

    RliteConnection.set_file(filename)

    global orig_classes

    # already patched
    if orig_classes:
        return

    orig_classes = (redis.connection.Connection,
                    redis.connection.ConnectionPool)

    _set_classes(RliteConnection, RliteConnectionPool)


# ============================================================================
def unpatch_connection():
    global orig_classes

    if not orig_classes:
        return

    _set_classes(*orig_classes)
    orig_classes = None


# ============================================================================
@contextmanager
def patch(filename=':memory:'):
    """
    Context manager version of patch_connection/unpatch_connection
    """
    patch_connection(filename)
    yield
    unpatch_connection()


# ============================================================================
def _set_classes(conn_class, pool_class):
    redis.connection.Connection = conn_class
    redis.Connection = conn_class

    redis.connection.ConnectionPool = pool_class
    redis.client.ConnectionPool = pool_class
    redis.ConnectionPool = pool_class
