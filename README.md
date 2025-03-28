# Wi-Fi Tray Controller

A system tray utility for Windows to quickly toggle Wi-Fi status with hotkey support and visual notifications.

## Features

- 🖱️ System tray interface with status indicator
- 🔑 Hotkey support (Ctrl+Alt+W)
- 📢 Desktop notifications for status changes
- 🛡️ Automatic admin privilege elevation
- 🔄 Real-time status updates
- 👨💻 Developer info menu
- 🎨 Custom icons with fallback support
- 📊 Logging for troubleshooting

## Installation

1. **Requirements**:
   - Python 3.6+
   - Windows 10/11

2. **Install dependencies**:
   ```bash
   pip install pyqt5 keyboard
   ```

3. **Download**:
   - <a href="https://github.com/bebedudu/toggle/releases/">Download program</a>
   - Clone repository or download `wifi.py`
   - Optional: Add `wifi_on.ico` and `wifi_off.ico` to the directory

## Usage

1. **Run the application**:
   ```bash
   python wifi.py
   ```
   *Note: Will automatically request admin privileges*

2. **System tray controls**:
   - Left-click tray icon to:
     - Turn Wi-Fi On/Off
     - Open developer website
     - Exit application
   - Right-click for context menu

3. **Hotkey**:
   - Press `Ctrl+Alt+W` to toggle Wi-Fi state

## Compilation (Optional)

Create standalone executable with PyInstaller:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build executable:
   ```bash
   pyinstaller --noconsole --onefile --add-data "wifi_on.ico;." --add-data "wifi_off.ico;." wifi.py
   ```

3. Find executable in `dist/` directory

## Notes

- First run may trigger Windows SmartScreen - select "More info" > "Run anyway"
- Icons will automatically generate if missing
- Logs are stored in `wifi_toggle.log`

## Developer Info

- Developer: Bibek Chand Sah
- Website: [https://www.bibekchandsah.com.np](https://www.bibekchondsah.com.np)
- Accessible via "Developer" menu item in tray 
