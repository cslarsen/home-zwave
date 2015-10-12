#! /usr/bin/env python
# -*- coding: utf-8 -*-

from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import code
import datetime
import logging
import louie
import os
import sys
import time

class Signal:
  @staticmethod
  def node_updated(network, node):
    logging.info("Node updated %s" % node)

  @staticmethod
  def node_event(*args, **kw):
    logging.info("node event args=%s kw=%s" % (args, kw))

  @staticmethod
  def value_updated(network, node, value):
    name = node.product_name
    if not name:
      name = node.product_type

    logging.info("s node_id=%s value_id=%x '%s' %s: %s %s" % (
      node.node_id,
      value.value_id,
      name,
      value.label,
      value.data,
      value.units))

  @staticmethod
  def network_started(network):
    logging.info("Network started")

  @staticmethod
  def network_failed(network):
    logging.info("Network failed")

  @staticmethod
  def network_ready(network):
    logging.info("Network ready")

def get_options(
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

def main(device = "/dev/ttyACM0"): # TODO: Auto-discover
  logging.basicConfig(level=logging.INFO)
  logging.info("Starting up")

  if not os.path.exists(device):
    raise RuntimeError("Device does not exist: %s" % device)

  if not os.access(device, os.R_OK):
    raise RuntimeError("Cannot read from device (need sudo?): %s" % device)

  options = get_options(device=device)

  network = ZWaveNetwork(options, log=None, autostart=False)
  #print(network) # TODO: Does not work, seems to be a bug in python-openzwave

  # Set up signaling
  louie.dispatcher.connect(Signal.node_updated, ZWaveNetwork.SIGNAL_NODE)
  louie.dispatcher.connect(Signal.value_updated, ZWaveNetwork.SIGNAL_VALUE)
  louie.dispatcher.connect(Signal.network_started, ZWaveNetwork.SIGNAL_NETWORK_STARTED)
  louie.dispatcher.connect(Signal.network_failed, ZWaveNetwork.SIGNAL_NETWORK_FAILED)
  louie.dispatcher.connect(Signal.network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)
  louie.dispatcher.connect(Signal.node_event, ZWaveNetwork.SIGNAL_NODE_EVENT)

  # Find light switch

  try:
    network.start()
    #while True:
    #  time.sleep(5)
    code.interact(local=locals())
  except KeyboardInterrupt:
    pass
  finally:
    logging.info("\nStopping network ...")
    network.stop()

if __name__ == "__main__":
  main()
