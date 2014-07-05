The paperAirplane software has 3 major components, described as follows.

The Microspooler
----------------
This is the program that runs the virtual printer(s).  Depending on the environment, there may be one or multiple of these, and they can support
one or more virtual printers as needed.  This component includes a socket server that is able to handle connections from clients.  When a print
job comes in, the microspooler connects to central control to inform that a new job is available, and transfers the job over to central control.
The microspooler also communicates with a local daemon to determine who sent the print job based on the user name, which is assumed to be globally
unique across the environment.

The local daemon
----------------
This component runs on the individual client workstations and serves 2 key functions:
 * Determine who is logged in.  The microspooler needs to know who to bill for the job, so it contacts the daemon to find out who is logged in to 
that specific workstation.
 * Display status information.  Should show what printers are online and what the user's credit balance is.

Central Control
---------------
All print jobs eventually run through central control.  This server process consumes jobs from the microspoolers as well as handling billing and
daemon update requests.  The central controller knows how to talk to the billing environment and how to talk to the individual physical printers.

