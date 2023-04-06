from src import merkle_tree, blockchain

import unittest


class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.blockchain = blockchain.Blockchain()

    def test_sign_verification(self):
        import ecdsa
        sk = ecdsa.SigningKey.generate(ecdsa.SECP256k1)
        pk = sk.get_verifying_key()
        msg_to_sign = b'Hello'
        signature = sk.sign(msg_to_sign)

        self.assertTrue(self.blockchain.confirm_sign(signature, pk.to_string(), msg_to_sign))

class TestMerkleTree(unittest.TestCase):

    def test_odd_txs(self):
        tree = merkle_tree.MerkleTree([1])
        self.assertEqual(tree.root.hex(), "25e624a27f3a6fae840db755b297e67c0632f1e138346d1ed490825dd95dffdb")

    def test_even_txs(self):
        tree = merkle_tree.MerkleTree([1, 2])
        self.assertEqual(tree.root.hex(), "3582898a9e9549aeb5f67e532b38221ed5d11cb4c1e19507fd677d9b78ff7c76")
