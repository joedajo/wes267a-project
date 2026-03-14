import time
import smbus
import socket

OLED_ADDR = 0x3C
bus = smbus.SMBus(1)

def oled_cmd(*cmds):
    buf = bytearray(list(cmds))

    for i in range(0, len(buf), 32):
        bus.write_i2c_block_data(OLED_ADDR, 0x00 + i*32, [x for x in buf[i:i+32]])
    
    # i2c.write(OLED_ADDR, buf, len(buf))
    # bus.write_i2c_block_data(OLED_ADDR, 0x00, bytearray(list(cmds)))
    
def oled_data(data_bytes):
    if isinstance(data_bytes, list):
        data_bytes = bytes(data_bytes)

    buf = data_bytes

    for i in range(0, len(buf), 32):
        bus.write_i2c_block_data(OLED_ADDR, 0x40 + i*32, [x for x in buf[i:i+32]])

    # bus.write_i2c_block_data(OLED_ADDR, 0x40, bytearray(list(cmds)))
    # i2c.write(OLED_ADDR, buf, len(buf))

def oled_set_pos(page, col):
    oled_cmd(0xB0 + page)
    oled_cmd(0x00 + (col & 0x0F))
    oled_cmd(0x10 + (col >> 4))
    
def oled_clear():
    for page in range(8):
        oled_set_pos(page, 0)
        oled_data([0x00] * 128)
        
def oled_init():
    oled_cmd(
        0xAE,
        0xD5, 0x80,
        0xA8, 0x3F,
        0xD3, 0x00,
        0x40,
        0x8D, 0x14,
        0x20, 0x00,
        0xA1,
        0xC8,
        0xDA, 0x12,
        0x81, 0xCF,
        0xD9, 0xF1,
        0xDB, 0x40,
        0xA4,
        0xA6,
        0xAF
    )
    time.sleep(0.1)
    oled_clear()

FONT = {
    " ": [0x00,0x00,0x00,0x00,0x00],
    "-": [0x08,0x08,0x08,0x08,0x08],
    ".": [0x00,0x60,0x60,0x00,0x00],
    ":": [0x00,0x36,0x36,0x00,0x00],
    "/": [0x20,0x10,0x08,0x04,0x02],

    "0": [0x3E,0x51,0x49,0x45,0x3E],
    "1": [0x00,0x42,0x7F,0x40,0x00],
    "2": [0x42,0x61,0x51,0x49,0x46],
    "3": [0x21,0x41,0x45,0x4B,0x31],
    "4": [0x18,0x14,0x12,0x7F,0x10],
    "5": [0x27,0x45,0x45,0x45,0x39],
    "6": [0x3C,0x4A,0x49,0x49,0x30],
    "7": [0x01,0x71,0x09,0x05,0x03],
    "8": [0x36,0x49,0x49,0x49,0x36],
    "9": [0x06,0x49,0x49,0x29,0x1E],

    "A": [0x7E,0x11,0x11,0x11,0x7E],
    "B": [0x7F,0x49,0x49,0x49,0x36],
    "C": [0x3E,0x41,0x41,0x41,0x22],
    "D": [0x7F,0x41,0x41,0x22,0x1C],
    "E": [0x7F,0x49,0x49,0x49,0x41],
    "F": [0x7F,0x09,0x09,0x09,0x01],
    "G": [0x3E,0x41,0x49,0x49,0x7A],
    "H": [0x7F,0x08,0x08,0x08,0x7F],
    "I": [0x00,0x41,0x7F,0x41,0x00],
    "J": [0x20,0x40,0x41,0x3F,0x01],
    "K": [0x7F,0x08,0x14,0x22,0x41],
    "L": [0x7F,0x40,0x40,0x40,0x40],
    "M": [0x7F,0x02,0x0C,0x02,0x7F],
    "N": [0x7F,0x04,0x08,0x10,0x7F],
    "O": [0x3E,0x41,0x41,0x41,0x3E],
    "P": [0x7F,0x09,0x09,0x09,0x06],
    "Q": [0x3E,0x41,0x51,0x21,0x5E],
    "R": [0x7F,0x09,0x19,0x29,0x46],
    "S": [0x46,0x49,0x49,0x49,0x31],
    "T": [0x01,0x01,0x7F,0x01,0x01],
    "U": [0x3F,0x40,0x40,0x40,0x3F],
    "V": [0x1F,0x20,0x40,0x20,0x1F],
    "W": [0x3F,0x40,0x38,0x40,0x3F],
    "X": [0x63,0x14,0x08,0x14,0x63],
    "Y": [0x07,0x08,0x70,0x08,0x07],
    "Z": [0x61,0x51,0x49,0x45,0x43],
}

def oled_text(page, col, text):
    oled_set_pos(page, col)
    out = []

    for ch in str(text):
        pattern = FONT.get(ch.upper(), FONT[" "])
        out.extend(pattern + [0x00])

    oled_data(out[:128-col])
    
def oled_show_env(temp_c, temp_f, mic_level, status):
    oled_clear()
    oled_text(0, 0, f"T C:{temp_c:.1f}")
    oled_text(1, 0, f"T F:{temp_f:.1f}")
    oled_text(3, 0, f"MIC:{mic_level:.1f}")
    oled_text(6, 0, status[:20])

    
RECEIVER_IP = "0.0.0.0"
PORT = 12345

def create_udp_receiver(local_ip="0.0.0.0", port=12345):# <-- UDP Receiver Functions
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_ip, port))
    return sock

def receive_packet(sock, buffer_size=1024):
    data, addr = sock.recvfrom(buffer_size)
    message = data.decode().strip()

    parts = message.split(",")

    if len(parts) < 5:
        raise ValueError(f"Invalid packet format: {message}")

    payload = {
        "temp_c": float(parts[0]),
        "temp_f": float(parts[1]),
        "mic_level": float(parts[2]),
        "temp_status": parts[3].strip(),
        "mic_status": parts[4].strip()
    }

    return payload, addr

def evaluate_status(temp_c, mic_level,  #<-- warning logic
                    hot_temp_c=30.0, 
                    cold_temp_c=15.0,
                    loud_threshold=500.0):
    warnings = []

    if temp_c >= hot_temp_c:
        warnings.append("HOT")
    elif temp_c <= cold_temp_c:
        warnings.append("COLD")

    if mic_level >= loud_threshold:
        warnings.append("LOUD")

    if not warnings:
        return "NORMAL"

    return "/".join(warnings)

def combine_status(derived_status, temp_status, mic_status):
    status_parts = []

    if derived_status and derived_status != "NORMAL":
        status_parts.append(derived_status)

    if temp_status and temp_status != "NORMAL":
        status_parts.append(temp_status)

    if mic_status and mic_status != "NORMAL":
        status_parts.append(mic_status)

    if not status_parts:
        return "NORMAL"

    final_parts = []
    for item in status_parts:
        if item not in final_parts:
            final_parts.append(item)

    return "/".join(final_parts)



print("Receiver ready on port", PORT)

sock = create_udp_receiver("192.168.1.76")

oled_init()
oled_show_env(20, 20, 20, "good")

while True:     #<-- main reciever loop
    try:
        payload, addr = receive_packet(sock)
        print(payload)

        temp_c = payload["temp_c"]
        temp_f = payload["temp_f"]
        mic_level = payload["mic_level"]
        temp_status = payload["temp_status"]
        mic_status = payload["mic_status"]

        derived_status = evaluate_status(temp_c, mic_level)
        final_status = combine_status(derived_status, temp_status, mic_status)

        print(f"From {addr[0]}:{addr[1]}")
        print(f"Temp: {temp_c:.2f} C | {temp_f:.2f} F")
        print(f"Mic Level: {mic_level:.2f}")
        print(f"Status: {final_status}")
        print("-" * 40)

        oled_show_env(temp_c, temp_f, mic_level, final_status)
    except Exception as e:
        print("Receiver error:", e)
        time.sleep(0.5)
        
