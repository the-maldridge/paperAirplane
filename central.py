import logging
import SocketServer
import json
import tempfile
import base64
import threading
import time
import Queue

class IncommingJob(SocketServer.BaseRequestHandler):
    def handle(self):
        logging.debug("Processing new job from %s", self.client_address[0])
        data = self.request.recv(256)
        jobJSON = data
        while(len(data) != 0):
            data = self.request.recv(256)
            jobJSON += data
        self.job = json.loads(base64.b64decode(jobJSON))
        logging.debug("Recieved job %s from %s on %s", self.job["name"], self.job["originUser"], self.job["originPrinter"])

class Spooler():
    def __init__(self, bindaddr, bindport):
        try:
            logging.info("Initializing master spooler on %s:%s", bindaddr, bindport)
            server = SocketServer.TCPServer((bindaddr, bindport), IncommingJob)
            server.serve_forever()
        except Exception as e:
            logging.exception("Could not bind: %s", e)

class Billing():
    def __init__(self):
        logging.info("Initializing Billing Manager")
        while True:
            logging.info("pong")
            time.sleep(1000)

class CentralControl():
    def __init__(self):
        logging.info("Initializing CentralControl")
        q = Queue.Queue()

        threads = []
        threads.append(threading.Thread(target=Spooler, args=("localhost", 3201)))
        threads.append(threading.Thread(target=Billing))

        logging.info("GOING POLYTHREADED")
        for thread in threads:
            thread.daemon = False
            thread.start()

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    logging.info("Starting in debug mode")
    test = CentralControl()

