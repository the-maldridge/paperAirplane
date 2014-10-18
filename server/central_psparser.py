import logging
import json

class PSParser():
    def __init__(self):
        self.logger = logging.getLogger("PSParser")
        self.logger.info("Loaded PostScript Parser")
        
    def __getPSFromJID(self, jid):
        jobFile = open(jid, 'r')
        job = json.load(jobFile)
        jobFile.close()
        return job["postscript"]

    def isDuplex(self, jid):
        ps = self.__getPSFromJID(jid)
        if("/Duplex true" in ps):
            self.logger.debug("job %s is duplex enabled", jid)
            return True
        else:
            self.logger.debug("job %s is not duplex enabled", jid)
            return False

    def pageCount(self, jid):
        ps = self.__getPSFromJID(jid)
        self.logger.debug("Computing page count for %s", jid)
        numPages = ps.count("%%Page:")
        return numPages

