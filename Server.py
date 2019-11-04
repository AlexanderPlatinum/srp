import socket

import User
import UserRepo
import Utilities
import Constants

BUFFER_SIZE = 32
HOST = 'localhost'
PORT = 7777


def send_str(connection, to_send: str):
    str_len = len(to_send)
    need = BUFFER_SIZE - str_len + 1
    temp = to_send.ljust(need, ' ')
    connection.send(bytes(temp, 'ascii'))


class Server(object):
    __userRepo = UserRepo.UserRepo()
    __socket = socket.socket()

    def __init__(self):
        self.__socket.bind((HOST, PORT))
        self.__socket.listen()
        print("Server listen in port " + str(PORT))

    def run(self):
        while 1:
            connection, address = self.__socket.accept()
            func = connection.recv(BUFFER_SIZE).decode().replace(' ', '')
            print(func)
            if func is not None:
                self.__handle_all(connection, func)

    def __handle_all(self, connection, func):
        if func == "LOGIN":
            self.__handle_login(connection)
        elif func == "REGISTER":
            self.__handle_register(connection)
        else:
            print("method not found!")

    def __handle_register(self, connection):
        print("I am in register")
        login = connection.recv(BUFFER_SIZE).decode().replace(' ', '')
        print("I have login")
        salt = connection.recv(BUFFER_SIZE).decode().replace(' ', '')
        print("I have salt")
        verifier = connection.recv(BUFFER_SIZE).decode().replace(' ', '')
        print("I have verifier")

        user = User.User(login=login, salt=salt, verifier=verifier)
        self.__userRepo.add_user(user)

        print(user.to_str())

    def __handle_login(self, connection):
        print("I am in login")
        login = connection.recv(BUFFER_SIZE).decode().replace(' ', '')
        A = int(connection.recv(BUFFER_SIZE).decode().replace(' ', ''))
        user: User.User = self.__userRepo.get_by_login(login)

        if user is not None:
            v = int(user.verifier)
            b = Utilities.make_rand()
            B = (Constants.K * v + pow(Constants.G, b, Constants.N)) % Constants.N

            send_str(connection, str(B))
            send_str(connection, user.salt)

            u = Utilities.make_hash(Utilities.format2(A, B))
            server_S = pow(A * pow(v, u, Constants.N), b, Constants.N)
            server_K = Utilities.make_hash(str(server_S))

            hash_N = Utilities.make_hash(str(Constants.N))
            hash_G = Utilities.make_hash(str(Constants.G))
            hash_I = Utilities.make_hash(login)
            s = int(user.salt)

            server_M = Utilities.make_hash(Utilities.format6(hash_N ^ hash_G, hash_I, s, A, B, server_K))
            client_M = int(connection.recv(BUFFER_SIZE).decode().replace(' ', ''))

            if server_M == client_M:
                print("Session key := " + str(server_K))
                R = Utilities.make_hash(Utilities.format3(A, client_M, server_K))
                send_str(connection, str(R))
            else:
                print("Auth error")
        else:
            print("User not found")


def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
