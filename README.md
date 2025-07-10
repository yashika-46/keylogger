# keylogger
# Stealth Keylogger

A background keylogger for advanced monitoring and security auditing. Runs silently, logs keystrokes, and supports encrypted log files and stealth features.

## Features
- **Stealth Operation:** Runs in the background with minimal user visibility
- **Encrypted Logging:** Stores keystrokes in encrypted files for security
- **Log Rotation:** Automatically rotates logs when they reach a configurable size
- **Configurable:** All settings (log file, encryption, intervals, etc.) are customizable via a config file
- **Cross-platform:** Works on Windows, Linux, and macOS (with Python 3)
- **Remote Monitoring Ready:** (Optional) Can be extended for remote log upload

## Installation

1. **Clone or copy the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   (See `requirements.txt` for details)

   Or install manually:

```bash
pip install pynput==1.7.6
pip install tkinter-tooltip==2.0.0
pip install psutil==5.9.5
pip install cryptography==41.0.7
pip install pyperclip==1.8.2

## Usage

### 1. Create a configuration file (optional)
You can generate a default config file by running:
```bash
python stealth_keylogger.py --config
```
This creates `stealth_config.json` with default settings. You can edit this file to customize log file names, encryption, log rotation, and more.

### 2. Run the keylogger
```bash
python stealth_keylogger.py
```
- The keylogger will start in stealth mode, logging keystrokes to the files specified in the config.
- To stop, press `Ctrl+C` in the terminal where it was started.

### 3. Command-line options
- `--config` : Generate a default configuration file
- `--help`   : Show usage instructions

## Configuration
The `stealth_config.json` file supports the following options:
- `log_file`: Name of the plain text log file (default: `system.log`)
- `encrypted_log`: Name of the encrypted log file (default: `system.enc`)
- `log_interval`: How often to log system info (in seconds)
- `hide_process`: Attempt to hide the process (Windows only)
- `encrypt_logs`: Whether to encrypt logs
- `remote_monitoring`: Enable remote log upload (not implemented by default)
- `auto_start`: Enable auto-start on boot (not implemented by default)
- `max_log_size`: Maximum log file size in bytes before rotation (default: 10MB)
- `rotation_enabled`: Enable log rotation

## Log Files
- **Plain text log:** Human-readable keystroke logs
- **Encrypted log:** Keystrokes stored securely (requires the generated key file to decrypt)
- **Key file:** `stealth.key` is generated automatically for encryption/decryption

## Security & Legal Notice
- **Authorization Required:** Only use this tool on systems you own or have explicit permission to monitor.
- **Privacy:** This tool captures sensitive data. Use responsibly and store logs securely.
- **Encryption:** Encrypted logs help protect sensitive data from unauthorized access.
- **Compliance:** Ensure you comply with all applicable laws and regulations regarding monitoring and data collection.

## Troubleshooting
- **Permission errors:** Run as administrator/root if needed, especially on Windows.
- **Antivirus warnings:** Some security software may flag keyloggers as malicious.
- **No logs created:** Check config file paths and permissions.

## Extending Functionality
- **Remote monitoring:** Add code to upload logs to a server or cloud storage.
- **Auto-start:** Implement OS-specific auto-start (e.g., registry on Windows, systemd on Linux).
- **Custom triggers:** Add logic to start/stop logging based on user activity or schedules.

## Disclaimer
This software is for educational and authorized security auditing purposes only. The authors are not responsible for misuse or illegal use of this tool. 
