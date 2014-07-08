import logging
import SocketServer
import json
import tempfile
import base64
import threading
import database
import time
import Queue

class IncommingJob(SocketServer.BaseRequestHandler):

    def handle(self):
        logging.debug("Processing new job from %s", self.client_address[0])
        data = self.request.recv(256)
        jobJSON = data
        while(len(data) != 0):
            data = self.request.recv(256)
            jobJSON += data
        self.job = json.loads(base64.b64decode(jobJSON))
        logging.info("Recieved job %s from %s on %s", self.job["name"], self.job["originUser"], self.job["originPrinter"])

    def sendToBilling(self, jid):
        pass

    def saveJob(self, baseDir, job):
        jid = job["name"]
        os.chdir(baseDir)
        spoolFile = open(jid, 'w')
        json.dump(job, jid)
        self.sendToBilling(jid)

class Spooler():
    def __init__(self, bindaddr, bindport, spooldir, toBill):
        try:
            logging.info("Initializing master spooler on %s:%s", bindaddr, bindport)
            server = SocketServer.TCPServer((bindaddr, bindport), IncommingJob)
            server.serve_forever()
        except Exception as e:
            logging.exception("Could not bind: %s", e)

class PSParser():
    def __init__(self):
        logging.info("Loaded PostScript Parser")
        
    def __getPSFromJID(self, jid):
        jobFile = open(jid, 'r')
        job = json.load(jobFile)
        jobFile.close()
        return job["postscript"]

    def isDuplex(self, jid):
        ps = self.__getPSFromJID(jid)
        if("/Duplex true" in ps):
            logging.debug("job %s is duplex enabled", jid)
            return True
        else:
            logging.debug("job %s is not duplex enabled", jid)
            return False

    def isColor(self, ps, jid):
        logging.debug("Checking to see if %s is in color", jid)

    def pageCount(self, jid):
        ps = self.__getPSFromJID(jid)
        logging.debug("Computing page count for %s", jid)
        numPages = ps.count("%%Page:")
        return numPages

class Billing():
    def __init__(self, path, toBill):
        logging.info("Initializing Billing Manager")
        logging.debug("Attempting to connect to database")
        self.db = database.BillingDB(path)
        logging.debug("Successfully connected to database!")
        logging.debug("Attempting to create a parser")
        self.parser = PSParser()
        logging.debug("Successfully created parser")

    def computeCost(self, jid):
        cost = self.parser.pageCount(jid)
        if self.parser.isDuplex(jid):
            cost = cost / 2
        logging.info("Billing user %s %s credit(s) for job %s", job["originUser"], cost, jid)

class CentralControl():
    def __init__(self):
        logging.info("Initializing CentralControl")

        self.toBill = Queue.Queue()

        self.threads = []
        self.threads.append(threading.Thread(target=Spooler, args=("localhost", 3201, "coreSpool", self.toBill)))
        self.threads.append(threading.Thread(target=Billing, args=("test.sqlite", self.toBill)))

        logging.info("GOING POLYTHREADED")
        for thread in self.threads:
            thread.daemon = True
            thread.start()

        while(True):
            if not any([thread.isAlive() for thread in self.threads]):
                break
            else:
                time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    logging.info("Starting in debug mode")
    test = CentralControl()

