# Frontend Integration Guide

## Overview
The React + TypeScript frontend has been integrated with the PAI-MHC backend API. All pages and API calls have been updated to match the backend endpoints.

## Changes Made

### 1. API Client (`frontend/src/lib/api.ts`)
- ✅ Updated login to use JSON with `email` and `password` (not FormData)
- ✅ Updated `ChatResponse` interface to match backend structure
- ✅ Updated `WellnessResponse` interface to match backend structure
- ✅ Updated chat history endpoint to `/history` (no subject_id in path)
- ✅ Updated recommendations endpoint to use query parameters

### 2. Login Page (`frontend/src/pages/Login.tsx`)
- ✅ Changed from `username` to `email` field
- ✅ Pre-filled with demo credentials: `test@pai.com` / `123456`
- ✅ Updated to use JSON login request
- ✅ Default subject ID set to `S10`

### 3. Chat Page (`frontend/src/pages/Chat.tsx`)
- ✅ Updated to handle new response format (`text` instead of `response`)
- ✅ Updated emotion field mapping (`emotion` instead of `detected_emotion`)
- ✅ Updated probability field mapping (`probability` instead of `emotion_probability`)
- ✅ Added recommendations toast notification
- ✅ Added crisis escalation alert
- ✅ Updated history loading to use new endpoint

### 4. Wellness Page (`frontend/src/pages/Wellness.tsx`)
- ✅ Updated to handle backend response format
- ✅ Added status to emotion mapping
- ✅ Added features display section
- ✅ Handles null PWI values gracefully

### 5. Recommendations Page (`frontend/src/pages/Recommendations.tsx`)
- ✅ Updated to fetch recommendations from backend API
- ✅ Converts API response to display format
- ✅ Falls back to default recommendations if API fails

## API Endpoints Used

### Authentication
- `POST /login` - Login with email/password
  ```json
  {
    "email": "test@pai.com",
    "password": "123456"
  }
  ```

### Chat
- `POST /chat` - Send chat message
  ```json
  {
    "text": "I'm feeling sad",
    "subject_id": "S10"
  }
  ```
- `GET /history` - Get chat history (requires auth token)

### Wellness
- `GET /wellness/{subject_id}` - Get wellness data
- `GET /recommendations?emotion={emotion}&wellness_status={status}` - Get recommendations

## Environment Configuration

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

For production, update with your backend URL.

## Running the Frontend

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API URL
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

## Testing the Integration

1. **Start the backend:**
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test flow:**
   - Navigate to `http://localhost:5173` (or your Vite port)
   - Login with `test@pai.com` / `123456`
   - Send a chat message
   - Check wellness dashboard
   - View recommendations

## Features

### ✅ Working Features
- JWT authentication with token storage
- Real-time chat with emotion detection
- Wellness dashboard with PWI scores
- Personalized recommendations
- Chat history loading
- Crisis detection alerts
- Recommendations notifications

### 🔄 Data Flow
1. User logs in → Gets JWT token
2. Token stored in localStorage
3. All API requests include token in Authorization header
4. Chat messages trigger emotion detection + wellness check
5. Recommendations generated based on emotion + wellness
6. All data persisted in MongoDB via backend

## Troubleshooting

### CORS Issues
- Ensure backend has CORS middleware configured (already done)
- Check that backend is running on the correct host (`0.0.0.0` for network access)

### Authentication Issues
- Verify token is stored in localStorage: `localStorage.getItem('pai-mhc-token')`
- Check browser console for API errors
- Verify backend is running and accessible

### API Connection Issues
- Check `.env` file has correct `VITE_API_BASE_URL`
- Verify backend is running: `http://localhost:8000/docs`
- Check browser network tab for failed requests

## Next Steps

1. Add emotion-based recommendation fetching (use latest chat emotion)
2. Add PWI trend chart (requires historical data endpoint)
3. Add real-time wellness updates
4. Add notification system for crisis detection
5. Add user profile management

