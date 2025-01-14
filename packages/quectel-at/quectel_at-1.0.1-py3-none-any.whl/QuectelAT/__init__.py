import serial
from serial import Serial
import serial.tools.list_ports
from time import sleep

class RM520N_GL:

    def __init__(self, **kwargs):

        if "baud" not in kwargs:
            kwargs["baud"] = 115200

        self.at_port_name = "Quectel USB AT Port"
        self.nvme_port_name = "Quectel USB NMEA Port"
        self.dm_port_name = "Quectel USB DM Port"

        com_ports = self._list_ports()
        
        self.at_ser = Serial(com_ports[self.at_port_name], kwargs["baud"])
        self.at_ser.read_all()

        """self.nvme_ser = Serial(com_ports[self.nvme_port_name], kwargs["baud"])
        self.nvme_ser.read_all()
        
        self.dm_ser = Serial(com_ports[self.dm_port_name], kwargs["baud"])
        self.dm_ser.read_all()"""

        self.smsCanRead = True

    def _list_ports(self):
        com_ports = {}
        for i in serial.tools.list_ports.comports():
            com_ports[i[1].split("(")[0].strip()] = i[0]
        return com_ports

    def _isFloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def checkStatus(self):
        self.smsCanRead = False
        self.at_ser.read_all()
        self.at_ser.write(b"AT\r\n")
        sleep(0.05)
        required_value = b"AT\r\r\nOK\r\n"
        value = self.at_ser.read_all()
        self.smsCanRead = True
        status = value == required_value
        return status

    def restartModule(self):
        self.at_ser.read_all()
        self.at_ser.write(b"AT+CFUN=1,1\r\n")
        sleep(0.05)
        ret_val = self.at_ser.read_all()
        ret_val = self.at_ser.read_all()
        while len(ret_val) == 0:
            if self.at_port_name in self._list_ports():
                try:
                    ret_val = self.at_ser.read_all()
                except serial.serialutil.SerialException:
                    continue
        status = ret_val.decode()
        status = " ".join(status.split("\r\n")[3].split(" ")[1:])
        self.smsCanRead = True
        return status

    def getSignalStrengh(self):
        self.at_ser.read_all()
        self.at_ser.write(b"AT+CSQ\r\n")
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        signal = ret_val.split("\r\n")[1]
        signal_strenght = {}
        if signal.split(" ")[0] == "+CSQ:":
            values = signal.split(" ")[1].split(",")
            signal_strenght["rssi"] = values[0]
            signal_strenght["ber"] = values[1]
        return signal_strenght

    def checkSIMState(self):
        self.at_ser.read_all()
        self.at_ser.write(b"AT+CPIN?\r\n")
        sleep(0.05)
        ret_val = self.at_ser.read_all()
        #print(ret_val)
        ret_val = ret_val.decode().split("\n")[1]
        if " ".join(ret_val.split(" ")[:-1]) == "+CME ERROR:":
            return "NOT INSERTED"
        ret_val = " ".join(ret_val.split(" ")[1:]).strip()
        self.smsCanRead = True
        return ret_val

    def enterSIMPin(self, pin, puk = None):

        self.at_ser.read_all()

        if puk is None:
            self.at_ser.write(f'AT+CPIN="{pin}"\r\n'.encode())
        else:
            self.at_ser.write(f'AT+CPIN="{puk}","{pin}"\r\n'.encode())

        sleep(0.5)

        ret_val = self.at_ser.read_all().decode()

        #print(ret_val)

        sim_status = ""

        if len(pin) != 4 and (puk is not None and len(puk) != 8):
            sim_status = "WRONG PIN AND PUK LENGTH"
        elif len(pin) != 4:
            sim_status = "WRONG PIN LENGTH"
        elif puk is not None and len(puk) != 8:
            sim_status = "WRONG PUK LENGTH"

        else:

            if self.checkSIMState() == "READY":
                sim_status = "READY"

            else:

                if len(ret_val.split("\r\n")) == 7:
                    sim_status = ret_val.split("\r\n")[3].split(" ")[1]

                elif len(ret_val.split("\r\n")) == 3:
                    ret_val_cme = " ".join(ret_val.split("\r\n")[1].split(" ")[:-1])
                    if ret_val_cme == "+CME ERROR:":
                        ret_val_cme_num = int(ret_val.split("\r\n")[1].split(" ")[-1])
                        if ret_val_cme_num == 16:
                            sim_status = "SIM PIN"
                        elif ret_val_cme_num == 10:
                            sim_status = "NOT INSERTED"
                        elif ret_val_cme_num == 18:
                            sim_status = "READY"
                    elif ret_val.split("\r\n")[1] == "ERROR":
                        sim_status = "SIM PUK"

                elif len(ret_val.split("\r\n")) == 5:
                    sim_status = ret_val.split("\r\n")[3].split(" ")[1]

        self.smsCanRead = True

        return sim_status

    def disableSIMPin(self, pin):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CLCK="SC",0,"{pin}"\r\n'.encode())
        sleep(0.5)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        status = ""
        if len(pin) != 4:
            status = "WRONG PIN"
        else:
            if ret_val.split("\r\n")[1] == "OK":
                status = "OK"
            elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 13:
                status = "PIN ALREADY ENTERED"
            elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 16:
                if self.checkSIMState() == "SIM PIN":
                    status = "SIM PIN"
                else:
                    status = "WRONG PIN"
            elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 12:
                status = "SIM PUK"
        self.smsCanRead = True
        return status

    def enableSIMPin(self, pin):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CLCK="SC",1,"{pin}"\r\n'.encode())
        sleep(0.5)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        status = ""
        if len(pin) != 4:
            status = "WRONG PIN"
        else:
            if ret_val.split("\r\n")[1] == "OK":
                status = "OK"
            elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 13:
                status = "PIN ALREADY ENTERED"
            elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 16:
                status = "WRONG PIN"
        self.smsCanRead = True
        return status

    def defineNewSIMPin(self, old_pin, new_pin):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CPWD="SC","{old_pin}","{new_pin}"\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        if len(old_pin) != 4 and en(new_pin) != 4:
            status = "WRONG OLD AND NEW PIN LENGTH"
        elif len(old_pin) != 4:
            status = "WRONG OLD PIN LENGTH"
        elif len(new_pin) != 4:
            status = "WRONG NEW PIN LENGTH"
        else:
            if ret_val.split("\r\n")[1] == "OK":
                status = "OK"
            elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 16:
                status = "WRONG PIN"
            elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 13:
                status = "SIM PIN DISABLED"
        self.smsCanRead = True
        return status

    def setGNSSOn(self):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+QGPS=1\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        if ret_val.split("\r\n")[1] == "OK":
            status = "OK"
        elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 504:
            status = "GNSS ALREADY OPEN"
        self.smsCanRead = True
        return status

    def setGNSSOff(self):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+QGPSEND\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        if ret_val.split("\r\n")[1] == "OK":
            status = "OK"
        elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 505:
            status = "GNSS ALREADY CLOSED"
        self.smsCanRead = True
        return status

    def isGNSSActive(self):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+QGPS?\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        status = bool(int(ret_val.split("\r\n")[1].split(" ")[1]))
        self.smsCanRead = True
        return ret_val_answer

    def getGNSSData(self):
        
        self.at_ser.read_all()
        self.at_ser.write(f'AT+QGPSLOC=2\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        
        ret_val_cme = " ".join(ret_val.split("\r\n")[1].split(" ")[:-1])

        status = ""
        
        if ret_val_cme == "+CME ERROR:":
            if int(ret_val.split("\r\n")[1].split(" ")[-1]) == 505:
                status = "GNSS CLOSED"
            elif int(ret_val.split("\r\n")[1].split(" ")[-1]) == 516:
                status = "GNSS CANNOT READ"
                
        else:
            vals = ret_val.split("\r\n")[1].split(" ")[1].split(",")
            val_names = [
                "time",
                "latitude",
                "longitude",
                "hdop",
                "altitude",
                "fix",
                "direction",
                "speedkm",
                "speedknot",
                "date",
                "satellites"
            ]
            
            data_vals = {}
            
            for i in range(len(vals)):
                data_vals[val_names[i]] = vals[i]

            data_vals["latitude"] = float(data_vals["latitude"]) if self._isFloat(data_vals["latitude"]) else data_vals["latitude"]
            data_vals["longitude"] = float(data_vals["longitude"]) if self._isFloat(data_vals["longitude"]) else data_vals["longitude"]
            data_vals["hdop"] = float(data_vals["hdop"]) if self._isFloat(data_vals["hdop"]) else data_vals["hdop"]
            data_vals["altitude"] = float(data_vals["altitude"]) if self._isFloat(data_vals["altitude"]) else data_vals["altitude"]
            data_vals["fix"] = int(data_vals["fix"]) if data_vals["fix"].isnumeric() else data_vals["fix"]
            data_vals["direction"] = float(data_vals["direction"]) if self._isFloat(data_vals["direction"]) else data_vals["direction"]
            data_vals["speedkm"] = float(data_vals["speedkm"]) if self._isFloat(data_vals["speedkm"]) else data_vals["speedkm"]
            data_vals["speedknot"] = float(data_vals["speedknot"]) if self._isFloat(data_vals["speedknot"]) else data_vals["speedknot"]
            data_vals["satellites"] = int(data_vals["satellites"]) if data_vals["satellites"].isnumeric() else data_vals["satellites"]
            
            data_vals["lat"] = data_vals["latitude"]
            data_vals["lng"] = data_vals["longitude"]
            data_vals["alt"] = data_vals["altitude"]
            data_vals["sat"] = data_vals["satellites"]
            data_vals["dic"] = data_vals["direction"]
            data_vals["km"] = data_vals["speedkm"]
            data_vals["knot"] = data_vals["speedknot"]

            data_vals["hour"] = int(data_vals["time"][0:2])
            data_vals["minute"] = int(data_vals["time"][2:4])
            data_vals["second"] = int(data_vals["time"][4:6])
            
            data_vals["day"] = int(data_vals["date"][0:2])
            data_vals["month"] = int(data_vals["date"][2:4])
            data_vals["year"] = 2000 + int(data_vals["date"][4:6])
            
            status = data_vals

        self.smsCanRead = True
            
        return status

    def enableSMS(self):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CMGF=1\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        self.smsCanRead = True
        status = ret_val.split("\r\n")[1] == "OK"
        return status

    def disableSMS(self):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CMGF=0\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        self.smsCanRead = True
        status = ret_val.split("\r\n")[1] == "OK"
        return status

    def isSMSActive(self):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CMGF?\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        self.smsCanRead = True
        status = bool(int(ret_val.split("\r\n")[1].split(" ")[1]))
        return status

    def sendSMS(self, phone_number, message):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CMGS="{phone_number}"\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        status = False
        if ret_val.split("\r\n")[1] == "> ":
            self.at_ser.write(f'{message}\x1A'.encode())
            sleep(1)
            ret_val = self.at_ser.read_all().decode()
            #print(ret_val.split("\r\n"))
            if ret_val.split("\r\n")[3] == "OK":
                status = True
        self.smsCanRead = True
        return status

    def removeAllSMS(self):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CMGD=0,4\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        status = ret_val.split("\r\n")[1] == "OK"
        return status

    def removeCustomSMS(self, sms_num):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CMGD={sms_num},0\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        status = ret_val.split("\r\n")[1] == "OK"
        return status

    def getAllSMS(self):
        
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CMGL="ALL"\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        
        ret_list = []
        
        if ret_val.split("\r\n")[1] == "OK":
            all_messages = {}

        elif ret_val.split("\r\n")[1] == "ERROR":
            ret_list = "SMS IS CLOSED"
            
        else:
            
            all_messages = ret_val.split("\r\n")[1:-3:2]
            
            order = 0
            
            for  i in all_messages:
                
                msg = " ".join(i.split(" ")[1:])
                msg = msg.split(",")
                
                msg_num = int(msg[0])
                
                ret_list.append({})
                ret_list[order]["msg_num"] = msg_num
                ret_list[order]["msg_status"] = msg[1][1:-1]
                ret_list[order]["phone_number"] = msg[2][1:-1]
                ret_list[order]["date"] = msg[4][1:]
                ret_list[order]["time"] = msg[5][:-4]
                
                order += 1
                
            all_messages = ret_val.split("\r\n")[2:-3:2]

            order = 0
            
            for i in all_messages:
                ret_list[order]["message"] = i
                order += 1
                    
        return ret_list

    def getCustomSMS(self, sms_num):
        self.at_ser.read_all()
        self.at_ser.write(f'AT+CMGR={sms_num}\r\n'.encode())
        sleep(0.05)
        ret_val = self.at_ser.read_all().decode()
        #print(ret_val)
        sms_val = {}
        ret_val_cme = " ".join(ret_val.split("\r\n")[1].split(" ")[:-1])
        if not self.isSMSActive():
            sms_val = "SMS IS CLOSED"
        elif ret_val_cme == "+CMS ERROR:":
            if int(ret_val.split("\r\n")[1].split(" ")[-1]) == 321:
                sms_val = "NO SMS DETECTED"
        else:
            message = ret_val.split("\r\n")[1]
            msg = " ".join(message.split(" ")[1:])
            msg = msg.split(",")
            sms_val["msg_status"] = msg[0][1:-1]
            sms_val["phone_number"] = msg[1][1:-1]
            sms_val["date"] = msg[3][1:]
            sms_val["time"] = msg[4][:-4]
            message = ret_val.split("\r\n")[2]
            sms_val["message"] = message
        return sms_val

if __name__ == "__main__":

    AT_PORT = "COM11"
    NVME_PORT = "COM10"
    DM_PORT = "COM8"

    BAUD = 115200

    lte_module = RM520N_GL(baud = BAUD)

    print("Connected")
