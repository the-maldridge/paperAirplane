import logging
import socket
import json
import tempfile
import base64
import threading
import database
import time
import Queue
import os
import sys

import central_spooler
import central_billing
import central_jobcontrol
import central_psoutput

class CentralControl():
    def __init__(self):
        self.logger = logging.getLogger("CentralControl")

        self.logger.info("Initializing CentralControl")
        self.logger.debug("Attempting to get config")
        config = self.getConfig()
        self.logger.debug("Successfully got config")

        self.queues = {}
        self.queues["threadControl"] = Queue.Queue()
        self.queues["toBill"] = Queue.Queue()
        self.queues["toRelease"] = Queue.Queue()
        self.queues["toPrint"] = Queue.Queue()


        self.threads = []
        self.threads.append(threading.Thread(target=central_spooler.Spooler, args=(config, self.queues)))
        self.threads.append(threading.Thread(target=central_billing.Billing, args=(config, self.queues)))
        self.threads.append(threading.Thread(target=central_jobcontrol.JobRelease, args=(config, self.queues)))
        self.threads.append(threading.Thread(target=central_psoutput.PSOutput, args=(config, self.queues)))

        #set up startup locks before running:
        self.queues["threadControl"].put("spoolerStartup")


    def getConfig(self):
        try:
            configFile = open("config.json")
            conf = json.load(configFile)
            configFile.close()
            return conf
        except Exception as e:
            self.logger.critical("Malformed config file: %s", e)
            sys.exit(1)

    def run(self):
        self.logger.info("GOING POLYTHREADED")
        for thread in self.threads:
            thread.daemon = True
            thread.start()

        # we need to keep this thread running to check thread status
        while(True):
            if not any([thread.isAlive() for thread in self.threads]):
                break
            else:
                time.sleep(1)

        self.logger.info("All threads have exited, now exiting program")

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    logging.info("Starting in debug mode")
    test = CentralControl()
    test.run()
