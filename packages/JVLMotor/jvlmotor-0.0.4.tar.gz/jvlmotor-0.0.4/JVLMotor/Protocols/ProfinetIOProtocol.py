from .TemplateProtocol import *
from .Communications.Drivers.CifXDriver import *
from .MacTalkProtocol import *

import socket
import struct
import time

CIFX_NUM = 0
CIFX_CH_NUM = 0

PNM_AP_CMD_READ_RECORD_SUBM_REQ = 0x9422
PNM_AP_CMD_WRITE_RECORD_SUBM_REQ = 0x9424

STATION_NAME_REG_START = 71

READ_IO_NUM = 25
READ_ACYCLIC_NUM = 10

PNM_MODULE_COMMAND_INDEX = 0x10
PNM_MODULE_REGISTERS_INDEX = 0x11
PNM_MOTOR_REGISTERS_INDEX = 0x12

#Name of the station is defined in the registers 71 to 130 

class ProfinetIOProtocol(TemplateProtocol):
    def __init__(self,motor,ip,port="XXX",update=False):
        super().__init__(motor=motor)
        if update: 
            firmware_path = r"\MotorInterface\Protocols\Communications\Drivers\Firmwares\PNM"
            current_dir = os.getcwd()
            if os.path.basename(current_dir) == "MotorInterface":
                firmware_path = firmware_path.replace(r"\MotorInterface", "")
            if motor == "MAC":
                firmware_path += r"\MAC\cifxpnm.nxf"
                station_name = "macmotor"
                self.ip = "192.168.0.49"
            elif motor == "MIS":
                firmware_path += r"\MIS\cifxpnm.nxf"
                station_name = "mismotor"
                self.ip = "192.168.0.50"
            update_firmware_path = "./MotorInterface/Protocols/Communications/Drivers/Firmwares/PNM/updatePNMFirmware.py"
            if os.path.basename(current_dir) == "MotorInterface":
                update_firmware_path = firmware_path.replace(r"/MotorInterface", "")
            subprocess.run(["python",
                            update_firmware_path,
                            "--firmware_path",firmware_path],
                            check=True)
            time.sleep(8)
            self.port = port
            self.setup(station_name)

        self.driver = CifXDriver()

        self.channel, err = self.driver.openChannel(CIFX_NUM,CIFX_CH_NUM)
        self.driver.setHostStateChannel(self.channel)
        if (err != CIFX_NO_ERROR):
            print("Open channel error: ", self.driver.getErrorDescriptionDriver(err))
        self.driver.onBusStateChannel(self.channel)
        
        # Setup IOCS and IOPS flags
        header_flags = 0x80808080
        header_flags = header_flags.to_bytes(4,byteorder='big')
        err = self.driver.writeIOChannel(self.channel,0,0,header_flags,4)
        if (err != CIFX_NO_ERROR):
            print("Error I/O header flags: ", self.driver.getErrorDescriptionDriver(err))

        footer_flags = 0x8080
        footer_flags = footer_flags.to_bytes(2,byteorder='big')
        self.driver.writeIOChannel(self.channel,0,5+32,footer_flags,2)
        if (err != CIFX_NO_ERROR):
            print("Error I/O footer flags: ", self.driver.getErrorDescriptionDriver(err))

        #Iniatilize I/O read
        err = self.read(self.motor.io_read_words[0])
        if (err != CIFX_NO_ERROR):
            print("I/O read no set yet", self.driver.getErrorDescriptionDriver(err))

    def __del__(self):
        self.close()

    def updateFirmare(self,firmware_file):
        self.driver.openSysDevice(CIFX_NUM)
        self.driver.downloadFirmwareSysDevice(CIFX_CH_NUM,firmware_file)
        self.driver.closeSysDevice()
        
    def ipTouint32(self):
        packed_ip = socket.inet_aton(self.ip)
        return struct.unpack("!I", packed_ip)[0]
    
    def readIO(self,reg_num,length=4):
        for i in range(READ_IO_NUM):
            offset = self.motor.io_read_words.index(reg_num)*4 + 4
            value,err = self.driver.readIOChannel(self.channel,0,offset,length)
            if (err != CIFX_NO_ERROR):
                print("Error I/O reading:", self.driver.getErrorDescriptionDriver(err))
                return
        return int.from_bytes(value,byteorder='big',signed=True)

    def writeIO(self,reg_num,data,length=4):
        offset = self.motor.io_write_words.index(reg_num)*4 + 5
        bytes_data = data.to_bytes(length,byteorder='big')
        err = self.driver.writeIOChannel(self.channel,0,offset,bytes_data,length)
        if (err != CIFX_NO_ERROR):
            print("Error I/O writing:", self.driver.getErrorDescriptionDriver(err))
            return
        return CIFX_NO_ERROR

    
    def readAcyclic(self,reg_num,length=4):
        packet = CIFX_PACKET()
        packet.tHeader.ulDest = 0x20
        packet.tHeader.ulLen = 8
        packet.tHeader.ulState = 0
        packet.tHeader.ulCmd = PNM_AP_CMD_READ_RECORD_SUBM_REQ

        usSubmoduleHandle = 2
        usIndex = (PNM_MOTOR_REGISTERS_INDEX << 8) | reg_num
        ulMaxReadLen = 4

        packet.abData[0:2] = usSubmoduleHandle.to_bytes(2,byteorder='little')
        packet.abData[2:4] = usIndex.to_bytes(2,byteorder='little')
        packet.abData[4:8] = ulMaxReadLen.to_bytes(4,byteorder='little')

        for i in range(READ_ACYCLIC_NUM):
            err = self.driver.putPacketChannel(self.channel,packet,PACKET_WAIT_TIMEOUT)
            if err != CIFX_NO_ERROR:
                print("Read error: ", self.driver.getErrorDescriptionDriver(err))
                return

            rcv_packet, err = self.driver.getPacketChannel(self.channel, PACKET_WAIT_TIMEOUT)
            if err != CIFX_NO_ERROR:
                print("Read error: ", self.driver.getErrorDescriptionDriver(err))
                return

            status = rcv_packet.tHeader.ulState
            if (status != CIFX_NO_ERROR):
                print("Read Status: ", hex(status))
                print("Profinet error code: ", int.from_bytes(rcv_packet.abData[8:12],byteorder='big'))
                print("Profinet add value 1: ", int.from_bytes(rcv_packet.abData[12:14],byteorder='big'))
                print("Profinet add value 2: ", int.from_bytes(rcv_packet.abData[14:16],byteorder='big'))
                return
            
        data = rcv_packet.abData[16:16+length]
        value = int.from_bytes(data,byteorder='big',signed=False)
        return value

    def writeAcyclic(self,reg_num,data,length=4,no_response=False):
        packet = CIFX_PACKET()
        packet.tHeader.ulDest = 0x20
        packet.tHeader.ulLen = 8 + length
        packet.tHeader.ulState = 0
        packet.tHeader.ulCmd = PNM_AP_CMD_WRITE_RECORD_SUBM_REQ

        usSubmoduleHandle = 1
        usIndex = (PNM_MOTOR_REGISTERS_INDEX << 8) | reg_num
        ulDataLen = length
        abRecordData = data.to_bytes(length,byteorder='big')

        packet.abData[0:2] = usSubmoduleHandle.to_bytes(2,byteorder='little')
        packet.abData[2:4] = usIndex.to_bytes(2,byteorder='little')
        packet.abData[4:8] = ulDataLen.to_bytes(4,byteorder='little')
        packet.abData[8:8+length] = abRecordData

        err = self.driver.putPacketChannel(self.channel,packet,PACKET_WAIT_TIMEOUT)
        if err != CIFX_NO_ERROR:
            print("Read error: ", self.driver.getErrorDescriptionDriver(err))
            return

        rcv_packet, err = self.driver.getPacketChannel(self.channel, PACKET_WAIT_TIMEOUT)
        if err != CIFX_NO_ERROR:
            print("Read error: ", self.driver.getErrorDescriptionDriver(err))
            return

        status = rcv_packet.tHeader.ulState
        if (status != CIFX_NO_ERROR):
            print("Write Status: ", hex(status))
            print("Profinet error code: ", int.from_bytes(rcv_packet.abData[4:8],byteorder='big'))
            print("Profinet add value 1: ", int.from_bytes(rcv_packet.abData[8:10],byteorder='big'))
            print("Profinet add value 2: ", int.from_bytes(rcv_packet.abData[10:12],byteorder='big'))
            return
        
        return CIFX_NO_ERROR

    def read(self,reg_num,length=4):
        if reg_num in self.motor.io_read_words:
            return  self.readIO(reg_num,length)
        else:
            return self.readAcyclic(reg_num,length)
        
    def write(self,reg_num,data,length=4,no_response=False):
        if reg_num in self.motor.io_write_words:
            return self.writeIO(reg_num,data,length)
        else:
            return self.writeAcyclic(reg_num,data,length,no_response=no_response)
        
    def readModule(self,reg_num,length=4):
        packet = CIFX_PACKET()
        packet.tHeader.ulDest = 0x20
        packet.tHeader.ulLen = 8
        packet.tHeader.ulState = 0
        packet.tHeader.ulCmd = PNM_AP_CMD_READ_RECORD_SUBM_REQ

        usSubmoduleHandle = 2
        usIndex = (PNM_MODULE_REGISTERS_INDEX << 8) | reg_num
        ulMaxReadLen = 4

        packet.abData[0:2] = usSubmoduleHandle.to_bytes(2,byteorder='little')
        packet.abData[2:4] = usIndex.to_bytes(2,byteorder='little')
        packet.abData[4:8] = ulMaxReadLen.to_bytes(4,byteorder='little')

        err = self.driver.putPacketChannel(self.channel,packet,PACKET_WAIT_TIMEOUT)
        if err != CIFX_NO_ERROR:
            print("Read error: ", self.driver.getErrorDescriptionDriver(err))
            return

        rcv_packet, err = self.driver.getPacketChannel(self.channel, PACKET_WAIT_TIMEOUT)
        if err != CIFX_NO_ERROR:
            print("Read error: ", self.driver.getErrorDescriptionDriver(err))
            return

        status = rcv_packet.tHeader.ulState
        if (status != CIFX_NO_ERROR):
            print("Read Status: ", hex(status))
            print("Profinet error code: ", int.from_bytes(rcv_packet.abData[8:12],byteorder='big'))
            print("Profinet add value 1: ", int.from_bytes(rcv_packet.abData[12:14],byteorder='big'))
            print("Profinet add value 2: ", int.from_bytes(rcv_packet.abData[14:16],byteorder='big'))
            return 
        
        data = rcv_packet.abData[16:16+length]
        value = int.from_bytes(data,byteorder='big',signed=False)
        return value
    
    def writeModule(self,reg_num,data,length=4,no_response=False):
        packet = CIFX_PACKET()
        packet.tHeader.ulDest = 0x20
        packet.tHeader.ulLen = 8 + length
        packet.tHeader.ulState = 0
        packet.tHeader.ulCmd = PNM_AP_CMD_WRITE_RECORD_SUBM_REQ

        usSubmoduleHandle = 1
        usIndex = (PNM_MODULE_REGISTERS_INDEX << 8) | reg_num
        ulDataLen = length
        abRecordData = data.to_bytes(length,byteorder='big')

        packet.abData[0:2] = usSubmoduleHandle.to_bytes(2,byteorder='little')
        packet.abData[2:4] = usIndex.to_bytes(2,byteorder='little')
        packet.abData[4:8] = ulDataLen.to_bytes(4,byteorder='little')
        packet.abData[8:8+length] = abRecordData

        err = self.driver.putPacketChannel(self.channel,packet,PACKET_WAIT_TIMEOUT)
        if err != CIFX_NO_ERROR:
            print("Read error: ", self.driver.getErrorDescriptionDriver(err))
            return

        rcv_packet, err = self.driver.getPacketChannel(self.channel, PACKET_WAIT_TIMEOUT)
        if err != CIFX_NO_ERROR:
            print("Read error: ", self.driver.getErrorDescriptionDriver(err))
            return

        status = rcv_packet.tHeader.ulState
        if (status != CIFX_NO_ERROR):
            print("Write Status: ", hex(status))
            print("Profinet error code: ", int.from_bytes(rcv_packet.abData[4:8],byteorder='big'))
            print("Profinet add value 1: ", int.from_bytes(rcv_packet.abData[8:10],byteorder='big'))
            print("Profinet add value 2: ", int.from_bytes(rcv_packet.abData[10:12],byteorder='big'))
            return
        
        return CIFX_NO_ERROR
    
    def writeModuleCommand(self,data,length=4,no_response=False):
        packet = CIFX_PACKET()
        packet.tHeader.ulDest = 0x20
        packet.tHeader.ulLen = 8 + length
        packet.tHeader.ulState = 0
        packet.tHeader.ulCmd = PNM_AP_CMD_WRITE_RECORD_SUBM_REQ

        usSubmoduleHandle = 1
        usIndex = (PNM_MODULE_COMMAND_INDEX << 8) | 0
        ulDataLen = length
        abRecordData = data.to_bytes(length,byteorder='big')

        packet.abData[0:2] = usSubmoduleHandle.to_bytes(2,byteorder='little')
        packet.abData[2:4] = usIndex.to_bytes(2,byteorder='little')
        packet.abData[4:8] = ulDataLen.to_bytes(4,byteorder='little')
        packet.abData[8:8+length] = abRecordData

        err = self.driver.putPacketChannel(self.channel,packet,PACKET_WAIT_TIMEOUT)
        if err != CIFX_NO_ERROR:
            print("Read error: ", self.driver.getErrorDescriptionDriver(err))
            return

        rcv_packet, err = self.driver.getPacketChannel(self.channel, PACKET_WAIT_TIMEOUT)
        if err != CIFX_NO_ERROR:
            print("Read error: ", self.driver.getErrorDescriptionDriver(err))
            return

        status = rcv_packet.tHeader.ulState
        if (status != CIFX_NO_ERROR):
            print("Write Status: ", hex(status))
            print("Profinet error code: ", int.from_bytes(rcv_packet.abData[4:8],byteorder='big'))
            print("Profinet add value 1: ", int.from_bytes(rcv_packet.abData[8:10],byteorder='big'))
            print("Profinet add value 2: ", int.from_bytes(rcv_packet.abData[10:12],byteorder='big'))
            return
        
        return CIFX_NO_ERROR

    def setIP(self,motor):
        mt = MacTalkProtocol(port=self.port, motor=motor)
        mt.writeModule(self.motor.module_registers["ip"],self.ipTouint32())
        mt.writeModule(self.motor.module_registers["command"],
                       self.motor.module_cmd_register["save2flash"])
        mt.writeModule(self.motor.module_registers["command"],
                       self.motor.module_cmd_register["reset"])
        time.sleep(8)

    def unsetBlankName(self):
        mt = MacTalkProtocol(port=self.port)
        setup_bits = mt.readModule(self.motor.module_registers["setup_bits"])
        setup_bits &= ~(1 << self.motor.module_setup_bits["clear_station_name"])
        mt.writeModule(self.motor.module_registers["setup_bits"],setup_bits)
        mt.writeModule(self.motor.module_registers["command"],
                       self.motor.module_cmd_register["save2flash"])
        mt.writeModule(self.motor.module_registers["command"],
                       self.motor.module_cmd_register["reset"])
        time.sleep(8)

    def setStationName(self,name):
        mt = MacTalkProtocol(port=self.port)
        station_name_reg = STATION_NAME_REG_START
        for c in name:
            mt.writeModule(station_name_reg,int(c))
            station_name_reg += 1
        mt.writeModule(self.motor.module_registers["command"],
                       self.motor.module_cmd_register["save2flash"])
        mt.writeModule(self.motor.module_registers["command"],
                       self.motor.module_cmd_register["reset"])
        time.sleep(8)

    def setup(self,name):
        mt = MacTalkProtocol(port=self.port)
        mt.writeModule(self.motor.module_registers["ip"],self.ipTouint32())
        setup_bits = mt.readModule(self.motor.module_registers["setup_bits"])
        setup_bits &= ~(1 << self.motor.module_setup_bits["clear_station_name"])
        mt.writeModule(self.motor.module_registers["setup_bits"],setup_bits)
        station_name_reg = STATION_NAME_REG_START
        for i in range(0,len(name),4):
            chunk = name[i:i+4]
            chunk = chunk.ljust(4, '\0')
            value = 0
            for j, c in enumerate(chunk):
                value |= (ord(c) << (8 * j)) 
            mt.writeModule(station_name_reg,value)
            station_name_reg += 1
        
        mt.writeModule(station_name_reg,0)
        mt.writeModule(self.motor.module_registers["command"],
                       self.motor.module_cmd_register["save2flash"])
        mt.writeModule(self.motor.module_registers["command"],
                       self.motor.module_cmd_register["reset"])
        time.sleep(8)

    def close(self):
        self.driver.closeChannel(self.channel)
        self.driver.closeDriver()