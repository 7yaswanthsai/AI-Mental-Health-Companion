# Troubleshooting Mobile App Connection Issues

## Problem: "Cannot connect to server" Error

### Step 1: Verify Backend is Running

Check if the backend is running:
```powershell
# Windows
netstat -an | findstr :8000

# Should show something like:
# TCP    0.0.0.0:8000         0.0.0.0:0              LISTENING
```

### Step 2: Restart Backend with Correct Host Binding

**The backend MUST be bound to `0.0.0.0` (not just `127.0.0.1`) for mobile emulators to access it:**

```powershell
# Stop current server (Ctrl+C)
# Then restart with:
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Why `0.0.0.0`?**
- `127.0.0.1` only accepts connections from localhost
- `0.0.0.0` accepts connections from all network interfaces
- Android emulator's `10.0.2.2` needs the server to be accessible on the network interface

### Step 3: Test Backend Accessibility

**From your computer:**
```powershell
# Test local access
Invoke-WebRequest -Uri http://127.0.0.1:8000/docs -UseBasicParsing

# Test network access (should work if bound to 0.0.0.0)
Invoke-WebRequest -Uri http://localhost:8000/docs -UseBasicParsing
```

**From Android Emulator:**
1. Open browser in emulator
2. Navigate to: `http://10.0.2.2:8000/docs`
3. Should see FastAPI docs page

### Step 4: Check Firewall

Windows Firewall might be blocking port 8000:

```powershell
# Check firewall rules
netsh advfirewall firewall show rule name=all | findstr 8000

# If needed, allow port 8000 (run as Administrator)
netsh advfirewall firewall add rule name="PAI-MHC Backend" dir=in action=allow protocol=TCP localport=8000
```

### Step 5: Verify CORS is Configured

Make sure `backend/main.py` has CORS middleware (already added):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 6: Check Mobile App Configuration

Verify the mobile app is using the correct URL:
- Android Emulator: `http://10.0.2.2:8000`
- iOS Simulator: `http://localhost:8000`
- Physical Device: Your computer's IP (e.g., `http://192.168.1.100:8000`)

Check console logs in Expo:
```
[API Client] Using base URL: http://10.0.2.2:8000
```

### Step 7: Test with curl/Postman

Test the login endpoint directly:
```powershell
# From your computer
$body = @{email="test@pai.com"; password="123456"} | ConvertTo-Json
Invoke-WebRequest -Uri http://127.0.0.1:8000/login -Method POST -Body $body -ContentType "application/json"
```

### Common Issues and Solutions

**Issue: "Network Error" or "ECONNREFUSED"**
- ✅ Backend not running → Start it
- ✅ Backend bound to 127.0.0.1 only → Use `--host 0.0.0.0`
- ✅ Firewall blocking → Allow port 8000
- ✅ Wrong URL in app → Check console logs

**Issue: "CORS Error"**
- ✅ CORS middleware not added → Already fixed in main.py
- ✅ Backend not restarted → Restart after adding CORS

**Issue: "Timeout"**
- ✅ Backend too slow → Check backend logs
- ✅ Network issues → Try physical device on same WiFi

**Issue: Works on computer but not emulator**
- ✅ Backend bound to 127.0.0.1 → Change to 0.0.0.0
- ✅ Firewall blocking → Allow port 8000

### Quick Fix Script

Use the provided startup script:
```powershell
# Windows
.\backend\start_server.bat

# Or manually:
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Checklist

- [ ] Backend is running (`netstat` shows port 8000 listening)
- [ ] Backend is bound to `0.0.0.0` (not just `127.0.0.1`)
- [ ] Can access `http://127.0.0.1:8000/docs` from browser
- [ ] Can access `http://10.0.2.2:8000/docs` from Android emulator browser
- [ ] CORS middleware is configured
- [ ] Firewall allows port 8000
- [ ] Mobile app shows correct base URL in console
- [ ] Backend logs show incoming requests when mobile app tries to connect

### Still Not Working?

1. **Check backend logs** - Do you see the request coming in?
2. **Check mobile app logs** - What exact error is shown?
3. **Try physical device** - Use your computer's local IP instead
4. **Check network** - Ensure emulator and computer are on same network (for physical devices)

