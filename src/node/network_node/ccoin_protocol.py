from .constants import *
from hashlib import md5

class CCoinPackage:
    def __init__(self, got_bytes : bytes = b'', pkg_type : str = '', data : bytes = b'') -> None:
        self.__bytes = got_bytes

        if got_bytes:
            actual_data = self.__check_got_msg()
            if not actual_data:
                raise Exception('Broken package!')
        
        self.__type = pkg_type
        self.__data = data

    def __check_got_msg(self):
        if self.__bytes:
            pkg = self.__bytes[:HASH_OFFSET] + self.__bytes[HASH_OFFSET + HASH_SIZE:]
            got_hash_of_pkg = self.__bytes[HASH_OFFSET:HASH_OFFSET + HASH_SIZE]
            actual_hash_of_pkg = self.__hash_package(pkg)
            
            if got_hash_of_pkg != actual_hash_of_pkg:
                return False
            else:
                return True


    def __unpackage_data_field(self, pkg_type, data):
        res = {}

        if pkg_type == 'version':
            res['data'] = int.from_bytes(data, 'big')
        elif pkg_type == 'peers_ack':
            res['peers'] = data.decode().split('\n')

        print('-------------')
        print(res)

    def unpackage_data(self):
        res = {}

        data_copy = self.__bytes
        pkg_type = data_copy[:PKG_TYPE_SIZE]
        
        for key, item in PKG_TYPE_VARS.items():
            if item == pkg_type:
                res['type'] = key

        data_len = self.__bytes[PKG_TYPE_SIZE + HASH_SIZE:PKG_TYPE_SIZE + HASH_SIZE + DATA_LEN_SIZE]


        res['data'] = self.__bytes[PKG_TYPE_SIZE + HASH_SIZE + DATA_LEN_SIZE:PKG_TYPE_SIZE + HASH_SIZE + DATA_LEN_SIZE + int.from_bytes(data_len, 'big')]

        self.__unpackage_data_field(res['type'], res['data'])

        return res
        

    def package_data(self):
        res = b''
        res += PKG_TYPE_VARS[self.__type]
        res += int.to_bytes(len(self.__data), DATA_LEN_SIZE, 'big')
        
        res += self.__data
        # print('Hash: ', self.__hash_package(res))
        # print('Hashed: ', res)
        res = res[:HASH_OFFSET] + self.__hash_package(res) + res[HASH_OFFSET:]

        return res

    def __hash_package(self, data): return md5(data).digest()