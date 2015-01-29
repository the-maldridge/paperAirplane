import sqlite3
import MySQLdb
import logging

class BillingDB():
    def __init__(self, config):
        self.logger = logging.getLogger("DB-DRVR")

        if config["mode"] == "sqlite":
            self.logger.info("Selecting SQLite database driver")
            self.conn = sqlite3.connect(config["sqlite"]["path"])
        else:
            self.logger.info("Selecting mySQL database driver")
            user = config["mysql"]["user"]
            host = config["mysql"]["host"]
            passwd = config["mysql"]["passwd"]
            db = config["mysql"]["db"]
            try:
                self.logger.info("Attempting to connect to %s on %s", db, host)
                self.conn = MySQLdb.connect(host, user, passwd, db)
                self.logger.info("Connection successful")
            except:
                self.logger.error("Serious database connection error occured")

        try:
            self.logger.debug("Attempting to aquire DB cursor")
            self.c = self.conn.cursor()
            self.logger.debug("Aquired DB cursor")
        except:
            self.logger.error("Could not aquire DB cursor")
            
    def getUserBalance(self, username):
        cmd = "SELECT BALANCE FROM users WHERE username = %s"
        self.logger.debug("Executing: " + cmd)
        self.c.execute(cmd, username)
        balance = self.c.fetchall()
        return int(balance[0][0])

    def billUser(self, username, cost):
        current = self.getUserBalance(username)
        current = current - cost
        cmd = "UPDATE users SET BALANCE = %s WHERE username = %s"
        self.logger.debug("About to execute: " + cmd)
        self.c.execute(cmd, (current, username))
        self.conn.commit()

    def getUsers(self): 
        self.c.execute("SELECT * FROM users")
        return self.c.fetchall()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    configObj = {"mode":"mysql","mysql":{"user":"silenceDoGood","host":"localhost","passwd":"franklin","db":"paperAirplane"}}
    dat = BillingDB(configObj)

    bal = dat.getUserBalance("maldridge")
    logging.info("user maldridge has %d in their account", bal)
    dat.billUser("maldridge", 5)
    bal = dat.getUserBalance("maldridge")
    logging.info("user maldridge now has %d in their account", bal)
