from constants import *


class Transaction():
    def __init__(self, vout_data, info_of_expendable_tx, vin_data = []) -> None:
        self.__vin = 0
        self.__vout = 0
        self.tx_data = self.create_tx()

    def __verify_utxo_has_enough_coins(self, info_of_expendable_tx):
        # TODO: change info_of_expendable_tx
        available_coins = sum(list(map(lambda data: int.from_bytes(self.db.getInfoOfTxid(data[0])['vouts'][data[1]]['value'], 'little'), txids_in_bytes)))

        if available_coins < coins_to_spend:
            raise ValueError('[ERROR] Not enough coins on these vins!!!')

    def create_tx(self, vout_data, info_of_expendable_tx, vin_data = []):
        version = (0).to_bytes(BLOCK_STRUCT['version'], "little")
        tx_data = version
        inputs_num = len(vin_data).to_bytes(BLOCK_STRUCT['input_count'], "little")
        tx_data += inputs_num

        if len(vin_data):
            coins_to_spend = sum(map(lambda value: int(value), [info_for_vout[1] for info_for_vout in vout_data]))
            txids_in_bytes = [(int(txid, 16).to_bytes(BLOCK_STRUCT['txid'], 'big'), int(vout)) for txid, vout in vin_data]

            self.__verify_utxo_has_enough_coins(info_of_expendable_tx)

        for i in range(len(vin_data)):
            tx_data += self.__create_vin(vin_data[i][0], int(vin_data[i][1]))

        tx_data += len(vout_data).to_bytes(1, "little") #outputs num

        for i in range(len(vout_data)):
            print(vout_data[i])
            tx_data += self.__create_vout(vout_data[i][0], int(vout_data[i][1]))
        
        # TODO move appending to the upper layer
        if len(vin_data):
            self.appendToMempool(tx_data)
                
        return tx_data