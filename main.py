import argparse  # Flag support
import logging  # Disable logs
import socket  # Web support
import sys  # Supress output


import webbrowser  # Launch YouTube TV


import pyautogui  # Control system
from flask import Flask, render_template, request  # Web support

print("Virtual Remote Control")
print("Press Ctrl-C at any time to stop the program.")

# Define and parse command-line arguments
parser = argparse.ArgumentParser(description="Virtual Remote Control")
parser.add_argument("--track", action="store_true", help="Enable tracking mode")
parser.add_argument("--ip", action="store_true", help="Enable IP Viewing mode")
args = parser.parse_args()

# Disable unnecessary logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ANSI Color Codes:
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error: {e}")
        return None


# No Internet connection
if not check_internet():
    print(RED + "An error has occurred. Please check your Internet connection." + RESET)
    input("Press any key to exit...")
    sys.exit(1)

# Call the function to get the local IP address
local_ip = get_local_ip()

# Check if local IP is available
if local_ip is None:
    print(RED + "An error has occurred. Local IP address not found." + RESET)
    input("Press any key to exit...")
    sys.exit(1)

# Initialize web app
app = Flask(__name__)

# Dictionary to track connected users by IP address
connected_users = {}


@app.route('/')
def home():
    return render_template('index.html', remote_ip=request.remote_addr, local_ip=local_ip)


# Define a route to receive AJAX requests from the virtual d-pad on the phone
@app.route('/control', methods=['POST'])
def control():
    # Get the direction sent from the phone
    direction = request.form['direction']

    # Map the direction to corresponding arrow keys
    arrow_keys = {
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right',
        'center': 'enter',
        'volume-up': 'volumeup',
        'volume-down': 'volumedown',
        'mute': 'volumemute',
        'back': 'esc',
        'play-pause': 'playpause',
        'launch': ''
    }

    # Press the corresponding arrow key


    if direction in arrow_keys:
        if direction== 'launch':
            webbrowser.open("https://youtube.com/tv")  # Launch the website.
        else:
            pyautogui.press(arrow_keys[direction])

            remote_ip = request.remote_addr

            # Check if the user is connected and print the message accordingly
            if args.ip:
                if remote_ip not in connected_users:
                    print(f"IP: {remote_ip} has connected")
                    connected_users[remote_ip] = True
            if args.track:
                if remote_ip in connected_users:
                    print(f"IP: {remote_ip} - {direction}")
                else:
                    print(f"IP: {remote_ip} has connected")
                    connected_users[remote_ip] = True

    return ''


port = 8080
if args.track: print(GREEN + "Button tracking is enabled." + RESET)
if args.ip: print(GREEN + "IP logging is enabled." + RESET)
print(GREEN + "Internet is connected." + RESET)
print(GREEN + "Connect to this address from your phone: " + RESET + "http://" + local_ip + ":" + str(port))
app.run(host=local_ip, port=port, debug=False, threaded=True, processes=1)
