import logging
import socket
import json
import hashlib
import time
import os

class MicroSpooler():
    def __init__(self, originPrinter):
        spooldir = originPrinter
        self.name = originPrinter
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

    def spoolJob(self, jobToSpool, originUser, originPrinter):
        job = {}
        logging.debug("New job from user %s on %s", originUser, originPrinter)
        job["originPrinter"] = originPrinter
        job["originUser"] = originUser
        jobName = self.spoolFileName()
        job["name"] = jobName
        job["postscript"] = jobToSpool
        logging.info("Spooling Job %s for %s on %s", jobName, originUser, originPrinter)
        try:
            jobFile = open(jobName, 'w')
            json.dump(job, jobFile)
            self.alertSpooler("localhost", job)
            logging.debug("Successfully spooled %s", jobName)
        except Exception as e:
            logging.error("Encountered error while spooling: %s", e)

 
    def alertSpooler(self, central, job):
        logging.debug("Alerting the central controller")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((central, 3201))
            logging.debug("Attempting to send job to central")
            sock.sendall(json.dumps(job))
            logging.debug("Waiting on acknowledgement from central")
            sock.settimeout(15)
            ackmsg=""
            while("EOF" not in ackmsg):
                ackmsg += sock.recv(16)                
            logging.debug("Transmission to central succeeded")
        except Exception as e:
            logging.error("An error was encountered while attempting to alert the central spooler: %s", e)
        finally:
            sock.close()
            
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

    def getUser(self, addr):
        logging.debug("Determining user for address %s", addr[0])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr[0], 3200))
        try:
            originUser = sock.recv(512).strip()
        finally:
            sock.close()
        logging.debug("User determined to be %s", originUser)
        return originUser

    def getJob(self, con, addr):
        con.settimeout(1)
        data = con.recv(256)
        job = data
        while(len(data) != 0):
            try:
                data = con.recv(1024)
                job += data
            except Exception as e:
                logging.error("Encountered error %s", e)
                break
        user = self.getUser(addr)
        self.spooler.spoolJob(job, user, self.name)

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Initializing the MicroSpooler in test mode")
    printer = Printer("localhost", 9001, "test")
    while(True):
        printer.listener()
