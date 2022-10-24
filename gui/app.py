from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QKeySequence, QColor, QTextCursor

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import ecdsa
import hashlib
import threading

from blockchain.blockchain import Blockchain

class TestWindow(QWidget):
    def __init__(self, parent=None):
        super(TestWindow, self).__init__(parent)
        
        # self.grid = QGridLayout()
        # self.setLayout(self.grid)

        # self.setWindowTitle('Test')

        # btn_take_a_test = QPushButton('Take a test', self)
        # btn_take_a_test.clicked.connect(self.buttonClick)
        # btn_take_a_test.setStyleSheet("background-color : yellow")
        # self.grid.addWidget(btn_take_a_test, 1, 1)

class WalletWidget(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
    #     self.grid = QGridLayout()
    #     self.setLayout(self.grid)

    #     self.input = QLineEdit(self)
    #     self.input.setPlaceholderText("Number of tests")
    #     self.grid.addWidget(self.input, 1, 1)

    #     btn_take_a_test = QPushButton('Take a test', self)
    #     btn_take_a_test.clicked.connect(self.takeTestClick)
    #     btn_take_a_test.setStyleSheet("background-color : yellow")
    #     self.grid.addWidget(btn_take_a_test, 2, 1)

    # def takeTestClick(self):
    #     try:
    #         self.createTestWindow()
    #     except Exception as e :
    #         QMessageBox.about(self, "Error", str(e))

    # def createTestWindow(self):
    #     if not self.input.text():
    #         raise ValueError('Num of tests is not defined!')

    #     self.test_window = TestWindow()
    #     self.test_window.show()
class User():
    def __init__(self):
        self.username = 'ccoin_client'

        with open('wallet/wallet.bin', 'rb') as f:
            key = f.read()

            self.sk = ecdsa.SigningKey.from_string(key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)

class Terminal(QTextEdit):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""QTextEdit { background-color: black; color: white }""")
        

class TerminalInput(Terminal):
    def __init__(self, terminal_output):
        super().__init__()
        self.terminal_output = terminal_output
        self.user = User()
        self.prefix = f'{self.user.username}@ '
        self.history = ['']
        self.history_index = 0

        self.__clear_terminal()

    def __clear_terminal(self):
        self.clear()
        self.setTextColor(QColor(17, 255, 0))
        self.insertPlainText(self.prefix)
        self.setTextColor(QColor('white'))
    
    def __mining(self):
        sk = None

        with open('wallet/wallet.bin', 'rb') as f:
            key = f.read()

            sk = ecdsa.SigningKey.from_string(key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)

        self.thread_for_mining = threading.Thread(target=self.__start_inf_mining, args=(sk,))
        self.thread_for_mining.start()

    def __start_inf_mining(self, sk):
        from main import blockchain
        while True:
            blockchain.mine_block(sk.get_verifying_key().to_string().hex())

    def __mining_once(self):
        # from blockchain.blockchain import Blockchain
        from main import blockchain

        sk = None

        with open('wallet/wallet.bin', 'rb') as f:
            key = f.read()

            sk = ecdsa.SigningKey.from_string(key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        # Blockchain.mine_block(self.user.sk.get_verifying_key().to_string().hex())      
        blk_info = blockchain.mine_block(self.user.sk.get_verifying_key().to_string().hex())      
        print(str(blk_info))
        self.terminal_output.insertPlainText(str(blk_info))

    def __previous_command(self):
        self.__clear_terminal()

        self.history_index -= 1
        
        if self.history_index == -1:
            self.history_index += 1
        else:
            self.insertPlainText(f'{self.history[self.history_index]}')

    def __next_command(self):
        self.__clear_terminal()

        self.history_index += 1 #TODO change the behavior of the first elem

        if self.history_index == len(self.history):
            self.history_index -= 1
        else:
            self.insertPlainText(f'{self.history[self.history_index]}')

    def __add_info_to_output(self, cmd, msg):
        self.terminal_output.setTextColor(QColor(17, 255, 0))
        self.terminal_output.insertPlainText(self.prefix)
        self.terminal_output.setTextColor(QColor('white')) 
        self.terminal_output.insertPlainText(str(cmd) + '\n' * 2 + msg + '\n'*2)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Left:
            # print(self.textCursor().position())
            if self.textCursor().position() == len(self.prefix):
                self.textCursor().setPosition(len(self.prefix))
                # self.setTextColor(QColor('white'))
                return

        if event.key() == Qt.Key_Up:
            self.__previous_command()
            print(self.history_index)

        if event.key() == Qt.Key_Down:
            self.__next_command()
            print(self.history)

        if event.key() == Qt.Key_Backspace:
            if self.toPlainText() == self.prefix:
                self.setTextColor(QColor('white'))
                return

        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            # command = self.toPlainText().split()[1:]
            command = self.toPlainText()[len(self.prefix):]
            self.history.pop()
            self.history.append(command)
            self.history.append('')
            self.history_index = len(self.history) - 1
            result_of_cmd = None

            if command == 'mining' and len(command) == 1:
                self.__mining_once()
            elif command == 'exit':
                QtCore.QCoreApplication.instance().quit()
            else:
                result_of_cmd = '[ERROR]'
            
            self.__clear_terminal()
            print(self.history)

            self.__add_info_to_output(command, result_of_cmd)
            
            return
            
        super(Terminal, self).keyPressEvent(event)

class TerminalOutput(Terminal):
    def __init__(self):
        super().__init__()
        self.setEnabled(False)


class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        btn_take_a_test = QPushButton('Update dictionary', self)
        btn_take_a_test.setStyleSheet("background-color : yellow")
        self.terminal_output = TerminalOutput()
        self.terminal_input = TerminalInput(self.terminal_output)
        # self.command_line.setStyleSheet("""Terminal { background-color: black; color: white }""")
        # command_line.setStyleSheet("color : white")

        btn_take_a_test.clicked.connect(self.buttonClick)
        self.grid.addWidget(self.terminal_output, 1, 1)
        self.grid.addWidget(self.terminal_input, 2, 1)
        self.grid.addWidget(btn_take_a_test, 3, 1)

    def buttonClick(self):
        from main import blockchain
        import ecdsa
        import hashlib
        sk = None

        with open('wallet/wallet.bin', 'rb') as f:
            key = f.read()

            sk = ecdsa.SigningKey.from_string(key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)

            blockchain.mine_block(sk.get_verifying_key().to_string().hex())

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        
        outerLayout = QHBoxLayout()

        chain_table = QTableWidget()
        chain_h_names = ['height', 'txid', 'time',]

        chain_table.setRowCount(10)
        chain_table.setColumnCount(len(chain_h_names))
        chain_table.setHorizontalHeaderLabels(chain_h_names)
        chain_table.setColumnWidth(0, 50)
        chain_table.setColumnWidth(1, 70)
        chain_table.setColumnWidth(2, 200)
        chain_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        fillChainTable(chain_table)
        outerLayout.addWidget(chain_table)
        
        self.setLayout(outerLayout)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle('Dictionary')

        self.main_widget = MainWidget(self) 
        self.wallet_count = WalletWidget(self) 
        self.terminal_widget = TerminalWidget(self) 

        self.tabWidget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabWidget)

        self.tab_v1 = QtWidgets.QWidget()
        self.tabWidget.addTab(self.main_widget, "Explore")
        self.tabWidget.addTab(self.wallet_count, "Wallet")
        self.tabWidget.addTab(self.terminal_widget, "Terminal")
        print(self.tabWidget.sizeHint())
        self.setFixedSize(700, 800)
        

def fillChainTable(table):
    from main import blockchain
    chain = blockchain.get_chain()[::-1]
    # chain = dict(reversed(chain))
    for (i, block) in enumerate(chain):
        item = QTableWidgetItem(f"{block['index']}")
        f = table.setItem(i, 0, item)
        table.setItem(i, 1, QTableWidgetItem(f"{block['header']['timestamp']}"))
