import serial
import time
import firebase_admin
from firebase_admin import credentials, firestore
from threading import Thread

# Initialize Firebase
cred = credentials.Certificate("connectoarm.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Serial port setup
debug = False
servo_data = [45, 0, 180, 45]

if not debug:
    ser = serial.Serial('COM5', 115200)  # Open serial port

# Function to adjust servo angles based on command
def adjust_servo_data(command):
    global servo_data
    if command == 'down':
        servo_data[2] = min(180, servo_data[2] + 20)  # Increment tilt down
    elif command == 'up':
        servo_data[2] = max(130, servo_data[2] - 20)  # Decrement tilt up
    elif command == 'back':
        servo_data[1] = max(0, servo_data[1] - 20)    # Increment front
    elif command == 'front':
        servo_data[1] = min(75, servo_data[1] + 20)   # Decrement back
    elif command == 'right':
        servo_data[0] = max(0, servo_data[0] - 20)    # Pan left
    elif command == 'left':
        servo_data[0] = min(180, servo_data[0] + 20)  # Pan right
    elif command == 'open':
        servo_data[3] = 60
    elif command == 'close':
        servo_data[3] = 0
    print(f"Adjusted servo data: {servo_data}")

# Function to send servo data to Arduino
def send_to_arduino():
    global servo_data
    if not debug:
        try:
            ser.write(bytearray(servo_data))
            time.sleep(0.8)
            print(f"Sent to serial: {servo_data} , {bytearray(servo_data)}")
        except Exception as e:
            print(f"Error sending data to Arduino: {e}")
            ser.close()

# Firestore listener callback
def on_snapshot(doc_snapshot, changes, read_time):
    global servo_data
    servo_data = [45, 0, 180, 45]
    send_to_arduino()
    for doc in doc_snapshot:
        commands = doc.to_dict().get("commands", [])
        for command in commands:
            if command in ['up', 'down', 'front', 'back', 'left', 'right', 'open', 'close']:
                adjust_servo_data(command)
                send_to_arduino()
            else:
                print(f"Invalid command: {command}")

# Firestore listener setup
def listen_for_commands():
    doc_ref = db.collection("ArmControl").document("Control")
    doc_ref.on_snapshot(on_snapshot)

# Start Firestore listener in a separate thread
listener_thread = Thread(target=listen_for_commands)
listener_thread.start()

# Main program loop to handle manual commands (if needed)
try:
    while True:
        command = input("Enter command (up, down, front, back, left, right, open, close) or 'q' to quit: ").lower()
        if command == 'q':
            ser.close()  # Close the port when quitting
            break
        elif command in ['up', 'down', 'front', 'back', 'left', 'right', 'open', 'close']:
            adjust_servo_data(command)
            send_to_arduino()
        else:
            print("Invalid command.")
except KeyboardInterrupt:
    ser.close()  # Ensure the serial port closes on exit
    print("Program exited.")
