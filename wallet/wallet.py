import ecdsa
import hashlib
import os

class Wallet:
    def __init__(self):

        if os.path.exists('wallet/wallet.bin'):
            with open('wallet/wallet.bin', 'rb') as f:
                self.sk = ecdsa.SigningKey.from_string(f.read(), ecdsa.SECP256k1)
        
            self.pk = self.sk.get_verifying_key()
        self.utxo = []

    def add_utxo(self, transaction):
        
        tmp_arr = []
        id = hashlib.sha256(str(transaction).encode()).hexdigest()
        sum = transaction['vout'][0]['value']
        tmp_arr.append(id)
        tmp_arr.append(sum)
        self.utxo.append(tmp_arr)

    def generateKeys(self):
        
        self.sk = ecdsa.SigningKey.generate(ecdsa.SECP256k1)
        self.pk = self.sk.get_verifying_key()

        with open('wallet/wallet.bin', 'wb') as f:
            f.write(self.sk.to_string())