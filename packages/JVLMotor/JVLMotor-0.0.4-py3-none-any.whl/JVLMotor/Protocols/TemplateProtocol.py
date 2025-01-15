from JVLMotor.Motors.MACMotor import *
from JVLMotor.Motors.MISMotor import *

import subprocess
class TemplateProtocol:
    def __init__(self,motor="MAC"):
        if motor == "MAC":
            self.motor = MACMotor()
        elif motor == "MIS":
            self.motor = MISMotor()

        # Default ip
        self.ip = "192.168.0.49"

    def write(self,reg_num,data,length=4,no_response=False):
        pass

    def read(self,reg_num,length=4):
        pass

    def writeModule(self,reg_num,data,length=4,no_response=False):
        pass

    def readModule(self,reg_num,length=4):
        pass

    def readSBUF(self):
        pass

    def computeComplement(self,byte):
        return ~byte & 0xFF