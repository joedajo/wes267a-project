import socket
import struct
import numpy as np
import math

LISTEN_IP = "0.0.0.0" #listen on all IPs
LISTEN_PORT = 12345
PACKET_MAGIC = b"ATMP"

HEADER_FMT = "!4sIdffHH"
HEADER_SIZE = struct.calcsize(HEADER_FMT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))

print(f"Listening on UDP {LISTEN_IP}:{LISTEN_PORT}")

def pcm16_dbfs(samples):

    if samples.size == 0:
        return -120

    rms = np.sqrt(np.mean(samples.astype(np.float64)**2))

    if rms <= 0:
        return -120

    return 20 * math.log10(rms / 32767)

while True:

    packet, addr = sock.recvfrom(4096)

    if len(packet) < HEADER_SIZE:
        continue

    magic, seq, ts, temp_c, dbfs_tx, sample_rate, sample_count = struct.unpack(
        HEADER_FMT, packet[:HEADER_SIZE]
    )

    if magic != PACKET_MAGIC:
        continue

    audio_bytes = packet[HEADER_SIZE:]

    pcm16 = np.frombuffer(audio_bytes, dtype=np.int16)

    dbfs_rx = pcm16_dbfs(pcm16)

    temp_f = (temp_c * 9 / 5) + 32

    print(
        f"from={addr[0]} "
        f"seq={seq} "
        f"temp={temp_c:.2f}C "
        f"({temp_f:.2f}F) "
        f"level_tx={dbfs_tx:.1f}dBFS "
        f"level_rx={dbfs_rx:.1f}dBFS "
        f"samples={sample_count}"
    )
