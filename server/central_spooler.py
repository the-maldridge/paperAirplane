import logging
import socket
import json
import base64
import Queue
import os

class IncommingJob():
    def __init__(self, con, addr, toRelease):
        self.toRelease = toRelease
        self.con = con
        self.addr = addr

        self.logger = logging.getLogger("JobHandler")

        jobRaw = self.getJob()
        jid = self.saveJob(jobRaw)
        self.sendToBilling(jid)

    def getJob(self):
        self.logger.debug("Processing new job from %s", self.addr[0])
        self.con.settimeout(1)
        data = self.con.recv(256)
        jobJSON = data
        while(len(data) != 0):
            data = self.con.recv(256)
            jobJSON += data
        job = json.loads(base64.b64decode(jobJSON))
        self.logger.info("Recieved job %s from %s on %s", job["name"], job["originUser"], job["originPrinter"])
        return job

    def sendToBilling(self, jid):
        self.logger.debug("Sending %s for job release", jid)
        self.toRelease.put(jid)

    def saveJob(self, job):
        jid = job["name"]
        spoolFile = open(jid, 'w')
        json.dump(job, spoolFile)
        spoolFile.close()
        return jid

class Spooler():
    def __init__(self, config, queues):
        self.threadOps = queues["threadControl"]
        self.toRelease = queues["toRelease"]

        bindaddr = config["spooler"]["bindAddr"]
        bindport = config["spooler"]["bindPort"]
        spooldir = config["global"]["spoolDir"]

        self.logger = logging.getLogger("CoreSpooler")

        #need to improve this
        # currently it moves us into the spooler's main directory
        self.logger.debug("Current path is %s", os.getcwd())
        if(spooldir not in os.getcwd()):
            try:
                self.logger.info("Pivoting to master spool directory")
                os.chdir(spooldir)
                self.logger.debug("Successfully found master spool directory")
            except OSError:
                self.logger.warning("Could not use master spool directory")
                self.logger.warning("Attempting to create new spool directory")
                os.mkdir(spooldir)
                os.chdir(spooldir)
                self.logger.info("Successfully found master spool directory")
        else:
            self.logger.debug("Already in spooldir")

        # attempt to bind the master spooler onto a port
        try:
            self.logger.info("Initializing master spooler on %s:%s", bindaddr, bindport)
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((bindaddr, bindport))
        except Exception as e:
            self.logger.exception("Could not bind: %s", e)

        #clear thread lock
        self.threadOps.get(False)
        self.threadOps.task_done()
        self.run()

    def listener(self):
        self.s.listen(5)
        con, addr = self.s.accept()
        t = threading.Thread(target=IncommingJob, args=(con, addr, self.toRelease))
        t.daemon = True
        t.start()

    def run(self):
        while(True):
            self.listener()

