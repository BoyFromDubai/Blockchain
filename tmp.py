from main import wallet
from blockchain.save_data import data
from blockchain.mrkl_tree import MerkleTree
import plyvel
import pickle
import binascii
import time
import datetime
import hashlib



file = f"baa.txt"
f = open(file, 'rb')
print(f.read().hex())
f.close()