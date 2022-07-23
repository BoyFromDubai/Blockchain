import ecdsa
import hashlib
from blockchain.blockchain import Blockchain

if __name__ == '__main__':

    blockchain = Blockchain()

    sk = None

    with open('wallet/wallet.bin', 'rb') as f:
        key = f.read()

        sk = ecdsa.SigningKey.from_string(key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)

    blockchain.mine_block(sk.get_verifying_key().to_string().hex())