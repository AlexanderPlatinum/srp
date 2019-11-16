import socket

import User
import UserRepo
import Utilities
import Constants

BUFFER_SIZE = 128
HOST = 'localhost'
PORT = 7777

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
            recive_data = connection.recv(BUFFER_SIZE).decode().split(' ')
            if recive_data[0] is not None:
                self.__handle_all(connection, recive_data)

    def __handle_all(self, connection, recive_data):
        if recive_data[0] == "LOGIN":
            self.__handle_login(connection, recive_data)
        elif recive_data[0] == "REGISTER":
            self.__handle_register(recive_data)
        else:
            print("method not found!")

    def __handle_register(self, recive_data):
        login = recive_data[1]
        salt = recive_data[2]
        verifier = recive_data[3]

        user = User.User(login=login, salt=salt, verifier=verifier)
        self.__userRepo.add_user(user)

    def __handle_login(self, connection, recive_data):
        print("I am in login")
        login = recive_data[1]
        A = int(recive_data[2])
        user: User.User = self.__userRepo.get_by_login(login)

        if user is not None:
            v = int(user.verifier)
            b = Utilities.make_rand()
            B = (Constants.K * v + pow(Constants.G, b, Constants.N)) % Constants.N

            sended_data = str(B) + ' ' + user.salt
            connection.send(sended_data.encode())

            u = Utilities.make_hash(Utilities.format2(A, B))
            server_S = pow(A * pow(v, u, Constants.N), b, Constants.N)
            server_K = Utilities.make_hash(str(server_S))

            hash_N = Utilities.make_hash(str(Constants.N))
            hash_G = Utilities.make_hash(str(Constants.G))
            hash_I = Utilities.make_hash(login)
            s = int(user.salt)

            server_M = Utilities.make_hash(Utilities.format6(hash_N ^ hash_G, hash_I, s, A, B, server_K))
            client_M = int(connection.recv(BUFFER_SIZE).decode())

            print('server_M := ', server_M)
            print('client_M := ', client_M)

            if server_M == client_M:
                print("Session key := " + str(server_K))
                R = Utilities.make_hash(Utilities.format3(A, client_M, server_K))
                connection.send(str(R).encode())
                #send_str(connection, str(R))
            else:
                print("Auth error")
        else:
            print("User not found")


def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
