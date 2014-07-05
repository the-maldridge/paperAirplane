import logging
import socket
import json
import hashlib
import time
import os

class MicroSpooler():
    def __init__(self, name):
        spooldir = name
        self.name = name
        try:
            os.chdir(spooldir)
        except OSError as e:
            logging.warning("Could not chdir to spooldir: %s", e)
            logging.warning("Couldn't open spooler directory, trying to create...")
            try:
                os.mkdir(spooldir)
                logging.info("Successfully created spooler directory %s", spooldir)
                os.chdir(spooldir)
            except OSError as e:
                logging.error("Could not use specified spooling directory: %s", e)
        logging.info("Spooler successfully initialized")

    def spoolFileName(self):
        fname = hashlib.sha256(str(time.time())+self.name).hexdigest()
        return fname[0:10]

    def spoolJob(self, jobToSpool, originPrinter):
        job = {}
        logging.debug("New job from %s", originPrinter)
        job["origin"] = originPrinter

        jobName = self.spoolFileName()
        logging.info("Spooling Job %s", jobName)
        try:
            jobFile = open(jobName, 'w')
            json.dump(job, jobFile)
            logging.debug("Successfully spooled %s", jobName)
        except Exception as e:
            logging.error("Encountered error while spooling: %s", e)

class Printer():
    def __init__(self, bindaddr, port, name):
        self.name = name
        logging.info("Creating new printer %s on %s:%s", name, bindaddr, port)
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((bindaddr, port))
        except Exception as e:
            logging.error("Failed to bind printer %s", name)
            logging.error(e)
        logging.info("Initializing new spooler for %s", name)
        self.spooler = MicroSpooler(name)

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
        self.spooler.spoolJob(job, self.name)

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Initializing the MicroSpooler in test mode")
    printer = Printer(socket.gethostbyname(socket.gethostname()), 9001, "test")
    printer.listener()
