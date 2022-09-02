from flask import Blueprint, render_template, request
from blockchain.save_data import data
import hashlib
import pickle

views = Blueprint('views', __name__)

def hash_data(data):
    return hashlib.sha256(pickle.dumps(data)).hexdigest()

@views.route('/', methods=['GET'])
def main():
    chain = data.get_chain()

    return render_template("index.html", chain=chain, hash=hash_data)

@views.route('/block=<int:height>', methods=['GET'])
def block(height):
    from main import blockchain

    return render_template("block.html", block = data.get_block(height), blockchain=blockchain, hash=hash_data)
    
@views.route('/wallet', methods=['GET', 'POST'])
def wallet():
    if request.method == 'POST':
        sum = request.form.getlist('sum[]')
        txid = request.form.getlist('txid[]')
        vout = request.form.getlist('vout[]')
        address = request.form.getlist('address[]')

        from main import blockchain
        tx = blockchain.add_transaction(sum, address, txid, vout)
        data.save_to_mempool(tx)

    from main import wallet
    return render_template("wallet.html", wallet=wallet)

