import copy
import datetime
import unittest

from hamcrest import assert_that, equal_to
from mock import patch, call, MagicMock

from away_from_home.heartbeat import Heartbeat, Peer

_TEST_TIMESTAMP = datetime.datetime(year=1991, month=2, day=6)

_PEER = Peer(uuid='some_uuid', priority=1, last_seen=_TEST_TIMESTAMP)

_PEERS = {
    'some_uuid': _PEER,
    'other_uuid': Peer(
        uuid='other_uuid',
        priority=2,
        last_seen=_TEST_TIMESTAMP - datetime.timedelta(seconds=6)
    ),
}

_RECV_JSON = b"""{
    "uuid": "some_uuid",
    "priority": 1
}"""


class HeartBeatTest(unittest.TestCase):
    @patch('away_from_home.heartbeat.uuid4')
    @patch('away_from_home.heartbeat.Thread')
    def setUp(self, thread, uuid4):
        uuid4.return_value = 'own_uuid'
        self._subject = Heartbeat(priority=2)

        assert_that(
            thread.mock_calls,
            equal_to([
                call(target=self._subject._recv),
                call(target=self._subject._send),
                call(target=self._subject._expire),
            ])
        )

        self._subject._recv_sock = MagicMock()
        self._subject._send_sock = MagicMock()

    @patch('away_from_home.heartbeat.socket')
    def test_setup_socket(self, socket):
        socket.inet_aton.return_value = 'something'

        self._subject._setup_sockets()

        assert_that(
            socket.mock_calls,
            equal_to([
                call.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP),
                call.socket().setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1),
                call.inet_aton('239.137.62.91'),
                call.INADDR_ANY.__index__(),
                call.socket().setsockopt(
                    socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                    b'some\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00'
                ),
                call.socket().bind(('239.137.62.91', 6291)),
                call.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            ])
        )

    def test_handle_active_false(self):
        self._subject._peers = _PEERS

        self._subject._handle_active()

        assert_that(
            self._subject._active,
            equal_to(False)
        )

    def test_handle_active_true(self):
        self._subject._priority = 0
        self._subject._peers = _PEERS

        self._subject._handle_active()

        assert_that(
            self._subject._active,
            equal_to(True)
        )

    @patch('away_from_home.heartbeat.datetime')
    def test_recv(self, dt):
        dt.datetime.now.return_value = _TEST_TIMESTAMP
        self._subject._recv_sock.recv.return_value = _RECV_JSON
        self._subject._handle_active = MagicMock()

        self._subject._recv(test_mode=True)

        assert_that(
            self._subject._peers,
            equal_to({
                'some_uuid': _PEER
            })
        )

        assert_that(
            self._subject._handle_active.mock_calls,
            equal_to([
                call()
            ])
        )

    @patch('away_from_home.heartbeat.time')
    def test_send(self, time):
        self._subject._extra_info = {
            'some': 'thing'
        }

        self._subject._send(test_mode=True)

        assert_that(
            self._subject._send_sock.mock_calls,
            equal_to([
                call.sendto(
                    '{"uuid": "own_uuid", "priority": 2}',
                    ('239.137.62.91', 6291)
                )
            ])
        )

        assert_that(
            time.mock_calls,
            equal_to([
                call.sleep(1)
            ])
        )

    @patch('away_from_home.heartbeat.time')
    def test_expire(self, time):
        time.return_value = _TEST_TIMESTAMP - datetime.timedelta(seconds=10)
        self._subject._handle_active = MagicMock()

        self._subject._peers = copy.deepcopy(_PEERS)

        self._subject._expire(test_mode=True)

        assert_that(
            time.mock_calls,
            equal_to([
                call.sleep(1)
            ])
        )

    def test_start(self):
        self._subject._setup_sockets = MagicMock()
        self._subject._recv_thread = MagicMock()
        self._subject._send_thread = MagicMock()
        self._subject._expire_thread = MagicMock()

        self._subject.start()

        assert_that(
            self._subject._setup_sockets.mock_calls,
            equal_to([
                call()
            ])
        )

        assert_that(
            self._subject._recv_thread.mock_calls,
            equal_to([
                call.start()
            ])
        )

        assert_that(
            self._subject._send_thread.mock_calls,
            equal_to([
                call.start()
            ])
        )

        assert_that(
            self._subject._expire_thread.mock_calls,
            equal_to([
                call.start()
            ])
        )

    def test_stop(self):
        self._subject._recv_thread = MagicMock()
        self._subject._send_thread = MagicMock()
        self._subject._expire_thread = MagicMock()

        self._subject.stop()

        assert_that(
            self._subject._stopped,
            equal_to(True)
        )

        assert_that(
            self._subject._recv_thread.mock_calls,
            equal_to([
                call.join()
            ])
        )

        assert_that(
            self._subject._send_thread.mock_calls,
            equal_to([
                call.join()
            ])
        )

        assert_that(
            self._subject._expire_thread.mock_calls,
            equal_to([
                call.join()
            ])
        )
