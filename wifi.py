import subprocess
import ctypes
import logging
import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal
import keyboard
import tempfile
import webbrowser

# Configure logging
logging.basicConfig(
    filename="wifi_toggle.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class WifiTrayApp(QObject):
    wifi_toggled = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.tray_icon = QSystemTrayIcon(self)
        self.setup_tray()
        
        # Add hotkey registration
        keyboard.add_hotkey('ctrl+alt+w', self.on_hotkey_pressed)
        
        # Check admin privileges
        if not is_admin():
            self.show_notification("Admin Rights Required", "Rerunning with admin privileges...")
            rerun_as_admin()
    
    def open_developer_url(self):
        webbrowser.open("https://www.bibekchandsah.com.np")
        
    def setup_tray(self):
        # Create the tray icon with fallback
        self.tray_icon.setIcon(QIcon.fromTheme('network-wireless',
                             QIcon(self.get_icon_path())))
        
        # Create the context menu
        menu = QMenu()
            
        self.toggle_action = menu.addAction("Turn Wi-Fi OFF" if self.is_wifi_enabled() else "Turn Wi-Fi ON")
        self.toggle_action.triggered.connect(self.on_toggle_wifi)
        
        # Add developer menu item
        menu.addSeparator()
        developer_action = menu.addAction("Developer")
        developer_action.triggered.connect(self.open_developer_url)
        
        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.quit_app)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        shortcut = "Ctrl+Alt+W"
        self.tray_icon.setToolTip(f"Wi-Fi Tray Controller\n{shortcut}")
        
        # Connect notifications
        self.wifi_toggled.connect(self.update_tray_icon)
        
    def get_icon_path(self, wifi_on=True):
        # Try PyInstaller temp directory first
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_name = "wifi_on.ico" if wifi_on else "wifi_off.ico"
        icon_path = os.path.join(base_path, icon_name)
        
        # If not found in MEIPASS, try current directory
        if not os.path.exists(icon_path):
            local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), icon_name)
            if os.path.exists(local_path):
                return local_path
        
        # If still not found, create temp file with embedded icon
        if not os.path.exists(icon_path):
            from io import BytesIO
            import base64
            
            # Add the base64 encoded icons back
            WIFI_ON_ICON = base64.b64decode("""...""")  # Your base64 string here
            WIFI_OFF_ICON = base64.b64decode("""...""")  # Your base64 string here
            
            temp_dir = tempfile.gettempdir()
            icon_path = os.path.join(temp_dir, icon_name)
            with open(icon_path, 'wb') as f:
                f.write(WIFI_ON_ICON if wifi_on else WIFI_OFF_ICON)
        
        return icon_path
    
    def update_tray_icon(self, status):
        self.tray_icon.setIcon(QIcon(self.get_icon_path(status)))
        self.toggle_action.setText("Turn Wi-Fi OFF" if status else "Turn Wi-Fi ON")
    
    def show_notification(self, title, message):
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 2000)
    
    def on_toggle_wifi(self):
        current_state = self.is_wifi_enabled()
        try:
            toggle_wifi(enable=not current_state)
            new_state = not current_state
            self.wifi_toggled.emit(new_state)
            self.show_notification(
                "Wi-Fi Status Changed",
                f"Wi-Fi has been turned {'ON' if new_state else 'OFF'}"
            )
        except Exception as e:
            self.show_notification("Error", f"Failed to toggle Wi-Fi: {str(e)}")
            logging.error(f"Toggle error: {e}")
    
    def on_hotkey_pressed(self):
        """Handle the Ctrl+Alt+W hotkey press"""
        current_state = self.is_wifi_enabled()
        try:
            success = toggle_wifi(enable=not current_state)
            if success:
                new_state = not current_state
                self.wifi_toggled.emit(new_state)
                self.show_notification(
                    "Wi-Fi Toggled",
                    f"Wi-Fi turned {'ON' if new_state else 'OFF'} via hotkey"
                )
        except Exception as e:
            self.show_notification("Hotkey Error", f"Failed to toggle Wi-Fi: {str(e)}")
            logging.error(f"Hotkey toggle error: {e}")
    
    def is_wifi_enabled(self):
        adapter_name = get_wifi_adapter_name()
        result = subprocess.run(
            f"netsh interface show interface {adapter_name}",
            shell=True,
            capture_output=True,
            text=True
        )
        return "Enabled" in result.stdout
    
    def quit_app(self):
        keyboard.unhook_all()  # Clean up hotkey registration
        self.tray_icon.hide()
        self.app.quit()
    
    def run(self):
        self.app.exec_()

def is_admin():
    """
    Checks if the script is running with administrative privileges.
    
    Returns:
        bool: True if running as admin, False otherwise.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(f"Failed to check admin privileges: {e}")
        return False

def rerun_as_admin():
    """
    Reruns the script with administrative privileges.
    """
    try:
        # Get the full path of the current script
        script_path = os.path.abspath(sys.argv[0])

        # Use ShellExecute to rerun the script as an administrator
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}"', None, 1)
        logging.info("Script rerun with admin privileges.")
        sys.exit(0)  # Exit the current non-admin instance
    except Exception as e:
        logging.error(f"Failed to rerun script with admin privileges: {e}")
        print("Failed to rerun the script with admin privileges. Please run it manually as an administrator.")
        sys.exit(1)

def get_wifi_adapter_name():
    """
    Retrieves the name of the Wi-Fi adapter dynamically.
    
    Returns:
        str: The name of the Wi-Fi adapter, or None if not found.
    """
    try:
        result = subprocess.run("netsh interface show interface", shell=True, capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "Wi-Fi" in line or "Wireless" in line:
                adapter_name = line.split()[-1]  # Extract the adapter name
                logging.info(f"Detected Wi-Fi adapter: {adapter_name}")
                return adapter_name
        logging.error("Wi-Fi adapter not found.")
        print("Wi-Fi adapter not found. Please check your network settings.")
        return None
    except Exception as e:
        logging.error(f"Failed to retrieve Wi-Fi adapter name: {e}")
        print(f"Failed to retrieve Wi-Fi adapter name: {e}")
        return None

def toggle_wifi(enable=True):
    """
    Toggles the Wi-Fi state on or off.
    
    Args:
        enable (bool): True to turn Wi-Fi on, False to turn it off.
    """
    adapter_name = get_wifi_adapter_name()
    if not adapter_name:
        return False

    state = "enable" if enable else "disable"
    try:
        subprocess.run(f"netsh interface set interface {adapter_name} admin={state}", 
                      shell=True, check=True)
        logging.info(f"Wi-Fi turned {'on' if enable else 'off'}.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to toggle Wi-Fi: {e}")
        return False

def main():
    # Remove old text-based menu and replace with GUI
    app = WifiTrayApp()
    app.run()

if __name__ == "__main__":
    main()