from time import sleep
import usb.core

class miniproject1:

    def __init__(self):
        self.TOGGLE_LED1 = 0
        self.SET_DUTY_MOTOR_FORWARD =   1
        self.GET_DUTY_MOTOR_FORWARD =   2
        self.SET_DUTY_MOTOR_BACK =      3
        self.GET_DUTY_MOTOR_BACK =      4
        self.GET_ANGLE =                5

        self.dev = usb.core.find(idVendor = 0x6666, idProduct = 0x0003)
        if self.dev is None:
            raise ValueError('no USB device found matching idVendor = 0x6666 and idProduct = 0x0003')
        self.dev.set_configuration()



    def close(self):
        self.dev = None

    def toggle_led1(self):
        try:
            self.dev.ctrl_transfer(0x40, self.TOGGLE_LED1)
        except usb.core.USBError:
            print "Could not send TOGGLE_LED1 vendor request."

    def set_duty_motor_forward(self, duty):
        try:
            self.dev.ctrl_transfer(0x40, self.SET_DUTY_MOTOR_FORWARD, int(duty))
        except usb.core.USBError:
            print "Could not send SET_DUTY vendor request."

    def get_duty_motor_forward(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_MOTOR_FORWARD, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_ vendor request."
        else:
            return int(ret[0])+int(ret[1])*256
        
    def set_duty_motor_back(self, duty):
        try:
            self.dev.ctrl_transfer(0x40, self.SET_DUTY_MOTOR_BACK, int(duty))
        except usb.core.USBError:
            print "Could not send SET_DUTY_MOTOR_BACK vendor request."

    def get_duty_motor_back(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_MOTOR_BACK, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_MOTOR_BACK vendor request."
        else:
            return int(ret[0])+int(ret[1])*256

    def get_angle(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_ANGLE, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_ANGLE vendor request."
        else:
            return int(ret[0])+int(ret[1])*256


if __name__ == "__main__":
   mp = miniproject1()
   mp.get_angle()
   mp.set_duty_motor_forward(0x8000)
   for i in range(0, 100):
        print mp.get_angle()
        sleep(.5)
        i = i +1