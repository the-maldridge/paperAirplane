import logging
import database
import json
import central_psparser

class Billing():
    def __init__(self, config, queues):
        self.threadOps = queues["threadControl"]
        self.toBill = queues["toBill"]
        self.toPrint = queues["toPrint"]

        dbpath = config["billing"]["path"]

        self.logger = logging.getLogger("Billing")

        #init some internal instances of stuff
        self.logger.info("Initializing Billing Manager")

        self.logger.debug("Attempting to connect to database")
        self.db = database.BillingDB(dbpath)
        self.logger.debug("Successfully connected to database!")

        self.logger.debug("Attempting to create a parser")
        self.parser = central_psparser.PSParser()
        self.logger.debug("Successfully created parser")

        #enter main loop
        self.run()

    def run(self):
        while(True):
            jid = self.toBill.get(block=True)
            cost = self.computeCost(jid)
            user = self.getUser(jid)
            self.logger.info("Billing user %s %s credit(s) for job %s", user, cost, jid)
            self.logger.debug("Forwarding %s to print manager", jid)
            self.toPrint.put(jid)

    def computeCost(self, jid):
        cost = self.parser.pageCount(jid)
        if self.parser.isDuplex(jid):
            cost = ceiling(cost / 2)
        return cost

    def getUser(self, jid):
        f = open(jid, 'r')
        j = json.load(f)
        user = j["originUser"]
        f.close()
        return user

