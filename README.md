home-zwave
==========

A small experiment using Python OpenZWave.

Currently, it listens in on ZWave network events and records them to an SQLite3
database.

To start up:

  * You need to be root, or a member of the ``dialout`` group, because you need
    write access to the ZWave device's serial interface.
  * Edit the ``device`` setting. It should point to your ZWave controller, e.g.
    ``/dev/ttyACM0``. Do a ``dmesg | grep tty`` to get a clue.
  * No other programs must be using the ZWave device.

The entire program is event driven, and will start up without waiting for the
network to be ready. This means it will take some time to see all devices.

After booting, you are dropped into a true Python REPL. You can do stuff here
while the program runs concurrently (start with the ``network`` instance), but
I haven't added any interactive commands yet.

E.g., you can do

    $ sudo python home.py
    ...
    INFO:root:Value updated node_id=2 value_id=100000002494000 'Smart Energy Switch' Switch: True
    INFO:root:Value updated node_id=2 value_id=100000002c9c004 'Smart Energy Switch' Switch All: On and Off Enabled
    INFO:root:Value updated node_id=2 value_id=1000000024c4042 'Smart Energy Switch' Power: 0.0 W
    INFO:root:Value updated node_id=2 value_id=1000000024c8002 'Smart Energy Switch' Energy: 0.686999976635 kWh
    INFO:root:Value updated node_id=2 value_id=1000000024c8012 'Smart Energy Switch' Previous Reading: 0.686999976635 kWh
    INFO:root:Value updated node_id=2 value_id=1000000024c8023 'Smart Energy Switch' Interval: 3083 seconds
    ...
    >>> from pprint import pprint
    >>> pprint(map(str, network.nodes.values()))
    ['home_id: [0xffd99115] id: [1] name: [] model: [Z-Stick Gen5]',
     'home_id: [0xffd99115] id: [2] name: [] model: [Smart Energy Switch]',
     'home_id: [0xffd99115] id: [3] name: [] model: [MultiSensor 6]']

Hit ``CTRL+D`` to stop the server gracefully. It first stops the ZWave network,
then it will flush any pending values to the database.

If you don't like running with ``sudo``, just add yourself to the ``dialout``
group and log out and in again:

    $ sudo usermod -a -G dialout your-user-name

Type ``groups`` to verify that you're a member of ``dialout``, and you should
be able to run simply ``python home.py``.

To pair devices and set them up, I usually use the ``ozwcp`` program that comes
with OpenZWave. It's great.

Requirements
------------

You need the following Python modules:

  * python-openzwave
  * sqlite3
  * louie
  * (soon) pyudev

Additionally, Python-OpenZWave requires the C++ version of OpenZWave. It should
be bundled with the Python distribution, though.

My setup
--------

In case you're planning to start experimenting with ZWave, this is my setup:

  * Raspberry Pi 2
  * Aeotec Z-Stick Gen5 (which Linux reports as Sigma Designs; might be an OEM)
  * Aeotec MultiSensor 6
  * Aeotec Smart Energy Switch (power metering and actuator)

License
=======
Copyright 2015 Christian Stigen Larsen  
Distributed under the GPL v3 or later.
