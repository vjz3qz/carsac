#!/usr/bin/env python3
# RFID Wiegand Controller software with Arduino middleman - Authentication Module
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

import yaml
from datetime import date
from datetime import datetime
from datetime import time


# Authentication Function for RFIDs
def auth(id, doorstring, users):
    if id in users:
        user = users.get(id)
        inSched = True
        if user.get("schedule") != "all":
            inSched = False
            for sched in user.get("schedule"):
                inSched = inSched or schedCheck(sched, sched['times']['start'], sched['times']['end'])
        if inSched:
            for door in user.get("door_ids"):  # if they are a valid CARS ID, check if they have access to door
                if door == "all":  # if they have access to all doors
                    return True, user.get("username")
                if door == doorstring:  # if they have access to that door
                    return True, user.get("username")
        return False, user.get("username")
    return False, "Unknown"


# Authentication Function for PINs
def auth_PIN(pin, doorstring, authfilestring):
    authfile = open(authfilestring, "r")
    config = yaml.load_all(authfile, Loader=yaml.BaseLoader)
    for user in config:
        if str(user['PIN']) == str(pin):
            inSched = True
            if user['schedule'] != "all":
                inSched = False
                for sched in user['schedule']:
                    inSched = inSched or schedCheck(sched, sched['times']['start'], sched['times']['end'])
            if inSched:
                for door in user['door_ids']:
                    if door == 'all' or door == doorstring:
                        return True, user['username']
            return False, user['username']
    return False, "Unknown"


# Helper Function for checking a schedule against current date/time
def schedCheck(sched, startTime, endTime):
    currentDate = date.today()
    weekday = currentDate.weekday()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if weekdays[weekday] in sched or currentDate.isoformat() in sched:
        currentTime = datetime.now().time()
        startTime = datetime.strptime(sched['times']['start'], '%H:%M').time()
        endTime = datetime.strptime(sched['times']['end'], '%H:%M').time()
        if startTime <= currentTime and endTime >= currentTime:
            return True
    return False


def log(logStr, filepath):
    logFile = open(filepath, "a")
    now = datetime.now()
    timestamp = now.strftime("%m-%d-%Y %H:%M:%S")
    logFile.write("[" + timestamp + "] " + logStr + "\n")
    logFile.close()


def loadUsers(authfilestring):
    """ load function created a dictionary of card ID's mapped to a respective user's info.
    Parameters: the file path to YAML file
    authfilestring (str)
    Returns: dictionary of card ID's mapped to a dictionary contain username, door_ids, and schedule
    userDict =
    {
        cardID (str):
        {
            "username": username (str),
            "door_ids": door_ids (list),
            "schedule": schedule (str) (or something else)
            "PIN": PIN (str) (if available)
        }
    }
   """
    authfile = open(authfilestring, "r")
    yamlFile = yaml.load_all(authfile, Loader=yaml.BaseLoader)
    userDict = {}
    for user in yamlFile:  # iterates through users
        if user.get("PIN", 0) != 0:
            value = {"username": user.get("username"), "door_ids": user.get("door_ids"),
                     "schedule": user.get("schedule"), "PIN": user.get("PIN")}
        else:
            value = {"username": user.get("username"), "door_ids": user.get("door_ids"),
                     "schedule": user.get("schedule")}
        userDict[user.get("card_id")] = value
    return userDict

def createYML(users):
    with open('permissions.yml', 'w') as f:
        yaml.dump(users, f)
