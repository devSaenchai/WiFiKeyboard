import subprocess
import sys


# 1. Automatic Dependency Check & Installation
def install_dependencies():
    required = {"websockets", "pyautogui"}
    installed = set()

    # Check installed packages
    try:
        import pkg_resources

        installed = {pkg.key for pkg in pkg_resources.working_set}
    except ImportError:
        # Fallback for Python 3.11+ standard library
        import importlib.metadata

        installed = {
            dist.metadata["Name"].lower()
            for dist in importlib.metadata.distributions()
        }

    missing = required - installed
    if missing:
        print(f"Missing packages detected: {missing}. Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing]
        )


install_dependencies()

import asyncio
import json
import socket
import pyautogui
import websockets

# Disable default 0.1s delay between actions to eliminate lag
pyautogui.PAUSE = 0.0

KEY_MAP = {
    " ": "space",
    "ArrowUp": "up",
    "ArrowDown": "down",
    "ArrowLeft": "left",
    "ArrowRight": "right",
    "Control": "ctrl",
    "Escape": "escape",
    "Backspace": "backspace",
    "Enter": "enter",
}


# 2. Get Local IP Address
def get_local_ip():
    """Attempts to find the actual LAN IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually connect, but forces OS to pick the active network interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def process_command(data):
    cmd = data.get("type")

    if cmd == "keydown":
        key = data.get("key")
        if key:
            mapped_key = KEY_MAP.get(key, key.lower())
            pyautogui.keyDown(mapped_key)

    elif cmd == "keyup":
        key = data.get("key")
        if key:
            mapped_key = KEY_MAP.get(key, key.lower())
            pyautogui.keyUp(mapped_key)

    elif cmd == "mousemove":
        dx = data.get("x", 0)
        dy = data.get("y", 0)
        pyautogui.moveRel(dx, dy, _pause=False)

    elif cmd == "click":
        button = data.get("button", "left")
        pyautogui.click(button=button)


async def handler(websocket):
    print(f"Client connected from {websocket.remote_address}")
    loop = asyncio.get_running_loop()

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await loop.run_in_executor(None, process_command, data)
            except Exception as e:
                print(f"Error processing command: {e}")

    except websockets.ConnectionClosed:
        print("Client disconnected.")


async def main():
    port = 8765
    local_ip = get_local_ip()

    async with websockets.serve(handler, "0.0.0.0", port):
        print("\n==========================================")
        print("         WiFi Keyboard Server             ")
        print("==========================================")
        print(f" Status: Active")
        print(f" Local IP:  {local_ip}")
        print(f" Port:      {port}")
        print(f" Connect via: ws://{local_ip}:{port}")
        print("==========================================\n")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
