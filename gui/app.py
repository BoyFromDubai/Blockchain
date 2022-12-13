from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QKeySequence, QColor, QTextCursor

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os

import ecdsa
import hashlib
import threading
import socket

from blockchain.blockchain import Blockchain
from wallet.wallet import Wallet
from network.client import Node


class User():
    def __init__(self):
        self.username = 'ccoin_client'
        self.node = Node(self.__get_local_ip(), 9999, True)
        self.node.start()
        self.wallet = Wallet()
        self.blockchain = Blockchain(self.wallet)

    def __get_local_ip(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            sock.connect(('8.8.8.8', 80))

            return sock.getsockname()[0]
        except socket.error:
            try:
                return socket.gethostbyname(socket.gethostname()) 
            except socket.gaierror:
                return '127.0.0.1'
        finally:
            sock.close()


class UTXOWindow(QWidget):
    def __init__(self, wallet, parent=None):
        super(UTXOWindow, self).__init__(parent)
        self.wallet = wallet

class OverviewWidget(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

class WalletWidget(QWidget):
    def __init__(self, user, parent=None):
        super(QWidget, self).__init__(parent)
        self.wallet = user.wallet
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.utxos_box = QGroupBox('UTXOs')
        self.utxos_box_layout = QVBoxLayout()
        self.utxos_box.setLayout(self.utxos_box_layout)
        # self.layout.addWidget(self.utxos_box, 5)
        self.__create_utxo()

        scroll = QScrollArea(self)
        self.layout.addWidget(scroll, 5)
        scroll.setWidgetResizable(True)
        scrollContent = QWidget(scroll)

        self.scrollLayout = QVBoxLayout(scrollContent)
        scrollContent.setLayout(self.scrollLayout)
        self.scrollLayout.addWidget(self.utxos_box)
        scroll.setWidget(scrollContent)

        self.wallet_box = QGroupBox('Wallet Keys')
        self.wallet_box_layout = QVBoxLayout()
        self.wallet_box.setLayout(self.wallet_box_layout)
        self.layout.addWidget(self.wallet_box, 1)
        sk_label = QLabel('Secret key: ' + str(user.wallet.sk.to_string().hex()))
        pk_label = QLabel('Public key: ' + str(user.wallet.sk.get_verifying_key().to_string().hex()))
        sk_label.setAlignment(Qt.AlignLeft)
        pk_label.setAlignment(Qt.AlignLeft)
        sk_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        pk_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.wallet_box_layout.addWidget(sk_label)
        self.wallet_box_layout.addWidget(pk_label)

    def __create_utxo(self):

        for utxo in self.wallet.utxos:
            utxo_box = QGroupBox('UTXO')
            utxo_box_layout = QVBoxLayout()
            utxo_box.setLayout(utxo_box_layout)
            txid = QLabel('txid: ' + list(utxo.keys())[0])
            n, value = utxo[list(utxo.keys())[0]]
            value = QLabel('value: ' + str(int.from_bytes(value, 'little')))
            n = QLabel('n: ' + str(int.from_bytes(n, 'little')))
            txid.setTextInteractionFlags(Qt.TextSelectableByMouse)
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            n.setTextInteractionFlags(Qt.TextSelectableByMouse)
            utxo_box_layout.addWidget(txid)
            utxo_box_layout.addWidget(value)
            utxo_box_layout.addWidget(n)

            self.utxos_box_layout.addWidget(utxo_box, 1)

    def reloadPage(self):
        for _ in range(self.utxos_box_layout.count()):
            self.utxos_box_layout.itemAt(0).widget().setParent(None)

        self.__create_utxo()

class TransactionWidget(QWidget):
    def __init__(self, user, parent=None):
        super(QWidget, self).__init__(parent)
        self.user = user

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
        try:
            for sum in self.info_fields['sums']:
                try:
                    if sum.text() == '':
                        raise Exception('Coins field must be filled!')    

                    int(sum.text())

                except ValueError as e:
                    raise ValueError('Number of coins must be int!')

                except Exception as e:
                    # print(e)
                    raise e
            
            for address in self.info_fields['addresses']:
                try:
                    if address.text() == '':
                        raise Exception('Address field must be filled!')    

                    hex(int(address.text(), 16))

                except ValueError as e:
                    raise ValueError('Adress must be a hex value!')

                except Exception as e:
                    raise e

            for txid in self.info_fields['txids']:
                try:
                    if txid.text() == '':
                        raise Exception('TXID field must be filled!')    

                    hex(int(txid.text(), 16))

                except ValueError as e:
                    raise ValueError('TXID must be a hex value!')

                except Exception as e:
                    raise e

            for vout in self.info_fields['vouts']:
                try:
                    if vout.text() == '':
                        raise Exception('Vout field must be filled!')    

                    int(vout.text())

                except ValueError as e:
                    raise ValueError('Vout number must be int!')

                except Exception as e:
                    raise e

            tx_data = self.user.blockchain.add_transaction([sum.text() for sum in self.info_fields['sums']],
                [address.text() for address in self.info_fields['addresses']],
                self.user.wallet.sk,
                [txid.text() for txid in self.info_fields['txids']],
                [vout.text() for vout in self.info_fields['vouts']])


            # Blockchain.verifyTransaction(tx_data)
            self.user.node.newTxMessage(tx_data)

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(str(e))
            msg.setWindowTitle("Error")
            msg.exec_()

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
    def __init__(self, terminal_output, user, prefix, callbackWallet):
        super().__init__()
        self.terminal_output = terminal_output
        self.user = user
        self.prefix = prefix
        self.history = self.__recover_history()
        # print(self.history)
        self.history_index = len(self.history) - 1

        self.callback_wallet = callbackWallet

        self.__clear_terminal()

    def __execute_command(self, command):
        command_arr = command.split()
        res = ''
        
        if command_arr[0] == 'mining':
            if command_arr[1] == '-s' or command_arr[1] == '--start':
                res = self.__start_inf_mining()
            elif command_arr[1] == '-o' or command_arr[1] == '--once':
                mining_thread = threading.Thread(target=self.__mining_once)
                mining_thread.start()
                mining_thread.join()
                self.callback_wallet()     

           
                # res = self.__mining_once()

        if command_arr[0] == 'abc':
            print(self.user.wallet.utxos)

        if command_arr[0] == 'network':
            if command_arr[1] == '-c' or command_arr[1] == '--connnect':
                try:
                    conn_thread = threading.Thread(target=self.user.node.connectWithNode, args=(command_arr[2], self.user.node.port))
                    conn_thread.start()
                except Exception as e:
                    print(e)
            elif command_arr[1] == '-l' or command_arr[1] == '--list':
                nodes = self.user.node.getPeers()
                res = ''
                for node in nodes: res += node
                print(res)

        if command_arr[0] == 'history':
            if command_arr[1] == '-c' or command_arr[1] == '--clear':
                open('gui/history.txt', 'w').close()
                self.history = ['']
        
        self.__print_event(command, res)

    def __recover_history(self):
        if os.path.exists('gui/history.txt'):
            with open('gui/history.txt', 'r') as f:
                return f.read().split('\n')
        else:
            return ['']

    def __print_event(self, command, res):
        self.terminal_output.addEvent(command, res)
    def __clear_terminal(self):
        self.clear()
        self.setTextColor(QColor(17, 255, 0))
        self.insertPlainText(self.prefix)
        self.setTextColor(QColor('white'))

    def __start_inf_mining(self):

        while True:
            self.user.blockchain.mine_block(self.user.wallet.sk.get_verifying_key().to_string().hex())

    def __mining_once(self):
        blk_info = self.user.blockchain.mine_block(self.user.wallet.sk.get_verifying_key().to_string().hex())  
        # mining_thread = threading.Thread(target=self.blockchain.mine_block, args=(self.user.wallet.sk.get_verifying_key().to_string().hex()))
        # mining_thread.start()

        # self.callback_wallet()     

        self.user.node.newBlockMessage(blk_info)   

        return blk_info

    def __previous_command(self):
        self.__clear_terminal()

        self.history_index -= 1

        self.insertPlainText(f'{self.history[self.history_index]}')
        
    def __next_command(self):
        self.__clear_terminal()

        self.history_index += 1 #TODO change the behavior of the first elem
        self.insertPlainText(f'{self.history[self.history_index]}')

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Left:
            if self.textCursor().position() == len(self.prefix):
                self.textCursor().setPosition(len(self.prefix))
                return

        if event.key() == Qt.Key_Up:
            if (self.history_index != 0):
                self.__previous_command()

        if event.key() == Qt.Key_Down:
            if (self.history_index != len(self.history) - 1):
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
        
            with open('gui/history.txt', 'a') as f:
                f.write(command + '\n')

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
    def __init__(self, user, callbackWallet, parent=None):
        super(QWidget, self).__init__(parent)
        self.prefix = f'{user.username}@ '
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.terminal_output = TerminalOutput(self.prefix)
        self.terminal_input = TerminalInput(self.terminal_output, user, self.prefix, callbackWallet)

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

        if not self.user.blockchain.verifyChain():
            print('Chain isn\'t valid')

        self.setWindowTitle('CCoin Core')
        self.setWindowIcon(QtGui.QIcon('gui/logo.png'))
        self.setStyleSheet("background-color: grey;")

        self.wallet_widget = WalletWidget(self.user, self) 
        self.terminal_widget = TerminalWidget(self.user, self.wallet_widget.reloadPage, self) 
        self.utxo_window = UTXOWindow(self.user.wallet, self)
        self.main_widget = MainWidget(self)
        self.transaction_widget = TransactionWidget(self.user, self) 
        self.overview_widget = OverviewWidget(self) 

        self.tabWidget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabWidget)

        self.tab_v1 = QtWidgets.QWidget()
        self.tabWidget.addTab(self.terminal_widget, "Terminal")
        self.tabWidget.addTab(self.overview_widget, "Overview")
        self.tabWidget.addTab(self.main_widget, "Explore")
        self.tabWidget.addTab(self.wallet_widget, "Wallet")
        self.tabWidget.addTab(self.transaction_widget, "Create transaction")

        self.setFixedSize(1300, 800)


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
        # self.user.network_client.closeListening()
        self.user.node.stop()
        

def fillChainTable(table):
    # from main import blockchain
    # chain = blockchain.get_chain()[::-1]
    # # chain = dict(reversed(chain))
    # for (i, block) in enumerate(chain):
    #     item = QTableWidgetItem(f"{block['index']}")
    #     f = table.setItem(i, 0, item)
    #     table.setItem(i, 1, QTableWidgetItem(f"{block['header']['timestamp']}"))
    pass
