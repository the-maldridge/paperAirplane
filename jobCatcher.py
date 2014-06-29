import logging
import SocketServer

class JobHandler():
    def handle():
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        logging.debug("{} wrote:".format(self.client_address[0]))
        logging.debug(self.data)

class Printer():
    def __init__(self, bindaddr, port, name):
        logging.info("Creating new printer %s on %s:%s", name, bindaddr, port)
        try:
            self.server = SocketServer.TCPServer((bindaddr, port), JobHandler)
        except Exception as e:
            logging.error("Failed to bind printer %s", name)
            logging.error(e)

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Initializing jobCatcher in test mode")
    printer = Printer("192.168.42.214", 9001, "test")
    printer.server.serve_forever()
