from cProfile import label
from copy import copy
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QKeySequence, QColor, QTextCursor

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from network.client import Client
from wallet.wallet import Wallet
import os

import ecdsa
import hashlib
import threading
import argparse

from blockchain.blockchain import Blockchain
from network.client import Client

class User():
    def __init__(self):
        self.username = 'ccoin_client'
        self.network_client = Client()
        self.wallet = Wallet()
        if os.path.exists('wallet/wallet.bin'):
            with open('wallet/wallet.bin', 'rb') as f:
                key = f.read()

                self.sk = ecdsa.SigningKey.from_string(key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)

class TestWindow(QWidget):
    def __init__(self, parent=None):
        super(TestWindow, self).__init__(parent)

class OverviewWidget(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

class WalletWidget(QWidget):
    def __init__(self, user, blockchain, parent=None):
        super(QWidget, self).__init__(parent)
        self.user = user
        self.blockchain = blockchain

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.info_fields = {
            'addresses': [],
            'sums': [],
            'vouts': [],
            'txids': [],
        }

        self.vin_box = QGroupBox('VIN')
        self.vin_box_layout = QVBoxLayout()
        self.vin_box.setLayout(self.vin_box_layout)
        self.layout.addWidget(self.vin_box, 1)
        create_vin = QPushButton('Create VIN', self)
        create_vin.clicked.connect(self.addVin)
        create_vin.setStyleSheet("background-color : green")
        self.vin_box_layout.addWidget(create_vin, 1)
        self.addVin()

        self.vout_box = QGroupBox('VOUT')
        self.vout_box_layout = QVBoxLayout()
        self.vout_box.setLayout(self.vout_box_layout)
        self.layout.addWidget(self.vout_box, 1)
        create_vout = QPushButton('Create VOUT', self)
        create_vout.clicked.connect(self.addVout)
        create_vout.setStyleSheet("background-color : green")
        self.vout_box_layout.addWidget(create_vout, 1)
        self.addVout()

        send_tx = QPushButton('Create transaction', self)
        send_tx.clicked.connect(self.sendTransaction)
        send_tx.setStyleSheet("background-color : yellow")
        self.layout.addWidget(send_tx, 1)

    def sendTransaction(self):
        print([sum.text() for sum in self.info_fields['sums']])
        print([address.text() for address in self.info_fields['addresses']])
        print([txid.text() for txid in self.info_fields['txids']])
        print([int(vout.text()) for vout in self.info_fields['vouts']])

        self.blockchain.add_transaction([sum.text() for sum in self.info_fields['sums']],
        [address.text() for address in self.info_fields['addresses']],
        self.user.sk,
        [txid.text() for txid in self.info_fields['txids']],
        [vout.text() for vout in self.info_fields['vouts']])

    def addVout(self):
        # for i in range(len(self.info_fields['txids'])):
        #     print(self.info_fields['txids'][i].text())
        groupbox = QGroupBox()
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)  

        address = QLineEdit(self)
        self.info_fields['addresses'].append(address)
        address.setPlaceholderText("Enter address")
        groupbox_layout.addWidget(address, 1)
        sum = QLineEdit(self)
        self.info_fields['sums'].append(sum)
        sum.setPlaceholderText("Enter sum")
        groupbox_layout.addWidget(sum, 1)
        self.vout_box_layout.addWidget(groupbox, 1)

    def addVin(self):        
        groupbox = QGroupBox()
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)    

        txid = QLineEdit(self)
        self.info_fields['txids'].append(txid)
        txid.setPlaceholderText("Enter txid")
        groupbox_layout.addWidget(txid)
        vout = QLineEdit(self)
        self.info_fields['vouts'].append(vout)
        vout.setPlaceholderText("Enter vout")
        groupbox_layout.addWidget(vout)
        self.vin_box_layout.addWidget(groupbox, 1)

class Terminal(QTextEdit):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""QTextEdit { background-color: black; color: white }""")
        
class TerminalInput(Terminal):
    def __init__(self, terminal_output, user, prefix, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.terminal_output = terminal_output
        self.user = user
        self.prefix = prefix
        self.history = ['']
        self.history_index = 0

        self.__clear_terminal()

    def __check_keys(func):
        def wrapper(*args):
            if not os.path.exists('wallet/wallet.bin'):
                message = '[WARNING] Private key wasn\'t generated!\nGenerating key...\n'
                args[0].user.wallet.generateKeys()

                message += 'Key generated successfully'
                print(*args)
                args[0].terminal_output.addEvent(args[1], message)

            else:
                func(*args)

        return wrapper

    @__check_keys
    def __execute_command(self, command):
        command_arr = command.split()
        res = ''
        
        if command_arr[0] == 'mining':
            if command_arr[1] == '-s' or command_arr[1] == '--start':
                res = self.__start_inf_mining()
            elif command_arr[1] == '-o' or command_arr[1] == '--once':
                res = self.__mining_once()

        elif command_arr[0] == 'show':
            if command_arr[1] == 'srv-ip':
                with open('network/server.txt', 'r') as f:
                    res = f.read()

        elif command_arr[0] == 'add':
            if command_arr[1] == 'srv-ip':
                self.user.network_client.changeServerToConnectWith(command_arr[2])

        # self.__add_info_to_output(command, res)
        self.terminal_output.addEvent(command, res)

    
    def __clear_terminal(self):
        self.clear()
        self.setTextColor(QColor(17, 255, 0))
        self.insertPlainText(self.prefix)
        self.setTextColor(QColor('white'))

    def __start_inf_mining(self):

        while True:
            self.blockchain.mine_block(self.user.sk.get_verifying_key().to_string().hex())

    def __mining_once(self):
        # from blockchain.blockchain import Blockchain

        # blk_info = Blockchain.mine_block(self.user.sk.get_verifying_key().to_string().hex())      
        blk_info = self.blockchain.mine_block(self.user.wallet.sk.get_verifying_key().to_string().hex())      
        return blk_info

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
            
            self.insertPlainText(f'{self.history[self.history_index]}')
        else:
            self.insertPlainText(f'{self.history[self.history_index]}')

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Left:
            if self.textCursor().position() == len(self.prefix):
                self.textCursor().setPosition(len(self.prefix))
                return

        if event.key() == Qt.Key_Up:
            self.__previous_command()

        if event.key() == Qt.Key_Down:
            self.__next_command()

        if event.key() == Qt.Key_Backspace:
            if self.toPlainText() == self.prefix:
                self.setTextColor(QColor('white'))
                return

        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            command = self.toPlainText()[len(self.prefix):]
            
            self.history.pop()
            self.history.append(command)
            self.history.append('')
            self.history_index = len(self.history) - 1
            
            self.__execute_command(command)
            
            self.__clear_terminal()

            
            return
            
        super(Terminal, self).keyPressEvent(event)

class TerminalOutput(Terminal):
    def __init__(self, prefix):
        super().__init__()
        self.prefix = prefix
        self.setReadOnly(True)
        self.insertPlainText('***CCoin Terminal***' + '\n'*2)

    def addEvent(self, cmd, msg):
        self.setTextColor(QColor(17, 255, 0))
        self.insertPlainText(self.prefix)
        self.setTextColor(QColor('white')) 
        self.insertPlainText(str(cmd) + '\n' + str(msg) + '\n\n')
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

class TerminalWidget(QWidget):
    def __init__(self, user, blockchain, parent=None):
        super(QWidget, self).__init__(parent)
        self.prefix = f'{user.username}@ '
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.terminal_output = TerminalOutput(self.prefix)
        self.terminal_input = TerminalInput(self.terminal_output, user, self.prefix, blockchain)

        self.layout.addWidget(self.terminal_output, 20)
        self.layout.addWidget(self.terminal_input, 1)

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        
        outerLayout = QHBoxLayout()

        chain_table = QTableWidget()
        chain_h_names = ['height', 'txid', 'time',]

        chain_table.setRowCount(50)
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
        self.user = User()
        blockchain = Blockchain()

        self.setWindowTitle('CCoin Core')
        self.setWindowIcon(QtGui.QIcon('gui/logo.png'))

        self.terminal_widget = TerminalWidget(self.user, blockchain, self) 
        self.main_widget = MainWidget(self) 
        self.wallet_widget = WalletWidget(self.user, blockchain, self) 
        self.overview_widget = OverviewWidget(self) 

        self.tabWidget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabWidget)

        self.tab_v1 = QtWidgets.QWidget()
        self.tabWidget.addTab(self.overview_widget, "Overview")
        self.tabWidget.addTab(self.terminal_widget, "Terminal")
        self.tabWidget.addTab(self.main_widget, "Explore")
        self.tabWidget.addTab(self.wallet_widget, "Wallet")

        self.setFixedSize(700, 800)


        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        settingsMenu = menubar.addMenu('&Settings')
        helpMenu = menubar.addMenu('&Help')
        fileMenu.addAction(exitAction)

    def closeEvent(self, event):
        self.user.network_client.closeListening()
        
        

def fillChainTable(table):
    # from main import blockchain
    # chain = blockchain.get_chain()[::-1]
    # # chain = dict(reversed(chain))
    # for (i, block) in enumerate(chain):
    #     item = QTableWidgetItem(f"{block['index']}")
    #     f = table.setItem(i, 0, item)
    #     table.setItem(i, 1, QTableWidgetItem(f"{block['header']['timestamp']}"))
    pass
