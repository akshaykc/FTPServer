'''
Created on Apr 13, 2016

@author: achaluv
'''
import socket
import threading
import segment
import random
import sys

class udpServer(threading.Thread):
    def __init__(self, udpServerPort, fileName, packetLossProb):
        threading.Thread.__init__(self)
        #self.hostName = hostName
        self.udpServerPort = udpServerPort
        self.fileName = fileName
        self.packetLossProb = float(packetLossProb)
        self.segSize = 1024
        self.randomNum = 0
        self.sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.udpServerPort))
        open(self.fileName, 'w').close()
    
    def run(self):
        print "Server thread started\n"
        #outputFile = open(self.fileName, "r+b")
        firstPacket = True
        seq = 0
        while True:
            data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            data = bytearray(data)
            remoteHost = addr[0]
            remotePort = addr[1]
            #print "received message:", data, addr
                
            segRcvd = segment.segmentResponse(data, len(data))
            checkSum = self.check(segRcvd)
            self.randomNum = random.uniform(0.0,1.0)
            #print self.packetLossProb
            if checkSum == 0 and self.randomNum >= self.packetLossProb:
                #print "Get ", segRcvd.getSeqNo(), " waiting ", seq
                if firstPacket or segRcvd.getSeqNo() == seq:
                    seq = segRcvd.getSeqNo() + segRcvd.getDataSize()
                    firstPacket = False
                    outputString = ''.join(chr(x) for x in segRcvd.getDataWithoutHeader())
                    with open(self.fileName, 'a') as outputFile: 
                        outputFile.write(outputString)
                        #print outputString
                else:
                    seq = seq
                    
                responseSegment = segment.segmentAck(seq, self.segSize)
                dataToSend = bytearray(responseSegment.getData())
                self.sock.sendto(dataToSend, (remoteHost, remotePort))
                    
            elif self.randomNum < self.packetLossProb:
                print "Packet loss, sequence number = ", segRcvd.getSeqNo()
        outputFile.close()
        self.sock.close()
        print "Server thread closed"
        
    def check(self, segment):
        return 0
    
    

    
def main(argv):
    udpServerThread = udpServer(int(argv[0]),argv[1], float(argv[2]))
    udpServerThread.start()
    
    
if __name__ == "__main__":
    main(sys.argv[1:])