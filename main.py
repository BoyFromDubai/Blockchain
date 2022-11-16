from website import create_app
from gui.app import MainWindow, QApplication
import sys
from network.client import Client

app = create_app()
# wallet = Wallet()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()

    sys.exit(app.exec_())