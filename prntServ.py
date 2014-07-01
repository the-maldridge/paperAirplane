import logging
import socket
import json
import random
import os

class Spooler():
    def __init__(self, spooldir):
        try:
            os.chdir(spooldir)
        except OSError as e:
            logging.debug("Could not chdir to spooldir: %s", e)
            logging.warning("Couldn't open spooler directory, trying to create...")
            try:
                os.mkdir(spooldir)
                logging.info("Successfully created spooler directory %s", spooldir)
                os.chdir(spooldir)
            except OSError as e:
                logging.error("Could not use specified spooling directory: %s", e)
        logging.info("Spooler successfully initialized")

    def rndSpoolFile(self):
        num = random.random()
        num *= 10000
        return str(int(num))

    def spoolJob(self, jobToSpool):
        job = {}
        logging.debug("Locking job")
        job["locked"] = True
        logging.info("Spooling Job")
        if "/Duplex true" in jobToSpool:
            job["duplex"] = True
        else:
            job["duplex"] = False
        job["postScript"] = jobToSpool
        jobFile = open(self.rndSpoolFile(), 'w')
        json.dump(job, jobFile)

class Printer():
    def __init__(self, bindaddr, port, name):
        logging.info("Creating new printer %s on %s:%s", name, bindaddr, port)
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((bindaddr, port))
        except Exception as e:
            logging.error("Failed to bind printer %s", name)
            logging.error(e)
        logging.info("Initializing new spooler for %s", name)
        self.spooler = Spooler(name)

    def listener(self):
        self.s.listen(1)
        con, addr = self.s.accept()
        self.getJob(con, addr)

    def getJob(self, con, addr):
        job = ""
        data = ""
        con.settimeout(1)
        while("%%EOF" not in job):
            try:
                data = con.recv(1024)
                job += data
            except Exception as e:
                logging.error("Encountered error %s", e)
                break
        logging.debug("{} wrote:".format(addr))
        logging.debug(job)
        self.spooler.spoolJob(job)

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Initializing prntSrv in test mode")
    printer = Printer(socket.gethostbyname(socket.gethostname()), 9001, "test")
    printer.listener()
