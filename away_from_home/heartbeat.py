import copy
import datetime
import inspect
import json
import socket
import struct
import time
from collections import namedtuple
from logging import getLogger
from threading import Thread, RLock
from uuid import uuid4

_GROUP = '239.255.192.137'
_PORT = 6291
_STALE_AGE = datetime.timedelta(seconds=5)

Peer = namedtuple('Peer', ['uuid', 'priority', 'last_seen'])

socket.setdefaulttimeout(1)


class Heartbeat(object):
    def __init__(self, priority):
        self._priority = priority

        self._uuid = uuid4()
        self._peers = {}

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._lock = RLock()
        self._stopped = False
        self._recv_thread = Thread(
            target=self._recv
        )
        self._send_thread = Thread(
            target=self._send
        )

        self._logger = getLogger(self.__class__.__name__)
        self._logger.debug('{0}(); priority={1}, uuid={2}'.format(
            inspect.currentframe().f_code.co_name, self._priority, self._uuid
        ))

    @property
    def peers(self):
        with self._lock:
            return copy.deepcopy(self._peers.values())

    def _setup_recv_socket(self):
        mreq = struct.pack("4sl", socket.inet_aton(_GROUP), socket.INADDR_ANY)
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self._sock.bind((_GROUP, _PORT))

    def _recv(self):
        self._setup_recv_socket()

        while not self._stopped:
            try:
                data = self._sock.recv(1024)
            except socket.timeout:
                continue

            data_as_json = json.loads(data)

            remote_uuid = data_as_json.get('uuid')
            remote_priority = data_as_json.get('priority')

            if remote_uuid == self._uuid:
                continue

            with self._lock:
                self._peers.update({
                    remote_uuid: Peer(
                        uuid=remote_uuid,
                        priority=remote_priority,
                        last_seen=datetime.datetime.now(),
                    )
                })

                last_seen_by_uuid = {uuid: peer.last_seen for uuid, peer in self._peers}

                for uuid, last_seen in last_seen_by_uuid.iteritems():
                    if last_seen > datetime.datetime.now() - _STALE_AGE:
                        self._peers.pop(uuid)

    def _send(self):
        while not self._stopped:
            payload = {
                'uuid': self._uuid,
                'priority': self._priority,
            }

            self._sock.sendto(
                json.dumps(payload, default=lambda x: str(x)),
                (_GROUP, _PORT)
            )

            time.sleep(1)

    def start(self):
        self._recv_thread.start()
        self._send_thread.start()

    def stop(self):
        self._stopped = True

        self._recv_thread.join()
        self._send_thread.join()


if __name__ == '__main__':
    import sys

    h = Heartbeat(
        priority=sys.argv[1]
    )
    h.start()

    while 1:
        try:
            print h.peers
            print ''
            time.sleep(1)
        except KeyboardInterrupt:
            h.stop()
