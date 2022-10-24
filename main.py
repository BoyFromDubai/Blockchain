from website import create_app
from blockchain.blockchain import Blockchain
from wallet.wallet import Wallet
from gui.app import MainWindow, QApplication
import sys

app = create_app()
blockchain = Blockchain()
wallet = Wallet()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())