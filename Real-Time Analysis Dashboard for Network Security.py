import socket
import psutil
import time
import matplotlib.pyplot as plt
import threading

# --- Data Collection ---

def get_network_data():
  """Collects network usage data."""
  net_io = psutil.net_io_counters()
  bytes_sent = net_io.bytes_sent
  bytes_recv = net_io.bytes_recv
  packets_sent = net_io.packets_sent
  packets_recv = net_io.packets_recv
  return bytes_sent, bytes_recv, packets_sent, packets_recv

def get_top_applications():
  connections = psutil.net_connections()
  app_data = {}
  for conn in connections:
    if conn.status == 'ESTABLISHED' and conn.raddr:
      app_name = psutil.Process(conn.pid).name()
      app_data[app_name] = app_data.get(app_name, 0) + 1
  sorted_app_data = sorted(app_data.items(), key=lambda item: item[1], reverse=True)
  return sorted_app_data[:5]  

# --- Visualization ---

def update_plot(sent_data, recv_data, packets_sent, packets_recv, top_apps):
  """Updates the real-time plot."""
  plt.clf()

  # Bandwidth Usage
  plt.subplot(3, 1, 1)
  plt.plot(sent_data, label='Bytes Sent')
  plt.plot(recv_data, label='Bytes Received')
  plt.ylabel('Bytes')
  plt.title('Network Bandwidth Usage')
  plt.legend()

  # Packet Usage
  plt.subplot(3, 1, 2)
  plt.plot(packets_sent, label='Packets Sent')
  plt.plot(packets_recv, label='Packets Received')
  plt.ylabel('Packets')
  plt.title('Network Packet Usage')
  plt.legend()

  # Top Applications
  plt.subplot(3, 1, 3)
  apps = [app[0] for app in top_apps]
  connections = [app[1] for app in top_apps]
  plt.bar(apps, connections)
  plt.xlabel('Applications')
  plt.ylabel('Active Connections')
  plt.title('Top Applications')

  plt.tight_layout()
  plt.pause(1)  # Update every 1 second

# --- Background Data Collection ---

def collect_data(sent_data, recv_data, packets_sent, packets_recv):
  """Collects data in the background."""
  while True:
    bytes_sent, bytes_recv, packets_sent_now, packets_recv_now = get_network_data()
    sent_data.append(bytes_sent)
    recv_data.append(bytes_recv)
    packets_sent.append(packets_sent_now)
    packets_recv.append(packets_recv_now)
    time.sleep(1)

# --- Main Loop ---

def main():
  plt.ion()  
  fig = plt.figure()

  sent_data = []
  recv_data = []
  packets_sent = []
  packets_recv = []

  # Start data collection thread
  data_thread = threading.Thread(target=collect_data, args=(sent_data, recv_data, packets_sent, packets_recv))
  data_thread.daemon = True  
  data_thread.start()

  try:
    while True:
      top_apps = get_top_applications()
      update_plot(sent_data, recv_data, packets_sent, packets_recv, top_apps)

  except KeyboardInterrupt:
    print("Exiting...")
    plt.close(fig)

if __name__ == "__main__":
  main()