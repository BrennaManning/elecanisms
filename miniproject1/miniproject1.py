from time import sleep
import os
import csv
import usb.core

import time
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
            angle_val = int(ret[0])+int(ret[1])*256
            if angle_val <13000:
                angle_val += 16398
            return angle_val

    def get_current(self):
        print "hooray"
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_CURRENT, 0, 0, 2)
        except:
            usb.core.USBError:
            print "Go straight to jail, do not pass go, do not collect $200"
        else:
            current = int(ret[0])+int(ret[1])*256
            return current

    def angle_calibration(self):
        angle_calibration = {}
        angle_calibration_data = []
        #angle_list = [0, 5, 10, 15, 20, 25, 30, 35, 45, 50,  55, 60, 65, 70, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360]
        for angle in range(0, 360, 5):
            print 'Turn to ' + str(angle) + ' degrees'
            raw_input("Press Enter to continue...")
            
            print str(angle) +' degrees: ' + str(self.get_angle())
            angle_val = self.get_angle()
            

            angle_calibration_data. append({'angle': angle, 'val': angle_val})
            angle = angle + 5

           
        fp = '/home/brenna/courses/elecanisms/miniproject1/angle_calibration.csv'
        print angle_calibration_data
        keys = angle_calibration_data[0].keys()
        with open('angle_calibration.csv', 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(angle_calibration_data)
            
    def spin_down(self):
        self.set_duty_motor_forward(0xffff)
        sleep(5)
        self.set_duty_motor_forward(0x0000)
        angle_spindown_data = []
        angle_val = 0
        previous_angle_val = 0
        start_time = time.time()
        rotation_data = []
        last_time = start_time
        num_rotations = 0
        previous_diff = 0
        for i in range(0, 500):
            angle_val = self.get_angle()
            angle_val_original = angle_val
            if angle_val - previous_angle_val > 100:
                i = i + 1
                num_rotations += 1
                print 'num rotations =' + str(num_rotations)
                print 'angle val: ' + str(angle_val) + 'previous angle: ' + str(previous_angle_val)
            #angle_val = angle_val + (num_rotations* 8200)
            diff = angle_val - previous_angle_val
            if diff > 8000:
                diff = previous_diff
            previous_diff = diff
            diff = -1 * diff
            now = time.time()
            time_since_start = now - start_time
            angle_spindown_data.append({'angle': angle_val, 'diff': diff, 'time': time_since_start})
            #print angl5e_val
            sleep(.01)
            previous_angle_val = angle_val_original
           
            i = i +1

        keys = angle_spindown_data[0].keys()
        with open('angle_spindown.csv', 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(angle_spindown_data)

if __name__ == "__main__":

    mp = miniproject1()
    mp.get_current()
    print "hello"
  