# Virtual Remote Control
Virtual Remote Control allows your phone or any other devices from your local network to connect and control the target computer using Flask.\
Useful for [Kodi](https://kodi.tv/) or [Youtube TV*](https://www.youtube.com/tv).\
\
**For Youtube TV on your web browser, [install this extension](https://chrome.google.com/webstore/detail/youtube-for-tv-4k/pdpkefmdjkgijhnhjkblpielhiikadbb).*

# Features
- No installation required on remote device.
- D-Pad with responsive controls.
- Supports dark mode.
- Includes basic media control keys (Volume controls, Play/Pause functions).
- Convenient Youtube TV launch button.
- Shows IP address in the remote device.
- Track which buttons were pressed from which IP address using ``--track`` flag.
- Log IP connections using ``--ip`` flag.

# Wishlist
- Keyboard and mouse input, clipboard support (may exist as a future repo)
- Extra media metadata informations.

# Using the program
- Download the latest version from the ``Releases`` page.
- Check your Internet connection and Firewall settings from both your remote and target devices and enter the IP (Website) appears in the terminal.

# Using the source code
Download the source code and open the project using your desired environment.\
Build using ``build.bat`` and enter the version number.\
Make sure to install all the required Python libraries:
``argparse``, ``logging``, ``socket``, ``webbrowser``, ``pyautogui``, ``flask``
