import socket
import struct
import time
import numpy as np
import math
import random

# Receiver address (raspberry pi)
RECEIVER_IP = "192.168.8.107"
RECEIVER_PORT = 12345

PACKET_MAGIC = b"ATMP"
SAMPLE_RATE = 8000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

seq = 0

print("Starting simulated PYNQ sender...")
print("Press CTRL+C to stop")

while True:

    # Simulate temperature (20–30 C)
    temp_c = 25 + random.uniform(-3, 3)

    # Generate simulated microphone signal
    samples = np.random.normal(0, 2000, 160).astype(np.int16)

    # Calculate dBFS
    rms = np.sqrt(np.mean(samples.astype(np.float64)**2))
    if rms > 0:
        dbfs = 20 * math.log10(rms / 32767)
    else:
        dbfs = -120

    sample_count = len(samples)

    header = struct.pack(
        "!4sIdffHH",
        PACKET_MAGIC,
        seq,
        time.time(),
        temp_c,
        dbfs,
        SAMPLE_RATE,
        sample_count
    )

    packet = header + samples.tobytes()

    sock.sendto(packet, (RECEIVER_IP, RECEIVER_PORT))

    print(f"seq={seq}  temp={temp_c:.2f}C  level={dbfs:.1f} dBFS")

    seq += 1

    time.sleep(1)
