import argparse  # Flag support
import logging  # Disable logs
import socket  # Web support
import sys  # Supress output
import webbrowser  # Launch YouTube TV

import pyautogui  # Control system
from colorama import init, Fore, Style, Back  # Text color support
from flask import Flask, render_template, request, jsonify  # Web support

# Initialize colorama (only required once)
init(autoreset=True)

print(Fore.WHITE + Style.BRIGHT + Back.BLUE + "Virtual Remote Control" + Style.RESET_ALL)
print(Fore.CYAN + "Press Ctrl-C at any time to stop the program." + Style.RESET_ALL)

# Define and parse command-line arguments
parser = argparse.ArgumentParser(description="Virtual Remote Control")
parser.add_argument("--track", action="store_true", help="Enable tracking mode")
parser.add_argument("--ip", action="store_true", help="Enable IP Viewing mode")
args = parser.parse_args()

# Disable unnecessary logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


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
    print(Fore.RED + "An error has occurred. Please check your Internet connection." + Style.RESET_ALL)
    input(Fore.YELLOW + "Press any key to exit..." + Style.RESET_ALL)
    sys.exit(1)

# Call the function to get the local IP address
local_ip = get_local_ip()

# Check if local IP is available
if local_ip is None:
    print(Fore.RED + "An error has occurred. Local IP address not found" + Style.RESET_ALL)
    input(Fore.YELLOW + "Press any key to exit..." + Style.RESET_ALL)
    sys.exit(1)

# Initialize web app
app = Flask(__name__)

# Dictionary to track connected users by IP address
connected = {}

# Count connected users so far (not active users)
connected_users = 0


@app.route('/')
def home():
    return render_template('index.html', remote_ip=request.remote_addr, local_ip=local_ip,
                           connected_users=connected_users, machine_name=socket.gethostname())


@app.route('/get_connected_users')
def get_connected_users():
    # Replace this with the actual logic to calculate connected_users
    return jsonify(connected_users=connected_users)


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
    global connected_users
    if direction in arrow_keys:
        if direction == 'launch':
            webbrowser.open("https://youtube.com/tv")  # Launch the website.
        else:
            pyautogui.press(arrow_keys[direction])

            remote_ip = request.remote_addr

            # Check if the user is connected and print the message accordingly
            if args.ip:
                if remote_ip not in connected:
                    print(f"IP: {remote_ip} has connected")
                    connected[remote_ip] = True
                    connected_users += 1
            if args.track:
                if remote_ip in connected:
                    print(f"IP: {remote_ip} - {direction}")
                else:
                    print(f"IP: {remote_ip} has connected")
                    connected[remote_ip] = True
                    connected_users += 1
            else:
                if remote_ip not in connected:
                    connected[remote_ip] = True
                    connected_users += 1
    return ''


port = 8080
if args.track: print(Fore.GREEN + "Button tracking is enabled." + Style.RESET_ALL)
if args.ip: print(Fore.GREEN + "IP logging is enabled." + Style.RESET_ALL)
print(Fore.GREEN + "Internet is connected." + Style.RESET_ALL)
print(
    Fore.GREEN + "Connect to this address from your phone: " + Style.RESET_ALL + "http://" + local_ip + ":" + str(port))
app.run(host=local_ip, port=port, debug=False, threaded=True, processes=1)
