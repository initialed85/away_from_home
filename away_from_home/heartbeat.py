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

_GROUP = '239.137.62.91'
_PORT = 6291
_STALE_AGE = datetime.timedelta(seconds=5)

Peer = namedtuple('Peer', ['uuid', 'priority', 'last_seen'])

socket.setdefaulttimeout(1)


class Heartbeat(object):
    def __init__(self, priority):
        self._priority = priority

        self._uuid = str(uuid4())
        self._peers = {}

        self._recv_thread = Thread(
            target=self._recv
        )
        self._send_thread = Thread(
            target=self._send
        )
        self._expire_thread = Thread(
            target=self._expire
        )
        self._stopped = False
        self._lock = RLock()
        self._recv_sock = None
        self._send_sock = None
        self._active = True

        self._logger = getLogger(self.__class__.__name__)
        self._logger.debug('{0}(); priority={1}, uuid={2}, active={3}'.format(
            inspect.currentframe().f_code.co_name, self._priority, repr(self._uuid), self._active
        ))

    @property
    def peers(self):
        with self._lock:
            return copy.deepcopy(self._peers.values())

    @property
    def active(self):
        return self._active

    def _setup_sockets(self):
        self._recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mreq = struct.pack("4sl", socket.inet_aton(_GROUP), socket.INADDR_ANY)
        self._recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self._recv_sock.bind((_GROUP, _PORT))
        self._send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def _handle_active(self):
        if len(self.peers) == 0 or self._priority < max([x.priority for x in self.peers]):
            if not self._active:
                self._active = True

                self._logger.info('{0}(); active={1}'.format(
                    inspect.currentframe().f_code.co_name, self._active
                ))
        else:
            if self._active:
                self._active = False

                self._logger.info('{0}(); active={1}'.format(
                    inspect.currentframe().f_code.co_name, self._active
                ))

    def _recv(self):
        while not self._stopped:
            try:
                data_as_json = self._recv_sock.recv(1024)
            except socket.timeout:
                continue

            data_as_dict = json.loads(data_as_json)
            remote_uuid = data_as_dict.get('uuid')
            remote_priority = data_as_dict.get('priority')

            if remote_uuid == self._uuid:
                continue

            with self._lock:
                peer = Peer(
                    uuid=remote_uuid,
                    priority=remote_priority,
                    last_seen=datetime.datetime.now(),
                )

                if remote_uuid not in self._peers:
                    self._logger.info('{0}(); added peer={1}'.format(
                        inspect.currentframe().f_code.co_name, peer
                    ))

                self._peers.update({
                    remote_uuid: peer
                })

            self._handle_active()

    def _send(self):
        while not self._stopped:
            data_as_dict = {
                'uuid': self._uuid,
                'priority': self._priority,
            }

            self._send_sock.sendto(
                json.dumps(data_as_dict),
                (_GROUP, _PORT)
            )

            time.sleep(1)

    def _expire(self):
        while not self._stopped:
            with self._lock:
                last_seen_by_uuid = {uuid: peer.last_seen for uuid, peer in self._peers.iteritems()}

                for uuid, last_seen in last_seen_by_uuid.iteritems():
                    peer = self._peers.get(uuid)
                    if last_seen < datetime.datetime.now() - _STALE_AGE:
                        self._peers.pop(uuid)
                        self._logger.info('{0}(); removed peer={1}'.format(
                            inspect.currentframe().f_code.co_name, peer
                        ))

            self._handle_active()

            time.sleep(1)

    def start(self):
        self._setup_sockets()

        self._recv_thread.start()
        self._send_thread.start()
        self._expire_thread.start()

    def stop(self):
        self._stopped = True

        self._recv_thread.join()
        self._send_thread.join()
        self._expire_thread.join()
