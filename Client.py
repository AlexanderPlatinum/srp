import socket

import User
import Utilities
import Constants

BUFFER_SIZE = 32
HOST = 'localhost'
PORT = 7777


class Client(object):
    __socket = socket.socket()

    def __init__(self):
        self.__socket.connect((HOST, PORT))

    def run(self):
        while 1:
            command = input("> ")
            self.__handle_all(command)

    def __handle_all(self, command):
        if command == "login":
            self.__handle_login()
        elif command == "register":
            self.__handle_register()
        else:
            print("Command not found!")

    def __handle_login(self):
        login = input("login: ")
        password = input("password: ")

        a = Utilities.make_rand()
        A = pow(Constants.G, a, Constants.N)

        self.__socket.send("LOGIN".encode())
        self.__socket.send(login.encode())
        self.__socket.send(str(A).encode())

        B = int(self.__socket.recv(BUFFER_SIZE).decode().replace(' ', ''))
        salt = int(self.__socket.recv(BUFFER_SIZE).decode().replace(' ', ''))

        u = Utilities.make_hash(Utilities.format2(A, B))
        x = Utilities.make_hash(Utilities.format2(salt, password))

        client_S = pow(B - Constants.K * pow(Constants.G, x, Constants.N), a + u * x, Constants.N)
        client_K = Utilities.make_hash(str(client_S))

        hash_N = Utilities.make_hash(str(Constants.N))
        hash_G = Utilities.make_hash(str(Constants.G))
        hash_I = Utilities.make_hash(login)

        client_M = Utilities.make_hash(Utilities.format6(hash_N ^ hash_G, hash_I, salt, A, B, client_K))
        self.__socket.send(str(client_M).encode())

        R_server = int(self.__socket.recv(BUFFER_SIZE).decode().replace(' ', ''))
        R_client = Utilities.make_hash(Utilities.format3(A, client_M, client_K))

        if R_client == R_server:
            print("Auth good, session_key := " + str(client_K))
        else:
            print("Auth error")

    def __handle_register(self):
        user = User.User

        user.login = input("login: ")
        password = input("password: ")

        salt = Utilities.make_rand()
        x = Utilities.make_hash(Utilities.format2(salt, password))
        verifier = pow(Constants.G, x, Constants.N)

        user.salt = str(salt)
        user.verifier = str(verifier)

        self.__send_register_data(user)

    def __send_register_data(self, user: User):
        self.__send_str('REGISTER')
        self.__send_str(user.login)
        self.__send_str(user.salt)
        self.__send_str(user.verifier)

    def __send_str(self, to_send: str):
        str_len = len(to_send)
        need = BUFFER_SIZE - str_len + 1
        temp = to_send.ljust(need, ' ')
        self.__socket.send(bytes(temp, 'ascii'))


def main():
    client = Client()
    client.run()


if __name__ == "__main__":
    main()
