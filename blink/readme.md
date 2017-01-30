# Elecanisms Mini Project 00 How to run “Blink” on PIC24

### SETUP

### Install the MPLAB compiler and the SCons software construction tool
Follow all steps [here.](http://elecanisms.olin.edu/handouts/1.1_BuildTools.pdf)

### Install and Configure Git
Fork Elecanisms Repo
Clone Elecanisms Repo

Follow steps [here](http://elecanisms.olin.edu/handouts/1.2_Getting_Started_w_Git.pdf) to get setup with git. 


### Bootloader 
Follow steps in README file in the “bootloader” folder of the elecanisms github. 
[Link here.] (https://github.com/OlinElecanisms/elecanisms/tree/master/bootloader)

### Once you are all set up

In the terminal, navigate to elecanisms/bootloader/software

Type python bootloadergui.py

Connect USB to computer

Click Connect
If PIC24 doesn’t connect, reboot the board by pressing on the red and black buttons together (located near the microusb port) and roll off onto the black button. This should automatically connect the PIC24 to the bootloader GUI.

Import hex file from the “blink” folder

Click Write

Your LED should be blinking on the PIC24 Board. If the LED on the board is not blinking, press the red button (located near the microusb port).

### Changing the Blinking Behavior

Open blink.c from the blink directory using a text editor. Change the code here. For example, you might change led1 to led2 to make a different led blink, or you could add <code>led_on(&led2)</code> beneath <code>led_on(&led1)</code> and  <code>led_toggle(&led2)</code> beneath  <code>led_toggle(&led1)</code>, and then comment out the <code>led_write(&led2, !sw_read(&sw2))</code> line near the bottom. This will make two lights blink together.

After you have modified blink.c, save this file and repeat the previous steps to connect and write to the board. 

