from src import merkle_tree, blockchain as chain
from src.blockchain import transaction

import unittest

blockchain = chain.Blockchain()

class TestBlockchain(unittest.TestCase):

    def test_sign_verification(self):
        import ecdsa
        sk = ecdsa.SigningKey.generate(ecdsa.SECP256k1)
        pk = sk.get_verifying_key()
        msg_to_sign = b'Hello'
        signature = sk.sign(msg_to_sign)

        self.assertTrue(blockchain.confirm_sign(signature, pk.to_string(), msg_to_sign))

class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.vout_data = [('ff', '13'), ('abcd', '200')]
        self.vin_data = [('123456', 0), ('cdefd', 5)]

    def test_tx_vouts(self):
        tx = transaction.Transaction(self.vout_data)
        vouts = blockchain.get_vouts(tx.tx_data)
        
        for i in range(len(vouts)):
            self.assertEqual(int(self.vout_data[i][1]), int.from_bytes(vouts[i]['value'], 'little'))
            self.assertEqual(hex(int(self.vout_data[i][0], 16)), hex(int.from_bytes(vouts[i]['script_pub_key'], 'big')))

class TestMerkleTree(unittest.TestCase):

    def test_odd_txs(self):
        tree = merkle_tree.MerkleTree([1])
        self.assertEqual(tree.root.hex(), "25e624a27f3a6fae840db755b297e67c0632f1e138346d1ed490825dd95dffdb")

    def test_even_txs(self):
        tree = merkle_tree.MerkleTree([1, 2])
        self.assertEqual(tree.root.hex(), "3582898a9e9549aeb5f67e532b38221ed5d11cb4c1e19507fd677d9b78ff7c76")
