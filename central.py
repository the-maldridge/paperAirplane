import logging
import socket
import json
import tempfile
import base64
import threading
import database
import time
import Queue
import os

class IncommingJob():
    def __init__(self, con, addr, baseDir, toBill):
        self.toBill = toBill
        self.con = con
        self.addr = addr
        #need to improve this
        logging.debug("Current path is %s", os.getcwd())
        if(baseDir not in os.getcwd()):
            try:
                logging.info("Pivoting to master spool directory")
                os.chdir(baseDir)
                logging.debug("Successfully found master spool directory")
            except OSError:
                logging.warning("Could not use master spool directory")
                logging.warning("Attempting to create new spool directory")
                os.mkdir(baseDir)
                os.chdir(baseDir)
                logging.info("Successfully found master spool directory")
        else:
            logging.debug("Already in spooldir")
        jobRaw = self.getJob()
        jid = self.saveJob(jobRaw)
        self.sendToBilling(jid)

    def getJob(self):
        logging.debug("Processing new job from %s", self.addr[0])
        self.con.settimeout(1)
        data = self.con.recv(256)
        jobJSON = data
        while(len(data) != 0):
            data = self.con.recv(256)
            jobJSON += data
        job = json.loads(base64.b64decode(jobJSON))
        logging.info("Recieved job %s from %s on %s", job["name"], job["originUser"], job["originPrinter"])
        return job

    def sendToBilling(self, jid):
        logging.info("made it to billing hook for %s", jid)

    def saveJob(self, job):
        jid = job["name"]
        spoolFile = open(jid, 'w')
        json.dump(job, spoolFile)
        spoolFile.close()
        return jid

class Spooler():
    def __init__(self, bindaddr, bindport, spooldir, toBill):
        self.bindaddr = bindaddr
        self.bindport = bindport
        self.spooldir = spooldir
        self.toBill = toBill
        try:
            logging.info("Initializing master spooler on %s:%s", bindaddr, bindport)
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((bindaddr, bindport))
        except Exception as e:
            logging.exception("Could not bind: %s", e)
        self.run()

    def listener(self):
        self.s.listen(5)
        con, addr = self.s.accept()
        t = threading.Thread(target=IncommingJob, args=(con, addr, self.spooldir, self.toBill))
        t.daemon = True
        t.start()

    def run(self):
        while(True):
            self.listener()

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

