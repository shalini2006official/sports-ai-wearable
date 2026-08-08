import serial

ser = serial.Serial("COM5", 115200)

latest_data = {
    "heart_rate": 0,
    "ir": 0
}

while True:
    line = ser.readline().decode(errors="ignore").strip()

    print(line)

    try:
        if "IR =" in line:
            parts = line.split()

            latest_data["ir"] = int(parts[2])
            latest_data["heart_rate"] = int(parts[5])

    except:
        pass