import logging
import SocketServer
import json
import tempfile

class IncommingJob(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(256)
        jobJSON = data
        while(len(data) != 0):
            jobJSON += data
            data = self.request.recv(256)
        logging.debug(jobJSON)
        self.job = json.loads(jobJSON)
        #logging.info("Received job %s", job["name"])

class Spooler():
    def __init__(self, bindaddr, bindport):
        server = SocketServer.TCPServer((bindaddr, bindport), IncommingJob)
        server.serve_forever()

class CentralControl():
    def __init__(self):
        logging.info("Initializing CentralControl")
        logging.debug("waiting for jobs...")
        test = Spooler("localhost", 3201)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    logging.info("Starting in debug mode")
    test = CentralControl()

