from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import datetime
import os
import sys
import time

def log(message, file=sys.stdout):
  file.write(message)
  file.flush()

def wait_state(network, state=network.STATE_READY, timeout_secs=-1,
    sleep=0.25):
  now = datetime.datetime.now
  start = now()
  prev = None

  while True:
    if prev != network.state:
      prev = network.state
      log("%s (%d/%d)\n" % (network.state_str, network.state, state))

    if network.state >= state:
      break

    diff = now() - start
    if timeout_secs > 0 and diff.seconds >= timeout_secs:
      break

    time.sleep(sleep)

def main():
  # TODO: Auto-discover
  device = "/dev/ttyACM1"

  # TODO: Auto-discover
  config_path = "/usr/local/etc/openzwave"

  user_path = "."
  cmd_line = ""

  if not os.path.exists(device):
    raise RuntimeError("Device does not exist: %s" % device)

  if not os.access(device, os.R_OK):
    raise RuntimeError("Cannot read from device (need sudo?): %s" % device)

  try:
    options = ZWaveOption(
        device,
        config_path=config_path,
        user_path=user_path,
        cmd_line=cmd_line)

    options.set_console_output(False)
    options.set_logging(False)
    options.lock()
  except ZWaveOption:
    # TODO: Seems device can only be used by one process at the time. If so,
    # try to give a meaningful error message
    raise

  network = ZWaveNetwork(options, log=None)
  #print(network) # TODO: Does not work, seems to be a bug in python-openzwave

  wait_state(network)

  if not network.is_ready:
    log("Network is not ready")
  else:
    log("Network is ready")

  for node in map(network.nodes.get, network.nodes):
    print(node)

if __name__ == "__main__":
  main()
