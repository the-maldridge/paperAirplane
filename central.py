import logging
import SocketServer
import json

class IncommingJob(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(256)
        job = data
        while(len(data) != 0):
            job += data
            data = self.request.recv(256)
        logging.debug(job)
        logging.debug("Replying to microSpooler at %s", self.client_address[0])
        self.request.send("EOF")

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

