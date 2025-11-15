# Chat Loading Issue - Troubleshooting Guide

## Symptoms
- Chat message shows "loading" but never gets a response
- No error message appears
- Backend seems to be processing but frontend doesn't receive response

## Debugging Steps

### 1. Check Browser Console
Open browser DevTools (F12) and check the Console tab. You should see:
- `[API] POST /chat` - Request being sent
- `[API] Response from /chat` - Response received (if successful)
- `[API] Error from /chat` - Error details (if failed)

### 2. Check Backend Terminal
Look at your backend terminal where uvicorn is running. You should see:
- `INFO: Incoming request: POST http://0.0.0.0:8000/chat`
- `INFO: Headers: {...}`
- `INFO: Response status: 200` (or error)

### 3. Check Network Tab
In browser DevTools → Network tab:
- Find the `/chat` request
- Check Status code (200 = success, 4xx/5xx = error)
- Check Response tab to see what the backend returned
- Check Timing to see if request is hanging

### 4. Common Issues and Solutions

#### Issue: Request Timeout
**Symptoms**: Request shows as "pending" for 30+ seconds, then fails
**Solution**: 
- Check if emotion model is loading correctly
- Verify backend logs show the request is being processed
- Increase timeout in `frontend/src/lib/api.ts` if needed

#### Issue: CORS Error
**Symptoms**: Console shows CORS error
**Solution**: 
- Verify backend has CORS middleware (already configured)
- Check backend is running on `0.0.0.0` not just `127.0.0.1`
- Verify frontend URL matches CORS allowed origins

#### Issue: Authentication Error
**Symptoms**: 401 Unauthorized in console
**Solution**:
- Check token is stored: `localStorage.getItem('pai-mhc-token')`
- Try logging out and logging back in
- Verify token hasn't expired

#### Issue: Backend Error
**Symptoms**: Backend logs show error, frontend shows loading
**Solution**:
- Check backend terminal for Python errors
- Common issues:
  - Emotion model not loading (check `backend/models/` directory)
  - MongoDB connection issues
  - Missing dependencies

#### Issue: Emotion Model Loading
**Symptoms**: Backend hangs on `predict_emotions()` call
**Solution**:
- Check if model files exist:
  - `backend/models/emotion_lstm_model.h5`
  - `backend/models/tokenizer.pkl`
  - `backend/models/mlb.pkl`
- If missing, run training script or use fallback emotion detection

### 5. Quick Test

Test the backend directly:
```bash
# Get token first
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@pai.com", "password": "123456"}'

# Use token to test chat
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel sad", "subject_id": "S10"}'
```

If this works, the issue is in the frontend. If it hangs, the issue is in the backend.

### 6. Enable More Logging

The frontend now logs:
- All API requests with data
- All API responses
- Detailed error information

The backend logs:
- All incoming requests
- Request headers
- Response status
- Any errors with full stack trace

### 7. Check Emotion Model

The emotion prediction might be slow. Check backend logs for:
```
❌ Error loading model or tokenizer: ...
```

If you see this, the model isn't loading and the fallback should be used, but it might cause delays.

## Next Steps

1. **Check browser console** - Look for the `[API]` logs
2. **Check backend terminal** - Look for request logs
3. **Check Network tab** - See the actual HTTP request/response
4. **Share the logs** - The console output will help identify the exact issue

