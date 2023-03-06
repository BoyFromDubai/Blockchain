import ecdsa
import os
import hashlib

class Wallet:
    KEYS_DIR = 'wallet'
    KEYS_PATH = 'wallet/signing_key.dat'

    def __init__(self, blockchain) -> None:
        self.blockchain = blockchain

        if os.path.exists(self.KEYS_PATH):
            with open(self.KEYS_PATH, 'rb') as f:
                self.sk = ecdsa.SigningKey.from_string(f.read(), ecdsa.SECP256k1)
        
            self.pk = self.sk.get_verifying_key()
        else:
            self.__generate_keys()

        self.utxos = []

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
        vouts_arr = []

        for i in range(len(utxo['vouts'])):
            if utxo['vouts'][i]['script_pub_key'] == self.pk.to_string().hex() and not int(utxo['vouts'][i]['spent'], 16):
                vouts_arr.append(i)
        
        return vouts_arr
                    

    def __get_utxo_from_db(self, tx_data: bytes):
        txid = hashlib.sha256(tx_data).digest()
        return (txid, self.blockchain.chainstate_db.get_utxo_formatted(txid))

    def __get_utxos(self) -> None:
        utxos = self.blockchain.chainstate_db.get_utxos()

        for utxo in utxos:
            vouts = self.__check_tx_on_vouts_posession(utxo[1])
            values = [utxo[1]['vouts'][vout]['value'] for vout in vouts]
            self.append_to_utxos(utxo[0], vouts, values)
            
    def get_utxos(self): return self.utxos

    def append_to_utxos(self, txid, vouts, values):
        for i in range(len(vouts)):
            self.utxos.append({
            'txid': txid, 
            'vout': vouts[i],
            'value': values[i]})

    def update_utxos(self, txs: bytes):
        for tx in txs:
            txid, utxo = self.__get_utxo_from_db(tx)
            vouts = self.__check_tx_on_vouts_posession(utxo)
            values = [utxo['vouts'][vout]['value'] for vout in vouts]
            self.append_to_utxos(txid.hex(), vouts, values)



     