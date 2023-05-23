# CARSAC
Access control solution for the Charlottesville-Albemarle Rescue Squad

## License
Copyright 2021, 2022 by John Kothmann, Tom Baker, and Varun Pasupuleti

This file is part of CARSAC.

CARSAC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

CARSAC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with CARSAC. If not, see <https://www.gnu.org/licenses/>.

## Hardware and setup

Install a strike in the door. Use a fail-secure strike for secure facilities like a telecom closet and fail-open for doors essential for egress and rescue workers like main enterances. In the event of a power outage and depletion of the backup battery, does the door need to be locked or unlocked? Ideally, install the diode to prevent high-voltage spikes when power is disconnected but the strike coil magnetic field transiently remains.

Print a case and attach Pi 0W, Adafruit Trinket/Feather, and wiring board to the case. Solder headers to the Pi 0W and wiring board if desired for easier troubleshooting. Otherwise, solder wires between elements as indicated on the wiring board.

Connect the power supply to the wiring board per the labels on the wiring board. Use Normally Closed (NC) for fail-open and Normally Open (NO) for fail-secure strikes.

## Configuration

Install Raspbian (32-bit, headless/the lightest image possible).

Update the hostname and enable SSH with `sudo raspi-config` (general and interfacing options).

Delete the default pi user (`sudo userdel pi`)

Add desired users and their SSH keys and add them to the sudoers group (`sudo useradd -m -G sudo ansible` then `ssh-copy-id -i ~/.ssh/id_ed25519.pub ansible@A.B.C.D`)

Clone git repo into /etc/carsac (may work best with scp from host after `sudo mkdir /etc/carsac`)

Edit door-specific config information in `/etc/carsac/config.ini` (door_id)

Set up CARSAC service with `sudo mv /etc/carsac/carsac.service /etc/systemd/system/carsac.service`, `sudo systemctl daemon-reload`, `sudo systemctl enable carsac`, `sudo systemctl start carsac`

Test for functionality

Set DHCP reservation on the router and add the new machine IP to /etc/ansible/hosts on the ansible master node. Login from the master to the client via SSH and perform fingerprint verification.
