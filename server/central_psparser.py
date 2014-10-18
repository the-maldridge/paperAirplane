import logging
import json
import re

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
        numPages = None
        self.logger.debug("Computing page count for %s", jid)

        rgxresult = re.search('%%Pages: [0-9]*', ps)
        logging.debug("rgxresult: {0}".format(rgxresult.group(0)))

        if(rgxresult != None) :
            numPages = int(re.search('%%Pages: [0-9]*', ps).group(0).split(" ")[1])
            self.logger.debug("File is adobe compliant, suspect to be {0} pages".format(numPages))
        else:
            self.logger.error("File is not adobe compliant, page count indeterminate.")
        return numPages

