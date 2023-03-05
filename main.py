import sys
from src.console_user.console_user import ConsoleUser
from src.blockchain import Blockchain
# app = create_app()
# wallet = Wallet()


if __name__ == '__main__':
    user = ConsoleUser()
    user.start_input()
