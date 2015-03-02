import logging
import json
import os
import socket

class PSOutput():
    def __init__(self, config, queues):
        self.threadOps = queues["threadControl"]
        self.toPrint = queues["toPrint"]
        self.toBill = queues["toBill"]
        self.config = config

        self.logger = logging.getLogger("PrinterOutput")

        self.run()

    def run(self):
        while(True):
            jid = self.toPrint.get(block=True)
            self.logger.debug("Got print request for job %s", jid)
            try:
                self.printJob(jid)
                self.logger.debug("Printed job %s", jid)
                self.rmJob(jid)
            except:
                self.moveToGraveYard(jid)

    def printJob(self, jid):
        destPrinter = self.getDestPrinter(jid)
        realPrinter = self.config["printers"][destPrinter]["name"]
        printer = self.config["printers"][destPrinter]["address"]
        port =  self.config["printers"][destPrinter]["port"]
        self.logger.debug("Sending %s recieved on %s to %s", jid, destPrinter, realPrinter)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            jidJSON = self.getJobFile(jid)
            s.connect((printer, port))
            self.logger.debug("Transmitting PostScript...")
            #s.sendall(jidJSON["postscript"])
            s.close()
        except Exception as e:
            self.logger.critical("Encountered error while printing: %s", e)
            setRefund(jid, jidJSON)
            self.logger.debug("Sending %s for refund")
            raise e

    def getDestPrinter(self, jid):
        f = open(jid)
        j = json.load(f)
        f.close()
        return j["destPrinter"]

    def getJobFile(self, jid):
        f = open(jid)
        j = json.load(f)
        f.close()
        return j

    def rmJob(self, jid):
        self.logger.debug("Removing spool file for %s", jid)
        os.remove(jid)
        self.logger.info("Completed handling of %s", jid)

    def setRefund(self, jid, jidJSON):
        jidJSON["refund"] = True
        f = open(jid, 'w')
        print "saving updated jid file"
        json.dump(f, jidJSON)
        f.close()
        self.toBill.put(jid)

    def moveToGraveYard(self, jid):
        self.logger.warning("Moving unprintable job %s to graveyard.", jid)
