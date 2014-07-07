import logging
import SocketServer
import json
import tempfile
import base64
import threading
import database
import time

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

class Spooler():
    def __init__(self, bindaddr, bindport):
        try:
            logging.info("Initializing master spooler on %s:%s", bindaddr, bindport)
            server = SocketServer.TCPServer((bindaddr, bindport), IncommingJob)
            server.serve_forever()
        except Exception as e:
            logging.exception("Could not bind: %s", e)

class PSParser():
    def __init__(self):
        logging.info("Loaded PostScript Parser")

    def isDuplex(self, ps, jid):
        if("/Duplex true" in ps):
            logging.debug("job %s is duplex enabled", jid)
            return True
        else:
            logging.debug("job %s is not duplex enabled", jid)

    def isColor(self, ps, jid):
        logging.debug("Checking to see if %s is in color", jid)

    def pageCount(self, ps, jid):
        logging.debug("Computing page count for %s", jid)

class Billing():
    def __init__(self, path):
        logging.info("Initializing Billing Manager")
        logging.debug("Attempting to connect to database")
        self.db = database.BillingDB(path)
        logging.debug("Successfully connected to database!")

class CentralControl():
    def __init__(self):
        logging.info("Initializing CentralControl")

        self.threads = []
        self.threads.append(threading.Thread(target=Spooler, args=("localhost", 3201)))
        self.threads.append(threading.Thread(target=Billing, args=("test.sqlite",)))

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

