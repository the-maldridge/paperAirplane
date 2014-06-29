import logging
import socket

class JobHandler():
    def __init__(self, socket, addr):
        job = ""
        socket.settimeout(1)
        while(True):
            try:
                data = socket.recv(1024).strip()
                print "polled"
                if data is not None:
                    job += data
            except Exception as e:
                print "connection closed"
                break
        logging.debug("{} wrote:".format(addr))
        logging.debug(job)
        logging.error("Encountered error %s", e)
"""from here, spool the job in a locked state, then when the accounting module clears the job, release the lock"""

class Printer():
    def __init__(self, bindaddr, port, name):
        logging.info("Creating new printer %s on %s:%s", name, bindaddr, port)
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((bindaddr, port))
        except Exception as e:
            logging.error("Failed to bind printer %s", name)
            logging.error(e)

    def listener(self):
        self.s.listen(1)
        self.con, self.addr = self.s.accept()
        self.job = JobHandler(self.con, self.addr)

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Initializing jobCatcher in test mode")
    printer = Printer("192.168.42.214", 9001, "test")
    printer.listener()
