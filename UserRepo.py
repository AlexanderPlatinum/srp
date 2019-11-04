import User


class UserRepo(object):
    users = []

    def add_user(self, user: User.User):
        self.users.append(user)

    def get_by_login(self, login):
        for user in self.users:
            print(user.login)
            if user.login == login:
                return user

        return None

    def get_all(self):
        return self.users
