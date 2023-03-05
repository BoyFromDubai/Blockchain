
class PackageData:
    def __init__(self, pkg_data : bytes = b'') -> None:
        self.pkg_data = pkg_data

    def package_data(self): return b''
    
    def parse_data(self): return {'data': None}
    
class VersionData(PackageData):
    VERSION_MSG_LEN = 2

    def __init__(self, version : bytes = b'', pkg_data: bytes = b'') -> None:
        super().__init__(pkg_data)
        self.version = version
    
    def package_data(self) -> bytes: return int.to_bytes(self.version, self.VERSION_MSG_LEN, 'big')

    def parse_data(self) -> dict: return {'version': int.from_bytes(self.pkg_data, 'big')}
    
class PeersRequestData(PackageData):
    def __init__(self, pkg_data: bytes = b'') -> None:
        super().__init__(pkg_data)
    

    
class PeersAckData(PackageData):
    def __init__(self, kwargs : dict = {}, pkg_data: bytes = b'') -> None:
        super().__init__(pkg_data)
        self.peers_ips = kwargs['peers_ips']

    def package_data(self) -> bytes:
        res = b''
        
        for i in range(len(self.peers_ips)):
            if i != len(self.peers_ips) - 1:
                res += (self.peers_ips[i] + '\n').encode()
            else:
                res += self.peers_ips[i].encode()
        
        return res
    
    def parse_data(self) -> dict: return { 'ips': self.pkg_data.decode().split('\n')}

class BlocksRequestData(PackageData):
    CUR_CHAIN_LEN_MSG_LEN = 2

    def __init__(self, cur_chain_len : int, last_blk_hash : bytes, pkg_data: bytes = b'') -> None:
        super().__init__(pkg_data)
        self.cur_chain_len = cur_chain_len
        self.last_blk_hash = last_blk_hash

    def package_data(self) -> bytes:
        res = int.to_bytes(self.cur_chain_len, self.CUR_CHAIN_LEN_MSG_LEN, 'big')
        res += self.last_blk_hash

        return res
    
    def parse_data(self):
        res = {}
        res['chain_len'] = int.to_bytes(self.pkg_data[:self.CUR_CHAIN_LEN_MSG_LEN], 'big')
        res['blk_hash'] = self.pkg_data[self.CUR_CHAIN_LEN_MSG_LEN:]

        return res
    
class StopSignalData(PackageData):
    def __init__(self, pkg_data: bytes = b'') -> None:
        super().__init__(pkg_data)
