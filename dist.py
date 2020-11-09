#!/usr/bin/python
import RPi.GPIO as GPIO
import time

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash

from time import sleep

# Pins where we have connected servos
#servo_pin = 37 # 26
#servo_pin1 = 35 # 19
PIN_TRIGGER = 23
PIN_ECHO = 24

GPIO.setmode(GPIO.BOARD) # We are using the BCM pin numbering
# Declaring Servo Pins as output pins
#GPIO.setup(servo_pin, GPIO.OUT)
#GPIO.setup(servo_pin1, GPIO.OUT)

GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)

# Created PWM channels at 50Hz frequency
#p = GPIO.PWM(servo_pin, 50)
#p1 = GPIO.PWM(servo_pin1, 50)

# Initial duty cycle
#p.start(0)
#p1.start(0)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Ohjaa moottoria'),
    dcc.Slider(
        id='slider-updatemode',
        marks={i: '{}'.format(10 ** i) for i in range(4)},
        min=1,
        max=12.5,
        value=1,
        step=0.01,
        updatemode='drag'
        ),
    html.Br(),
    html.Br(),
    html.Div(id='updatemode-output-container', style={'margin-top': 20}),
    dcc.Interval(
        id='interval-component',
        interval=2 * 1000,  # in milliseconds
        n_intervals=0
        ),
    html.Div(id='distance')
    ])

def distance():
    dist = ''
    #try:

    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    print ("Waiting for sensor to settle")

    time.sleep(0.5)

    print ("Calculating distance")

    GPIO.output(PIN_TRIGGER, GPIO.HIGH)

    time.sleep(0.00001)

    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    while GPIO.input(PIN_ECHO)==0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO)==1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    dist = round(pulse_duration * 17150, 2)
    print ("Distance:",dist,"cm")

    #finally:
    #      GPIO.cleanup()
    time.sleep(0.1)
    return dist

#@app.callback(Output('updatemode-output-container', 'children'),
#              [Input('slider-updatemode', 'value')])
#def display_value(value):
#    p.ChangeDutyCycle(float(value))
#    return 'Value: {}'.format(value)


@app.callback(Output('distance', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    dist = distance()
    print(dist)
    return dist

PORT = 8888
ADDRESS = '0.0.0.0'
if __name__ == '__main__':
    app.run_server(port=PORT, host=ADDRESS, debug=True)



