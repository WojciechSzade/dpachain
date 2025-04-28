import unittest
from unittest.mock import Mock

from src.node.manager import NodeManager
from src.node.errors import NoPeersAvailableError

from unittest import TestCase
from unittest.mock import patch, Mock
from src.node.manager import NodeManager


class SelectBestPeerTests(TestCase):
    @patch('src.node.manager.ProtocolManager')  # <- Patchujemy zanim wejdziemy
    def setUp(self, mock_protocol_manager):
        self.manager = NodeManager(
            nickname="test_node",
            port=1234,
            private_signing_key="FAKE_KEY_FOR_TESTS"
        )
        self.manager.peer_manager = Mock()

    def create_peer(self, is_authorized):
        peer = Mock()
        peer.is_authorized = is_authorized
        return peer

    def test_sorts_by_authorized_first_then_chain_size(self):
        responses = [
            {"pipe": None, "node": self.create_peer(False), "chain_size": 50},
            {"pipe": None, "node": self.create_peer(True), "chain_size": 30},
            {"pipe": None, "node": self.create_peer(True), "chain_size": 40},
            {"pipe": None, "node": self.create_peer(False), "chain_size": 60},
        ]

        result = self.manager.select_best_peers(responses)

        self.assertTrue(result[0].is_authorized)
        self.assertTrue(result[1].is_authorized)
        self.assertFalse(result[2].is_authorized)
        self.assertFalse(result[3].is_authorized)

    def test_returns_all_peers_if_exist(self):
        responses = [
            {"pipe": None, "node": self.create_peer(True), "chain_size": 10},
            {"pipe": None, "node": self.create_peer(False), "chain_size": 5},
        ]

        result = self.manager.select_best_peers(responses)
        self.assertEqual(len(result), 2)

    def test_randomizes_on_same_chain_size_and_auth(self):
        responses = []
        for _ in range(5):
            peer = self.create_peer(True)
            responses.append({"pipe": None, "node": peer, "chain_size": 100})

        result = self.manager.select_best_peers(responses)
        self.assertEqual(len(result), 5)

    def test_raises_when_no_peers(self):
        with self.assertRaises(NoPeersAvailableError):
            self.manager.select_best_peers([])

    def test_peers_with_better_chain_and_auth_prioritized(self):
        authorized_high = self.create_peer(True)
        unauthorized_low = self.create_peer(False)

        responses = [
            {"pipe": None, "node": unauthorized_low, "chain_size": 100},
            {"pipe": None, "node": authorized_high, "chain_size": 50},
        ]

        result = self.manager.select_best_peers(responses)
        self.assertEqual(result[0], authorized_high)
