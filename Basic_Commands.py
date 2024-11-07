import serial
import time

debug = False

# Initialize with default servo positions
servo_data = [45, 0, 180, 45]

if not debug:
    ser = serial.Serial('COM5', 115200)  # Open serial port
# Function to adjust servo angles based on user input
def adjust_servo_data(command):
    global servo_data
    if command == 'down':
        servo_data[2] = min(180, servo_data[2] + 20)  # Increment tilt down
    elif command == 'up':
        servo_data[2] = max(130, servo_data[2] - 20)  # Decrement tilt up
    elif command == 'back':
        servo_data[1] = max(0, servo_data[1] - 20)  # Increment front
    elif command == 'front':
        servo_data[1] = min(75, servo_data[1] + 20)  # Decrement back   
    elif command == 'right':
        servo_data[0] = max(0, servo_data[0] - 20)  # Pan left
    elif command == 'left':
        servo_data[0] = min(180, servo_data[0] + 20)  # Pan right
    elif command == 'open':
        servo_data[3] = 60
    elif command == 'close':
        servo_data[3] = 0       
    print(f"Adjusted servo data: {servo_data}")

while True:
    command = input("Enter command (up, down, front, back, left, right, open, close) or 'q' to quit: ").lower()
    if command == 'q':
        ser.close()  # Close the port after sending data
        break
    elif command in ['up', 'down', 'front', 'back','left', 'right', 'open', 'close']:
        adjust_servo_data(command)
        
        # Send updated servo data to Arduino
        if not debug:
            try:
                
                ser.write(bytearray(servo_data))
                time.sleep(0.2)
                print(f"Sent to serial: {servo_data} , {bytearray(servo_data)}")
                
            except Exception as e:
                print(f"Error sending data to Arduino: {e}")
                ser.close()  # Close the port after sending data
        else:
            print(f"Debug: {servo_data}")
    else:
        print("Invalid command. Please enter 'up', 'down', 'left', or 'right'.")
