#! /usr/bin/env python
# -*- coding: utf-8 -*-

from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import datetime
import os
import sys
import time

def log(message, file=sys.stdout):
  file.write(message)
  file.flush()

def wait_state(network, state=ZWaveNetwork.STATE_READY, timeout_secs=-1,
    sleep=0.25):
  now = datetime.datetime.now
  start = now()
  prev = None
  diff = now() - start

  while True:
    if prev != network.state:
      prev = network.state
      log("%s (%d/%d)\n" % (network.state_str, network.state, state))

    if network.state >= state:
      break

    diff = now() - start
    if timeout_secs > 0 and diff.seconds >= timeout_secs:
      return

    time.sleep(sleep)

  log("Time to boot: %s\n" % diff)

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
  if not os.path.exists(device):
    raise RuntimeError("Device does not exist: %s" % device)

  if not os.access(device, os.R_OK):
    raise RuntimeError("Cannot read from device (need sudo?): %s" % device)

  options = get_options(device=device)

  network = ZWaveNetwork(options, log=None)
  #print(network) # TODO: Does not work, seems to be a bug in python-openzwave

  wait_state(network)

  if not network.is_ready:
    log("Network is not ready\n")
  else:
    log("Network is ready\n")

  for node in map(network.nodes.get, network.nodes):
    print(node)

if __name__ == "__main__":
  main()
