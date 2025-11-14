# API Configuration Guide

## Network Setup for Mobile App

The mobile app needs to connect to your backend server. The configuration depends on how you're running the app:

### Android Emulator
- **Default**: Uses `http://10.0.2.2:8000` (automatically configured)
- This is a special IP that Android emulator uses to access your host machine

### iOS Simulator
- **Default**: Uses `http://localhost:8000` (automatically configured)
- Works out of the box with iOS simulator

### Physical Devices (Android/iOS)
You need to use your computer's local IP address instead of `127.0.0.1`.

**To find your local IP:**

**Windows:**
```powershell
ipconfig
# Look for "IPv4 Address" under your active network adapter (usually starts with 192.168.x.x)
```

**Mac/Linux:**
```bash
ifconfig | grep "inet "
# Or
ip addr show
# Look for your local network IP (usually 192.168.x.x or 10.x.x.x)
```

**Then update `app.json`:**
```json
{
  "expo": {
    "extra": {
      "apiBaseUrl": "http://192.168.1.100:8000"
    }
  }
}
```
Replace `192.168.1.100` with your actual IP address.

### Backend Server Configuration

Make sure your backend is accessible:

1. **For Android emulator/iOS simulator** (default):
   ```bash
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **For physical devices** (use your local IP):
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Or specify your IP:
   ```bash
   python -m uvicorn backend.main:app --reload --host 192.168.1.100 --port 8000
   ```

### Troubleshooting

**Network Error:**
- ✅ Check that backend is running
- ✅ Verify the IP address is correct
- ✅ Make sure phone/emulator and computer are on the same network (for physical devices)
- ✅ Check firewall isn't blocking port 8000
- ✅ Try accessing `http://YOUR_IP:8000/docs` in a browser on your device

**Connection Refused:**
- Make sure backend is bound to `0.0.0.0` (not just `127.0.0.1`) when using physical devices
- Check that port 8000 is not blocked by firewall

**Still having issues?**
- Check the console logs in Expo - it will show which URL is being used
- Try using `http://localhost:8000` in iOS simulator
- For Android, ensure you're using `10.0.2.2:8000` in emulator

