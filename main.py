from website import create_app
from gui.app import MainWindow, QApplication
import sys

# app = create_app()
# wallet = Wallet()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())