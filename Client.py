import socket

import User
import Utilities
import Constants

BUFFER_SIZE = 128
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

        sended_data = 'LOGIN' + ' ' + login + ' ' + str(A)
        self.__socket.send(sended_data.encode())

        recived_data = self.__socket.recv(BUFFER_SIZE).decode().split(' ')
        B = int(recived_data[0])
        salt = int(recived_data[1])

        print(recived_data)

        u = Utilities.make_hash(Utilities.format2(A, B))
        x = Utilities.make_hash(Utilities.format2(salt, password))

        client_S = pow(B - Constants.K * pow(Constants.G, x, Constants.N), a + u * x, Constants.N)
        client_K = Utilities.make_hash(str(client_S))

        hash_N = Utilities.make_hash(str(Constants.N))
        hash_G = Utilities.make_hash(str(Constants.G))
        hash_I = Utilities.make_hash(login)

        client_M = Utilities.make_hash(Utilities.format6(hash_N ^ hash_G, hash_I, salt, A, B, client_K))
        self.__socket.send(str(client_M).encode())

        R_server = int(self.__socket.recv(BUFFER_SIZE).decode())
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
        send_data = 'REGISTER' + ' ' + user.login + ' ' + user.salt + ' ' + user.verifier
        self.__socket.send(send_data.encode())



def main():
    client = Client()
    client.run()


if __name__ == "__main__":
    main()
