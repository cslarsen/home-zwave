#! /usr/bin/env python
# -*- coding: utf-8 -*-

from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import Queue
import code
import collections
import contextlib
import datetime
import logging
import louie
import os
import pyudev
import sqlite3
import sys
import threading
import time

class Db:
  def __init__(self, location):
    self.location = location
    self.con = sqlite3.connect(location)
    if self.empty():
      self.create_schema()

  @contextlib.contextmanager
  def cursor(self):
    c = self.con.cursor()
    yield c
    c.close()

  def close(self):
    """Flushes changes to disk and closes connection."""
    self.con.commit()
    self.con.close()

  def empty(self):
    with self.cursor() as c:
      return len(c.execute("select * from SQLITE_MASTER").fetchall()) == 0

  def create_schema(self):
    logging.info("Creating database %s" % self.location)

    with self.cursor() as c:
      c.execute("""create table value (
                    recorded_utc datetime default current_timestamp,
                    value_id integer,
                    value real)""")

  def add_value(self, timestamp, value):
    with self.cursor() as c:
      c.execute("insert into value (recorded_utc, value_id, value) values (?,?,?)",
          (timestamp, value.value_id, float(value.data)))

class DataQueue:
  queue = Queue.Queue(10000)
  running = True

  def __init__(self, location):
    self.db = Db(location)

  @staticmethod
  def worker(*args, **kw):
    logging.info("Database location: %s" % kw.get("location", "<unset>"))
    queue = DataQueue(kw.get("location", ":memory:"))

    # Time until we save to disk
    commit_timeout = datetime.timedelta(seconds=30)

    # Time to wait for each queue item
    get_timeout = 3

    try:
      start = datetime.datetime.utcnow()
      while True:
        try:
          item = DataQueue.queue.get(block=True, timeout=get_timeout)
          queue.db.add_value(*item)
          DataQueue.queue.task_done()
        except Queue.Empty:
          if not DataQueue.running:
            # Exit after saving remaining items
            break
          else:
            # Flush database to disk after some time
            now = datetime.datetime.utcnow()
            if (now - start) >= commit_timeout:
              start = now
              queue.db.con.commit()
    finally:
      queue.db.close()

  @staticmethod
  def put(*args, **kw):
    DataQueue.queue.put(*args, **kw)

  @staticmethod
  def stop():
    DataQueue.running = False


class Signal:
  @staticmethod
  def node_updated(*args, **kw):
    logging.info("Node updated args=%s kw=%s" % (args, kw))

  @staticmethod
  def node_event(*args, **kw):
    logging.info("Node event args=%s kw=%s" % (args, kw))

  @staticmethod
  def value_updated(network, node, value):
    name = node.product_name
    if not name:
      name = node.product_type

    logging.info("Value updated node_id=%s value_id=%x '%s' %s: %s %s" % (
      node.node_id,
      value.value_id,
      name,
      value.label,
      value.data,
      value.units))

    if isinstance(value.data, float) or isinstance(value.data, int):
      DataQueue.put((datetime.datetime.utcnow(), value), block=True)

  @staticmethod
  def network_started(network):
    logging.info("Network started")

  @staticmethod
  def network_failed(network):
    logging.info("Network failed")

  @staticmethod
  def network_ready(network):
    logging.info("Network ready")

def create_zwave_options(
    device,
    config_path = "/usr/local/etc/openzwave", # TODO: Auto-discover
    user_path = ".",
    cmd_line = ""):
  try:
    options = ZWaveOption(
        device,
        config_path=config_path,
        user_path=user_path,
        cmd_line=cmd_line)

    options.set_console_output(False)
    options.set_logging(False)
    options.lock()
    return options
  except ZWaveOption:
    # TODO: Seems device can only be used by one process at the time. If so,
    # try to give a meaningful error message
    raise

def discover_device():
  """Attempts to discover ZWave controller serial device."""
  udev = pyudev.Context()

  for dev in udev.list_devices():
    # Look for Z-Stick (Sigma Designs)
    if (dev.get("ID_VENDOR_ID", "") == u"0658" and
        dev.get("ID_MODEL", "") == u"0200" and
        dev.subsystem == "tty"):

      init = dev.time_since_initialized
      devname = dev["DEVNAME"]
      vendor = dev["ID_VENDOR_FROM_DATABASE"]

      logging.info("Found %s (%s, initialized %s UTC)" % (devname, vendor,
        (datetime.datetime.utcnow() - init)))
      return devname
  raise RuntimeError("Could not find any ZWave USB controllers.")

def check_device(device):
  if not os.path.exists(device):
    raise RuntimeError("Device does not exist: %s" % device)

  if not os.access(device, os.R_OK):
    raise RuntimeError("Cannot read from device (need sudo?): %s" % device)

def main():
  logging.basicConfig(level=logging.INFO,
    format="%(asctime)-15s %(levelno)d %(message)s")

  # TODO: Put in argparse
  device = None
  if device is None:
    device = discover_device()
  check_device(device)


  options = create_zwave_options(device=device)
  network = ZWaveNetwork(options, log=None, autostart=False)

  # Set up signaling
  louie.dispatcher.connect(Signal.node_updated, ZWaveNetwork.SIGNAL_NODE)
  louie.dispatcher.connect(Signal.value_updated, ZWaveNetwork.SIGNAL_VALUE)
  louie.dispatcher.connect(Signal.network_started, ZWaveNetwork.SIGNAL_NETWORK_STARTED)
  louie.dispatcher.connect(Signal.network_failed, ZWaveNetwork.SIGNAL_NETWORK_FAILED)
  louie.dispatcher.connect(Signal.network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)
  louie.dispatcher.connect(Signal.node_event, ZWaveNetwork.SIGNAL_NODE_EVENT)

  # TODO: Find light switch

  queue = threading.Thread(target=DataQueue.worker,
      kwargs={"location": "home.db"},
      name="db")
  queue.start()

  try:
      network.start()
      code.interact(local=locals())
  except KeyboardInterrupt:
    pass
  finally:
    logging.info("\nStopping network ...")
    network.stop()

    logging.info("Stopping data queue ...")
    DataQueue.stop()
    queue.join()

if __name__ == "__main__":
  main()
