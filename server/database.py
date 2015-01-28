import sqlite3

class BillingDB():
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.c = self.conn.cursor()

    def getUserBalance(self, username):
        self.c.execute("SELECT BALANCE FROM users WHERE username = ?", (username,))
        balance = self.c.fetchall()
        return int(balance[0][0])

    def billUser(self, username, cost):
        current = self.getUserBalance(username)
        current = current - cost
        self.c.execute("UPDATE users SET BALANCE = ? WHERE username = ?", (current, username))
        self.conn.commit()

    def getUsers(self): 
        self.c.execute("SELECT * FROM users")
        return self.c.fetchall()

if __name__ == "__main__":
    dat = BillingDB("test.sqlite")
    print dat.getUserBalance("maldridge")
    dat.billUser("maldridge", 5)
    print dat.getUserBalance("maldridge")
    print dat.getUsers()
