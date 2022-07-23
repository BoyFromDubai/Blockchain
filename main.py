from website import create_app
from blockchain.blockchain import Blockchain
from wallet.wallet import Wallet

app = create_app()
blockchain = Blockchain()
wallet = Wallet()

if __name__ == '__main__':
    app.run(debug=True)

    # import os
    # files_arr = os.listdir('blockchain/blocks')
    # for file in files_arr:
    #     os.remove('blockchain/blocks/' + file)