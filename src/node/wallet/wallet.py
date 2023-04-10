import ecdsa
import os
import hashlib

class Wallet:
    KEYS_DIR = 'wallet'
    KEYS_PATH = 'wallet/signing_key.dat'

    def __init__(self, blockchain) -> None:
        self.__blockchain = blockchain

        if os.path.exists(self.KEYS_PATH):
            with open(self.KEYS_PATH, 'rb') as f:
                self.sk = ecdsa.SigningKey.from_string(f.read(), ecdsa.SECP256k1)
        
            self.pk = self.sk.get_verifying_key()
        else:
            self.__generate_keys()

        self.__utxos = []

        self.__cur_vins = []
        self.__cur_vouts = []

        self.__get_utxos()
    
    def append_to_vins(self, vin): self.__cur_vins.append(vin)

    def append_to_vouts(self, vout): self.__cur_vouts.append(vout)

    def get_vins(self): return self.__cur_vins

    def get_vouts(self): return self.__cur_vouts

    def clear_vins(self): self.__cur_vins = []

    def clear_vouts(self): self.__cur_vouts = []

    def __generate_keys(self) -> None:
        self.sk = ecdsa.SigningKey.generate(ecdsa.SECP256k1)
        self.pk = self.sk.get_verifying_key()
        os.mkdir(self.KEYS_DIR)

        with open(self.KEYS_PATH, 'wb') as f:
            f.write(self.sk.to_string())
    
    def __check_tx_on_vouts_posession(self, utxo):
        return utxo['script_pub_key'] == self.pk.to_string().hex() and not utxo['spent']

    def __get_utxo_from_db(self, tx_data: bytes):
        txid = hashlib.sha256(tx_data).digest()

        return (txid, self.__blockchain.chainstate_db.get_utxo_formatted(txid))

    def __get_utxos(self) -> None:
        utxos = self.__blockchain.chainstate_db.get_utxos()

        for utxo in utxos:
            self.append_to_utxos(utxo[0], utxo[1]['vout'], utxo[1]['value'])
            
    def get_utxos(self): return self.__utxos

    def append_to_utxos(self, txid, vout_num, value):
        self.__utxos.append(
            {
                'txid': txid, 
                'vout': vout_num,
                'value': value,
            }
        )

    def update_utxos(self, txs: bytes):

        for tx in txs:
            txid, utxo = self.__get_utxo_from_db(tx)
            vouts = self.__check_tx_on_vouts_posession(utxo)
            values = [utxo['vouts'][vout]['value'] for vout in vouts]
            self.append_to_utxos(txid.hex(), vouts, values)



     