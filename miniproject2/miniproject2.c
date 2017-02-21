#include <p24FJ128GB206.h>
#include "config.h"
#include "common.h"
#include "usb.h"
#include "pin.h"
#include "ui.h"
#include "timer.h"
#include "oc.h"
#include "spi.h"


#define TOGGLE_LED1                  0
#define SET_DUTY_MOTOR_FORWARD       1
#define GET_DUTY_MOTOR_FORWARD       2
#define SET_DUTY_MOTOR_BACK          3
#define GET_DUTY_MOTOR_BACK          4
#define GET_ANGLE                    5
#define GET_CURRENT                  6
#define SET_BEHAVIOR                 7


// Some global variables.
_PIN *nCS1; // nCS1 is a pin
int behavior = 0; // Initial behavior is 0. (Does not correspond to motor commands.)


// Function to read  from encoder.
WORD enc_readReg(WORD address) {
    WORD cmd, result;
    cmd.w = 0x4000|address.w; //set 2nd MSB to 1 for a read
    cmd.w |= parity(cmd.w)<<15; //calculate even parity for

    pin_clear(nCS1); // Set pin low before communicating over SPI
    // Send address over SPI to communicate what information we want to get back.
    spi_transfer(&spi1, cmd.b[1]);
    spi_transfer(&spi1, cmd.b[0]);
    pin_set(nCS1); // Set pin high when transfer is complete.

    pin_clear(nCS1); // Set pin low again before receiving information.
    result.b[1] = spi_transfer(&spi1, 0x0000); // Send 0x0000 when you want to receive info rather than send it.
    result.b[0] = spi_transfer(&spi1, 0x0000);
    pin_set(nCS1); // Set pin high when transfer is complete.
    return result;
}



// VendorRequests to communicate over serial.
void VendorRequests(void) {
    WORD temp;
    WORD address;

    switch (USB_setup.bRequest) {
        case TOGGLE_LED1:
            led_toggle(&led1);
            BD[EP0IN].bytecount = 0;    // set EP0 IN byte count to 0
            BD[EP0IN].status = 0xC8;    // send packet as DATA1, set UOWN bit
            
            break;
        case SET_DUTY_MOTOR_FORWARD:
            pin_write(&D[07], USB_setup.wValue.w);
            BD[EP0IN].bytecount = 0;    // set EP0 IN byte count to 0
            BD[EP0IN].status = 0xC8;    // send packet as DATA1, set UOWN bit
            break;
        case GET_DUTY_MOTOR_FORWARD:
            temp.w = pin_read(&D[07]);
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;    // set EP0 IN byte count to 2
            BD[EP0IN].status = 0xC8;    // send packet as DATA1, set UOWN bit
            break;  

        case SET_DUTY_MOTOR_BACK:
            pin_write(&D[8], USB_setup.wValue.w);
            BD[EP0IN].bytecount = 0;    // set EP0 IN byte count to 0
            BD[EP0IN].status = 0xC8;    // send packet as DATA1, set UOWN bit
            break;

        case GET_DUTY_MOTOR_BACK:
            temp.w = pin_read(&D[8]);
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;    // set EP0 IN byte count to 2
            BD[EP0IN].status = 0xC8;    // send packet as DATA1, set UOWN bit
            break;  

        case GET_ANGLE:
            address.w = 0x3fff;
            angle = enc_readReg(address);
            temp = angle;
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;    // set EP0 IN byte count to 2
            BD[EP0IN].status = 0xC8;    // send packet as DATA1, set UOWN bit
            break;

        case GET_CURRENT:
            temp.w = pin_read(&A[0]);
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;    // set EP0 IN byte count to 2
            BD[EP0IN].status = 0xC8;    // send packet as DATA1, set UOWN bit
            break;  


        case SET_BEHAVIOR:
            behavior = USB_setup.wValue.w;
            BD[EP0IN].bytecount = 0;    // set EP0 IN byte count to 0
            BD[EP0IN].status = 0xC8;    // send packet as DATA1, set UOWN bit
            break;

        default:
            USB_error_flags |= 0x01;    // set Request Error Flag
    }
}

void VendorRequestsIn(void) {
    switch (USB_request.setup.bRequest) {
        default:
            USB_error_flags |= 0x01;                    // set Request Error Flag
    }
}

void VendorRequestsOut(void) {
    switch (USB_request.setup.bRequest) {
        default:
            USB_error_flags |= 0x01;                    // set Request Error Flag
    }
}


int16_t main(void) {
    init_clock();
    init_uart();
    init_pin();
    init_ui();
    init_oc();
    init_spi();
    init_timer();
    
    nCS1 = &D[3];
    pin_digitalOut(nCS1);
    pin_analogIn(&A[0]);
    
    // Open SPI communication and specify important pins and parameters.
    spi_open(&spi1, &D[1], &D[0], &D[2], 1e6, 0);

    // send register address (2 bytes)
    WORD address;
    address.w = 0x3fff; // This is the address we read from to get the value of the angular position.
    WORD temp; // Used in USB serial communication.
    
    // Initialize variables to 0
    int angle = 0;
    int previous_angle=0;
    int current = 0; 
    int w=0; // angular velocity

    //TIMER FOR DAMPER
    timer_setPeriod(&timer2, 0.01);
    timer_start(&timer2);

    // OC PWM for motor duty
    oc_pwm(&oc1, &D[7], NULL, 20e3, 0); // PWM to Motor 1 Forwards
    oc_pwm(&oc2, &D[8], NULL, 20e3, 0); // PWM to Motor 1 Forwards

    InitUSB();                              // initialize the USB registers and serial interface engine
    while (USB_USWSTAT!=CONFIG_STATE) {     // while the peripheral is not configured...
        ServiceUSB();                       // ...service USB requests
    }
    while (1) {
        ServiceUSB();                       // service any pending USB requests
        address.w = 0x3fff;
        temp = enc_readReg(address);
        angle = temp.b[0]+temp.b[1]*256;
        
        if (angle <13000){
            angle += 16398;
        }

        // When the behavior is set using the python code, it changes which case is selected here.
        switch (behavior){            
            case 1:
            // VIRTUAL SPRING                
                if (angle > 20000 && angle < 22000){
                    pin_write(&D[7], 0x0000);
                    pin_write(&D[8], (angle-20000)*20+0x3000);
                    led_on(&led1);

                }
                else if (angle > 18000 && angle < 20000) {
                    led_on(&led2);
                    pin_write(&D[8], 0x0000);
                    pin_write(&D[7], (20000-angle)*20+0x3000);

                }
                else {
                    pin_write(&D[7], 0x0000);
                    pin_write(&D[8], 0x0000);
                    led_off(&led1);
                    led_off(&led2);
                }

                break;
            
            case 2:
            // VIRTUAL WALL
                if (angle > 22000 && previous_angle < 22000){
                    led_on(&led1);
                    led_off(&led2);
                    pin_write(&D[8], 0x0000);
                    pin_write(&D[07], 0xffff);
                }
                
      
                else if (angle < 22000 && previous_angle > 22000) {
                    pin_write(&D[07], 0x0000);
                    pin_write(&D[7], 0x0000);
                    led_on(&led2);
                    led_off(&led1);
                }

                previous_angle = angle;
                
                break;

            case 3:
            // VIRTUAL TEXTURE - CORRUGATED

                if (angle > 20000 && angle < 22000){
                    pin_write(&D[7], 0x0000);
                    pin_write(&D[8], (angle-20000)*500+0x3000);
                    led_on(&led1);

                }
                else if (angle > 18000 && angle < 20000) {
                    led_on(&led2);
                    pin_write(&D[8], 0x0000);
                    pin_write(&D[7], (20000-angle)*500+0x3000);

                }
                else {
                    pin_write(&D[7], 0x0000);
                    pin_write(&D[8], 0x0000);
                    led_off(&led1);
                    led_off(&led2);
                }

                break;
            
            case 4:
            // VIRTUALDAMPER
                
                if (timer_flag(&timer2)) {
                    timer_lower(&timer2);
                    w = (angle - previous_angle);
                    previous_angle = angle;
                    
                }

                
                if (w < 0){
                    pin_write(&D[7], 0x0000);
                    pin_write(&D[8], 0x0000);
                    led_on(&led2);
                    led_off(&led1);
                    led_off(&led3);
                }
                else if (w > 0){
                    // pin_write(&D[8], (0xf000+(w/300 *(0xffff-0x4000)) || 0x0000);
                    pin_write(&D[8], (w*400));
                    pin_write(&D[7], 0x0000);
                    led_on(&led1);
                    led_off(&led2);                    
                    led_off(&led3);
                }
                else {
                    led_off(&led1);
                    led_off(&led2);
                    led_off(&led3);
                }
                break;
        }
    }  
}

