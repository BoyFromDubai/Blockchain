import hashlib
from typing import List

class MerkleTree:
    def __init__(self, leafs: List):
        self.leafs = self.__create_leafs(leafs)
        self.root = self.__create_mrkl_root(self.leafs)

    def convert_arr_to_bytes(self, arr: List):
        bytes_arr = []

        for item in arr:
            if type(item) is bytes:
                bytes_arr.append(item)
            elif type(item) is int:
                bytes_arr.append(item.to_bytes((item.bit_length() + 7) // 8, 'big'))
            elif type(item) is str:
                bytes_arr.append(item.encode())
            else:
                raise ValueError('[ERROR] Unsopperted type for merkle tree')

        return bytes_arr

    def __create_leafs(self, arr: List):
        tmp_leafs = []
        bytes_arr = self.convert_arr_to_bytes(arr)
        
        for item in bytes_arr:
            tmp_leafs.append(hashlib.sha256(item).hexdigest())

        return tmp_leafs

    def __create_mrkl_root(self, leafs: List):
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

            tmp_arr.append(hashlib.sha256(str_tmp_leaf.encode()).digest())

        if len(tmp_arr) != 1:
            return self.__create_mrkl_root(tmp_arr)
        
        return tmp_arr[0]
