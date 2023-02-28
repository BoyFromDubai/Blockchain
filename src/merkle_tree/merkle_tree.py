import hashlib
import pickle

class MerkleTree:
    def __init__(self, txs):
        self.leafs = self.__create_leafs(txs)
        self.root = self.__create_mrkl_root(self.leafs)

    def __create_leafs(self, txs):
        tmp_leafs = []
        
        for tx in txs:
            tmp_leafs.append(hashlib.sha256(pickle.dumps(tx)).hexdigest())
        
        return tmp_leafs

    def __create_mrkl_root(self, leafs):
        tmp_arr = []

        if not len(leafs):
            return None

        if len(leafs) % 2:
            leafs.append(leafs[-1])

        for i in range(0, len(leafs), 2):
            tmp_leafs = [leafs[i]]
            i += 1
            tmp_leafs.append(leafs[i])
            
            str_tmp_leaf = ''

            for leaf in tmp_leafs:
                str_tmp_leaf += str(leaf)

            tmp_arr.append(hashlib.sha256(pickle.dumps(str_tmp_leaf)).digest())

        if len(tmp_arr) != 1:
            return self.__create_mrkl_root(tmp_arr)
        else:
            return tmp_arr[0]
