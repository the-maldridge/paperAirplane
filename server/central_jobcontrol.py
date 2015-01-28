import logging

class JobRelease():
    def __init__(self, config, queues):
        self.threadOps = queues["threadControl"]
        self.toRelease = queues["toRelease"]
        self.toBill = queues["toBill"]

        self.logger = logging.getLogger("JobRelease")

        self.run()

    def run(self):
        #release all jobs immeadiately, need to rewrite at some point
        while(True):
            jid = self.toRelease.get(block=True)
            self.logger.debug("Forwarding job %s for billing", jid)
            self.toBill.put(jid)
    
