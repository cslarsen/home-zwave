home-zwave
==========

A small experiment using Python OpenZWave.

Currently, it listens in on ZWave network events and records them to an SQLite3
database.

To start up:

  * You need to be root, because of write access to the ZWave device
  * Edit the ``device`` setting. It should point to your ZWave controller, e.g.
    ``/dev/ttyACM0``. Do a ``dmesg | grep tty`` to get a clue.
  * No other programs must be using the ZWave device.

The entire program is event driven, and will start up without waiting for the
network to be ready. This means it will take some time to see all devices.

After booting, you are dropped into a Python REPL. You can do stuff here while
the program runs concurrently, but I haven't added any interactive commands
yet.

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
