#!/usr/bin/env python
import signal

def handleSig(signum, stack):
    print 'Got signal: ' + str(signum)
    pass

 
for s in [x for x in dir(signal) if x.startswith("SIG")]:
    signum = getattr(signal, s)
    if signum in [9,19,0]:
        continue
    signal.signal(signum, handleSig)

while True:
    pass
