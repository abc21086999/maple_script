from pynput import keyboard
import time

class KeyLogger:
    def __init__(self):
        self.listener = None
        self.events = []
        self.start_time = None

    def _key_to_str(self, key):
        """Helper to convert pynput key objects to strings."""
        if hasattr(key, 'name'):
            return key.name
        if hasattr(key, 'char'):
            return key.char
        return None

    def on_press(self, key):
        if self.start_time is None:
            return
        elapsed_time = round(time.time() - self.start_time, 2)
        key_str = self._key_to_str(key)
        if key_str:
            self.events.append(('press', key_str, elapsed_time))

    def on_release(self, key):
        if self.start_time is None:
            return
        elapsed_time = round(time.time() - self.start_time, 2)
        key_str = self._key_to_str(key)
        if key_str:
            self.events.append(('release', key_str, elapsed_time))
        
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def start(self):
        self.events = []
        self.start_time = time.time()
        self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release)
        self.listener.start()
        self.listener.join() # This will block until the listener is stopped
        return self.events


if __name__ == '__main__':
    print("Starting keylogger. Press ESC to stop.")
    key_logger = KeyLogger()
    recorded_events = key_logger.start()
    print("\nRecording stopped. Here are the recorded events:")
    print(recorded_events)