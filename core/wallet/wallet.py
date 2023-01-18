import ecdsa
import hashlib
import os

UTXOS_STRUCT = {
    'txid': 32,
    'n': 1,
    'value': 8,
}

class Wallet:
    def __init__(self):

        if os.path.exists('wallet/wallet.dat'):
            with open('wallet/wallet.dat', 'rb') as f:
                self.sk = ecdsa.SigningKey.from_string(f.read(), ecdsa.SECP256k1)
        
            self.pk = self.sk.get_verifying_key()
        else:
            self.generateKeys()

        self.utxos = []

    def appendUTXO(self, txid, n, value):
        
        n = n.to_bytes(UTXOS_STRUCT['n'], 'little')
        
        self.utxos.append({txid.hex(): (n, value)})
        print(txid)

        # with open('wallet/utxos.dat', 'ab') as f:
        #     f.write(txid)
        #     f.write(n)
        #     f.write(value)

        print(self.utxos)
    
    def generateKeys(self):
        
        self.sk = ecdsa.SigningKey.generate(ecdsa.SECP256k1)
        self.pk = self.sk.get_verifying_key()

        with open('wallet/wallet.dat', 'wb') as f:
            f.write(self.sk.to_string())