import argparse
import logging  
import socket 
import sys
import webbrowser
import pyautogui
from colorama import init, Fore, Style, Back 
from flask import Flask, render_template, request, jsonify
import time

init(autoreset=True)

print(Fore.WHITE + Style.BRIGHT + Back.BLUE + "Virtual Remote Control" + Style.RESET_ALL)
print(Fore.CYAN + "Press Ctrl-C at any time to stop the program." + Style.RESET_ALL)

parser = argparse.ArgumentParser(description="Virtual Remote Control")
parser.add_argument("--track", action="store_true", help="Enable tracking mode")
parser.add_argument("--ip", action="store_true", help="Enable IP Viewing mode")
args = parser.parse_args()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# --- Improved User Counting Logic ---
USER_TIMEOUT_SECONDS = 5 * 60  # e.g., 5 minutes for a user to be considered active

# The global 'connected' dictionary will store IP addresses and their last seen timestamp.
# The global 'connected_users' will store the count of currently active users.
# These are initialized later, before the Flask app routes.

def _update_and_get_active_users_count():
    global connected, connected_users
    current_time = time.time()
    
    # Filter out timed-out users
    active_clients_now = {
        ip: last_seen
        for ip, last_seen in connected.items()
        if (current_time - last_seen) < USER_TIMEOUT_SECONDS
    }
    
    connected = active_clients_now  # Update the global 'connected' dictionary
    connected_users = len(connected)  # Update the global 'connected_users' count
    return connected_users
# --- End of Improved User Counting Logic ---

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


if not check_internet():
    print(Fore.RED + "An error has occurred. Please check your Internet connection." + Style.RESET_ALL)
    input(Fore.YELLOW + "Press any key to exit..." + Style.RESET_ALL)
    sys.exit(1)

local_ip = get_local_ip()
if local_ip is None:
    print(Fore.RED + "An error has occurred. Local IP address not found" + Style.RESET_ALL)
    input(Fore.YELLOW + "Press any key to exit..." + Style.RESET_ALL)
    sys.exit(1)

app = Flask(__name__, static_url_path='', static_folder='templates')

connected = {}  # Stores {'ip_address': last_seen_timestamp}
connected_users = 0 # Stores the count of active users


@app.route('/')
def home():
    global connected # To update client's last_seen time
    # connected_users is updated by _update_and_get_active_users_count

    client_ip = request.remote_addr
    current_time = time.time()

    # Determine if this client was previously active (for logging purposes)
    was_previously_active = False
    if client_ip in connected:
        if (current_time - connected[client_ip]) < USER_TIMEOUT_SECONDS:
            was_previously_active = True
            
    # Record this client's access time
    connected[client_ip] = current_time

    current_active_users_count = _update_and_get_active_users_count()

    if args.ip:
        if not was_previously_active: # Log if new or re-activated after timeout
            print(Fore.GREEN + f"Client connected/re-activated: {client_ip}" + Style.RESET_ALL)
        print(Fore.BLUE + f"Total active users: {current_active_users_count}" + Style.RESET_ALL)
        # For debugging, you can print all active IPs:
        # print(Fore.MAGENTA + f"Active IPs: {list(connected.keys())}" + Style.RESET_ALL)

    return render_template('index.html', remote_ip=client_ip, local_ip=local_ip,
                           connected_users=current_active_users_count, machine_name=socket.gethostname())


@app.route('/get_connected_users')
def get_connected_users():
    # Ensure the count is up-to-date by cleaning up timed-out users
    current_active_users_count = _update_and_get_active_users_count()
    return jsonify(connected_users=current_active_users_count)


@app.route('/control', methods=['POST'])
def control():
    direction = request.form['direction']

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

    global connected_users
    if direction in arrow_keys:
        if direction == 'launch':
            webbrowser.open("https://youtube.com/tv")
        else:
            pyautogui.press(arrow_keys[direction])

            remote_ip = request.remote_addr

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
