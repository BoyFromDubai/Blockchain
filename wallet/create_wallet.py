from wallet import Wallet
import os

if __name__ == '__main__':

    if not os.path.exists('wallet/wallet.bin'):
        wallet = Wallet()
        sk = wallet.sk

        with open('wallet/wallet.bin', 'wb') as f:
            f.write(sk.to_string())
        
    else:
        print('Keys already exists!')

    # with open('wallet/wallet.bin', 'rb') as f:
    #     key1 = f.read()

    #     sk = ecdsa.SigningKey.from_string(key1, ecdsa.SECP256k1)
    #     print(sk)
    #     print(sk.to_string())

    #     # sign = sk.sign(b'asd')
    #     # print(pk.verify(sign, b"message"))