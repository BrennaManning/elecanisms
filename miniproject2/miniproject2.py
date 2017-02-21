from time import sleep
import os
import csv
import usb.core
import numpy as np
import time


# Helper Functions
def translate(value, leftMin, leftMax, rightMin, rightMax):
    """ This helper function scales a value from one range of values to another. It is used in our python spring implementation.
    Much thanks to Adam from stackoverflow:
    http://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another/1969296 """
    
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class miniproject2:
    """ The high level class for controlling our haptic feedback device. """ 
    def __init__(self):
        """ Initialize values."""
        self.TOGGLE_LED1 = 0
        self.SET_DUTY_MOTOR_FORWARD =   1
        self.GET_DUTY_MOTOR_FORWARD =   2
        self.SET_DUTY_MOTOR_BACK =      3
        self.GET_DUTY_MOTOR_BACK =      4
        self.GET_ANGLE =                5
        self.GET_CURRENT =              6
        self.SET_BEHAVIOR =             7

        self.dev = usb.core.find(idVendor = 0x6666, idProduct = 0x0003)
        if self.dev is None:
            raise ValueError('no USB device found matching idVendor = 0x6666 and idProduct = 0x0003')
        self.dev.set_configuration()

        self.currents = [32500] * 10

    def close(self):
        """ This function disconnects from the USB device. """
        self.dev = None

    def toggle_led1(self):
        """ This function makes an LED blink on and off.
        It was used for testing and learning how to interface with the PIC. """
        try:
            self.dev.ctrl_transfer(0x40, self.TOGGLE_LED1)
        except usb.core.USBError:
            print "Could not send TOGGLE_LED1 vendor request."

    def set_duty_motor_forward(self, duty):
        """ This function takes in a duty as an input and
        sets the motor to run forward with a PWM of that duty cycle."""
        try:
            self.dev.ctrl_transfer(0x40, self.SET_DUTY_MOTOR_FORWARD, int(duty))
        except usb.core.USBError:
            print "Could not send SET_DUTY vendor request."

    def get_duty_motor_forward(self):
        """ This function returns the value of the duty cycle of the motor running forward. """
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_MOTOR_FORWARD, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_ vendor request."
        else:
            return int(ret[0])+int(ret[1])*256
        
    def set_duty_motor_back(self, duty):
        """ This function takes in a duty as an input and
        sets the motor to run backward with a PWM of that duty cycle."""
        try:
            self.dev.ctrl_transfer(0x40, self.SET_DUTY_MOTOR_BACK, int(duty))
        except usb.core.USBError:
            print "Could not send SET_DUTY_MOTOR_BACK vendor request."

    def get_duty_motor_back(self):
        """ This function returns the value of the duty cycle of the motor running backward. """
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_MOTOR_BACK, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_MOTOR_BACK vendor request."
        else:
            return int(ret[0])+int(ret[1])*256

    def get_angle(self):
        """ This function returns the angular displacement from the value of the encoder."""
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
        """ This function returns the value of the A0 pin, which is proportional to current and torque. """
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_CURRENT, 0, 0, 2)
        except usb.core.USBError:
            print "Go straight to jail, do not pass go, do not collect $200"
        else:
            current = int(ret[0])+int(ret[1])*256
            return current

    def set_behavior(self, behavior):
        try:
            self.dev.ctrl_transfer(0x40, self.SET_BEHAVIOR, int(behavior))
            print "setting behavior to ", behavior
            behaviors = {1: 'spring', 2: 'wall', 3: 'texture', 4: 'damper'}
            print "Behavior = Virtual", behaviors[behavior]
        except usb.core.USBError:
            print "You goofed it real good with the bevavhavior setting thing."
    
    def get_rolling_current(self):
        """ This function returns the rolling average of the last 10 current values. """
        self.currents.pop(0)
        self.currents.append(self.get_current())
        current = np.mean(self.currents)
        return int(current)

    def angle_calibration(self):
        """ This function can be used to create a graph of expected angle vs encoder reading. """ 
        angle_calibration = {}
        angle_calibration_data = []
        for angle in range(0, 360, 5):
            print 'Turn to ' + str(angle) + ' degrees'
            raw_input("Press Enter to continue...")
            
            print str(angle) +' degrees: ' + str(self.get_angle())
            angle_val = self.get_angle()
            

            angle_calibration_data. append({'angle': angle, 'val': angle_val})
            angle = angle + 5

           
        fp = '/home/brenna/courses/elecanisms/miniproject2/angle_calibration.csv'
        print angle_calibration_data
        keys = angle_calibration_data[0].keys()
        with open('angle_calibration.csv', 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(angle_calibration_data)
            
    def spin_down(self):
        """ This function can be used to run a spindown test and create a graph.  """
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
    
    def save_rolling_current(self):
        """ This function saves the rolling current values to a csv. """
        mp.set_duty_motor_forward(0x8000)
        current_data = []
        for i in range(0,1000):
            mp.set_duty_motor_forward(i*65)
            current_val=mp.get_rolling_current()
            current_data.append({'current': current_val})
            print i

        keys = current_data[0].keys()
        with open('current_data_sweep_rolling.csv', 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(current_data)
        print "done"
        mp.set_duty_motor_forward(0x0000)

    def virtual_spring(self):
        """ This function creates a virtual spring with duty proportional to displacement"""
        angle = self.get_angle()
        diff = abs(angle - 20000)
        
        if diff < 50:
            self.set_duty_motor_back(0x0000)
            self.set_duty_motor_forward(0x0000)

        elif angle > 20000 and angle < 22000:
            #180 degrees

            duty_forward = translate(diff, 0, 2000, 20000, 65000)
            self.set_duty_motor_back(duty_forward)
            self.set_duty_motor_forward(0x0000)
        elif angle <20000 and angle >18000:
                
            duty_back = translate(diff, 0, 2000, 20000, 65000)
            self.set_duty_motor_forward(duty_back)
            self.set_duty_motor_back(0x0000)


        else:
            self.set_duty_motor_back(0x0000)
            self.set_duty_motor_forward(0x0000)

    def virtual_spring_torque(self):
        """ This function creates a virtual spring with torque proportional to displacement"""

        angle = self.get_angle()
        target_angle = 20000
        target_torque = (angle-target_angle)*6
        measured_torque = self.get_rolling_current()
        
        duty = 0
        p = 6

        #print "angle  " + str(angle-target_angle) + '  target_torque  ' + str(target_torque) + '  measured_torque  ' + str(measured_torque)
        if abs(abs(target_torque - measured_torque) - 32000) < 100:
            print "stop"
            self.set_duty_motor_forward(0x0000)
            self.set_duty_motor_back(0x0000)

        elif -20000 < target_torque < 0:
            #self.set_duty_motor_forward

            duty = (abs(32000-target_torque-measured_torque)) or 0x0000
            # print "left " + str((duty*p))+ " \t actual " + str(self.get_duty_motor_forward())
            print('left')
            self.set_duty_motor_forward(duty*p)
            self.set_duty_motor_back(0x0000)

        elif 0 < target_torque < 20000:
           
            duty = (abs(32000-target_torque-measured_torque)) or 0x0000
            # print "right "  + str((duty*p)) + "\t actual " + str(self.get_duty_motor_back())
            print str(measured_torque)
            self.set_duty_motor_forward(0x0000)
            self.set_duty_motor_back(duty*p)
           

        else:
            print "stop"
            self.set_duty_motor_forward(0x0000)
            self.set_duty_motor_back(0x0000)

    def bumpy(self):
        """ This function creates a virtual bumpy texture."""
        #old_angle = self.get_angle()
        for bump in [18000, 20000, 22000, 24000]:
            old_angle = self.get_angle()
            sleep(.001)
            new_angle = self.get_angle() 
            if abs(old_angle-new_angle) > 1:
                if new_angle < bump < old_angle:
                    print "BOOO"
                    self.set_duty_motor_forward(0x8000)
                    self.set_duty_motor_back(0x0000)
                elif new_angle > bump > old_angle:
                    print "HOOO"
                    self.set_duty_motor_back(0x8000)
                    self.set_duty_motor_forward(0x0000)
                else:
                    self.set_duty_motor_forward(0x0000)
                    self.set_duty_motor_back(0x0000)

    def virtual_wall(self):
        """ This function creates a virtual wall. """
        pass

    def virtual_damper(self):
        """ This function creates a virtual damper. """
        pass

    def plot_angle_v_torque(self, title):
        plot_data = []
        print "plotting"
        for i in range(0, 1000):
            angle = self.get_angle()
            torque_val = self.get_rolling_current()
            plot_data.append({'angle': angle, 'torque': torque_val})
            sleep(.01)  


           
        fp = '/home/brenna/courses/elecanisms/miniproject2/' + title + '.csv'
        print plot_data
        keys = plot_data[0].keys()
        with open(title + '.csv', 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(plot_data)

    
    def plot_omega_v_torque(self, title):
        """This function saves a .csv file of torque and angular velocity over time."""
        plot_data = []
        previous_angle = 0
        print "plotting"
        for i in range(0, 100):
            angle = self.get_angle()
            omega = angle - previous_angle
            torque_val = self.get_rolling_current()
            plot_data.append({'omega': omega, 'torque': torque_val})
            sleep(.1)  
            previous_angle = angle

           
        fp = '/home/brenna/courses/elecanisms/miniproject2/' + title + '.csv'
        print plot_data
        keys = plot_data[0].keys()
        with open(title + '.csv', 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(plot_data)


if __name__ == "__main__":

    DISKO = miniproject2()
    