import asyncio
import websockets
import json
import pyautogui

# Disable PyAutoGUI fail-safe if you want to move to corners 
# (Warning: Keep True if you want to stop the script by slamming mouse to a corner)
pyautogui.FAILSAFE = True

async def handler(websocket):
    print(f"Client connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                cmd = data.get('type')
                
                # KEYBOARD EVENTS
                if cmd == 'keydown':
                    key = data.get('key')
                    if key:
                        pyautogui.keyDown(key)
                
                elif cmd == 'keyup':
                    key = data.get('key')
                    if key:
                        pyautogui.keyUp(key)
                
                # MOUSE MOVEMENT (Relative)
                elif cmd == 'mousemove':
                    x = data.get('x', 0)
                    y = data.get('y', 0)
                    pyautogui.moveRel(x, y)
                
                # MOUSE CLICK
                elif cmd == 'click':
                    button = data.get('button', 'left')
                    pyautogui.click(button=button)

            except Exception as e:
                print(f"Error processing command: {e}")

    except websockets.ConnectionClosed:
        print("Client disconnected.")

async def main():
    # "0.0.0.0" allows connections from any device on your local network
    # Ensure port 8765 is open in your Windows/OS firewall
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("--- RGB WiFi Keyboard Server ---")
        print("Status: Active")
        print("Listening on: Port 8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user.")