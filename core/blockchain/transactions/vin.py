from core.blockchain.constants import *

class Vin():
    def __init__(self, txid, vout_num) -> None:
        self.vin_data = self.__create_vin(txid, vout_num)

    def __create_vin(self, txid, vout_num):
        txid = int(txid, 16).to_bytes(BLOCK_STRUCT['txid'], 'big')

        tx_vouts = self.db.getInfoOfTxid(txid)['vouts']

        if vout_num > len(tx_vouts) - 1:
            raise ValueError('[ERROR] Not enough vouts in tx!!!')

        else:
            vout = tx_vouts[vout_num]

            if int.from_bytes(vout['spent'], 'little'):
                raise ValueError('[ERROR] Vout is already spent!!!')
            else:

                script_pub_key = vout['script_pub_key'] 
                
                vin_data = txid 
                vin_data += vout_num.to_bytes(BLOCK_STRUCT['vout'], "little")

                message_to_sign = txid
                scriptSig = self.wallet.sk.sign(message_to_sign)
                print('message_to_sign')
                print(message_to_sign)
                print('scriptSig')
                print(scriptSig)
                
                if not self.confirmSign(scriptSig, script_pub_key, message_to_sign):
                    raise ValueError('[ERROR] Signature failed!')

                vin_data += len(scriptSig).to_bytes(BLOCK_STRUCT['script_sig_size'], "little") #ScriptSig size
                vin_data += scriptSig #ScriptSig

                return vin_data