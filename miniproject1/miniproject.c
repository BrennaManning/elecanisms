#include <p24FJ128GB206.h>
#include "config.h"
#include "common.h"
#include "ui.h"
#include "timer.h"
#include "oc.h"
#include "pin.h"
#include "uart.h"

int16_t main(void) {
    init_clock();
    init_ui();
    init_timer();
    init_pin();
    init_oc();
    init_uart();
    led_on(&led1);
    led_on(&led2);

    int i;
    for(i = 1; i < 9; i++){
        pin_digitalOut(&D[i]);
        pin_clear(&D[i]);
    }

    while (1) {
         oc_pwm(&oc1, &D[7], NULL, 10e3, 0x8000); // 50% duty cycle
        //pin_write(&D[7], 12);
     
        //pin_set(&D[7]);
        //pin_clear(&D[8]);
        //led_on(&led1);
        //pin_toggle(&D[7]);
        if (timer_flag(&timer2)) {
            timer_lower(&timer2);
            //pin_toggle(&D[7]);
            led_toggle(&led1);
        }/*
        led_write(&led2, !sw_read(&sw2));
        led_write(&led3, !sw_read(&sw3)); */
        

    } 
}