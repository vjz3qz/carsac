#!/usr/bin/env python3
# RFID Wiegand Controller software with Arduino middleman - serialRF.py3
# Copyright (C) 2021-2023 John Kothmann & Varun Pasupuleti
# Contact via email: kothmannj@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


import serial
import RPi.GPIO as GPIO
import time
from datetime import datetime
from AuthModule import auth, log, auth_PIN, loadUsers
import configparser as cp
import sys, getopt

if __name__ == '__main__':
    # Read Config file:
    configfile = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "k:")
    except getopt.GetoptError:
        print("Usage: serialRF.py3 -k <configfilepath>")
        sys.exit(2)
    for opt, arg in opts:
        if (opt != '-k'):
            print('Usage: serialRF.py3 -k <configfilepath>')
        else:
            configfile = arg

    config = cp.ConfigParser()
    config.read(configfile)
    mainconf = config["MAIN"]
    DOOR_ID = mainconf["door_id"]
    BAUD_RATE = int(mainconf["baud_rate"])
    GPIO_PIN = int(mainconf["gpio_out"])
    OPEN_TIME_SECS = int(mainconf["open_time"])
    LOG_ENABLED = mainconf["use_logging"]
    LOG_FILEPATH = mainconf["log_filepath"]
    SERIAL_PORT = mainconf["serial_port"]
    authconf = config["AUTH"]
    AUTH_FILEPATH = authconf["auth_filepath"]
    # set up logging if configured
    if LOG_ENABLED == "True" or LOG_ENABLED == "True #only accepts True or False":
        logging = True
    else:
        logging = False
    # Set up serial communications with microcontroller at baud rate defined by user
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.flush()
    # Set up GPIO output
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    GPIO.output(GPIO_PIN, GPIO.LOW)
    try:
        # add userDict before while true loop to allow it to be passed into auth function.
        userDict = loadUsers(AUTH_FILEPATH)
        while True:
            # Loop infinitely until serial communications received
            if ser.in_waiting > 0:
                # Read in authentication request from microcontroller; formatted according to arduino C script
                line = ser.readline().decode('utf-8').rstrip()
                # If successful read was parsed by arduino code
                if line[0:4] == "Card":
                    # line[22:28] is card ID hex value, create tuple of card ID and door ID to pass to authFile module
                    tup = auth(line[22:28], DOOR_ID, userDict)
                    if tup[0]:
                        # if authentication success:
                        logStringGranted = "Granted Access to User " + tup[1] + " with card ID " + line[22:28]
                        print("[CONSOLE]: " + logStringGranted)
                        # Open door
                        GPIO.output(GPIO_PIN, GPIO.HIGH)
                        time.sleep(OPEN_TIME_SECS)
                        GPIO.output(GPIO_PIN, GPIO.LOW)
                        # Log event
                        if logging: log(logStringGranted, LOG_FILEPATH)
                    elif tup[1] == "Unknown":
                        # If card not in authentication file, log event
                        logStringUnknown = "Access Denied: Card with ID " + line[22:28] + " is not recognized."
                        print("[CONSOLE]: " + logStringUnknown)
                        if logging: log(logStringUnknown, LOG_FILEPATH)
                    else:
                        logStringDenied = "Access Denied: User " + tup[1] + " with card ID " + line[
                                                                                               22:28] + " has insufficient permissions."
                        print("[CONSOLE]: " + logStringDenied)
                        if logging: log(logStringDenied, LOG_FILEPATH)
                elif line[0:3] == "PIN":
                    splits = line.split()
                    tup = auth_PIN(splits[1], DOOR_ID, AUTH_FILEPATH)
                    print("PIN Received: " + line)
                    print(splits[1])
                    if tup[0]:
                        logStringPINGranted = "Granted Access to User " + tup[1] + " using PIN code."
                        print("[CONSOLE]: " + logStringPINGranted)
                        if logging: log(logStringPINGranted, LOG_FILEPATH)
                        GPIO.output(GPIO_PIN, GPIO.HIGH)
                        time.sleep(OPEN_TIME_SECS)
                        GPIO.output(GPIO_PIN, GPIO.LOW)
                    elif tup[1] == "Unknown":
                        logStringPINUnk = "Denied Access to Unrecognized PIN Attempt with PIN: " + splits[1]
                        print("[CONSOLE]: " + logStringPINUnk)
                        if logging: log(logStringPINUnk, LOG_FILEPATH)
                    else:
                        logStringPINDenied = "Denied Access to User " + tup[1] + " using PIN code."
                        print("[CONSOLE]: " + logStringPINDenied)
                        if logging: log(logStringPINDenied, LOG_FILEPATH)
                else:
                    print("[CONSOLE]: Unexpected Input Received: " + line)
    except KeyboardInterrupt:
        print("[CONSOLE]: Program Stopped")
    finally:
        GPIO.cleanup()
