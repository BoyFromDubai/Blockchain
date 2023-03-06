from hashlib import md5
from .data_field_helpers import *


PKG_TYPE_VARS = {
    'peers_request':                (b'\x01', PeersRequestData),
    'peers_ack':                    (b'\x02', PeersAckData),
    'version':                      (b'\x03', VersionData),
    'compare_nth_block_request':    (b'\x04', CompareNthBlockRequestData),
    'compare_nth_block_ack':        (b'\x05', CompareNthBlockAckData),

    'block_request':                (b'\x06', BlockRequestData),
    'block_ack':                    (b'\x07', BlockAckData),
     
    'tx_msg':                       (b'\x08', TxMsgData),
         
    'stop_signal':                  (b'\xFF', StopSignalData)
}

class CCoinPackage:
    def __init__(self) -> None:
        self.pkg_type_size = 1
        self.hash_offset = 4
        self.hash_size = 16
        self.data_len_size = 4

    def __check_got_msg(self, pkg):
        if pkg:
            pkg = pkg[:self.hash_offset] + pkg[self.hash_offset + self.hash_size:]
            got_hash_of_pkg = pkg[self.hash_offset:self.hash_offset + self.hash_size]
            actual_hash_of_pkg = self.__hash_package(pkg)
            
            if got_hash_of_pkg != actual_hash_of_pkg:
                return False
            else:
                return True


    def unpackage_data(self, pkg):
        res = {}

        pkg_not_broken = self.__check_got_msg(pkg)
        if pkg_not_broken:
            raise Exception('Broken package!')

        pkg_type = pkg[:self.pkg_type_size]
        handler_type_pair = None

        for key, item in PKG_TYPE_VARS.items():
            if item[0] == pkg_type:
                res['type'] = key
                handler_type_pair = item

        data_len = pkg[self.pkg_type_size + self.hash_size:self.pkg_type_size + self.hash_size + self.data_len_size]

        data_field = pkg[self.pkg_type_size + self.hash_size + self.data_len_size:self.pkg_type_size + self.hash_size + self.data_len_size + int.from_bytes(data_len, 'big')]
        res['data_dict'] = handler_type_pair[1](pkg_data=data_field).parse_data()
        
        return res
        

    def package_data(self, pkg_type: str, **kwargs):
        res = b''
        handler_type_pair = PKG_TYPE_VARS[pkg_type]
        res += handler_type_pair[0]
        data_field = handler_type_pair[1](**kwargs).package_data()
        print('FFFFF', data_field)
        res += int.to_bytes(len(data_field), self.data_len_size, 'big')
        res += data_field
        res = res[:self.hash_offset] + self.__hash_package(res) + res[self.hash_offset:]

        return res

    def __hash_package(self, data): return md5(data).digest()


    