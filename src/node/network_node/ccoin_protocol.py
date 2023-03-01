from .constants import *
from hashlib import sha256

class CCoinPackage:
    def __init__(self, got_bytes : bytes = b'', pkg_type : str = '', data : bytes = b'') -> None:
        self.__bytes = got_bytes

        self.__type = pkg_type
        self.__data = data

    def unpackage_data(self):
        res = {}

        data_copy = self.__data
        pkg_type = data_copy[:PKG_TYPE_SIZE]
        
        for key, item in PKG_TYPE_VARS.items():
            if item == pkg_type:
                res['type'] = key

    def package_data(self):
        res = b''
        res += PKG_TYPE_VARS[self.__type]
        res += int.to_bytes(len(self.__data), DATA_LEN_SIZE, 'big')
        res += self.__data
        res = res[:HASH_OFFSET] + self.__hash_package(res) + res[HASH_OFFSET:]

        return res

    def __hash_package(self, data): return sha256(data).digest()