# Backend Upgrade Summary

## Overview

The backend has been completely rewritten and upgraded to support a more empathetic, ChatGPT-like mental health companion chatbot with user registration.

## Key Changes

### 1. User Registration System
- **New Endpoint:** `POST /register`
- **Fields:** name, email, password, subject_id (optional)
- **Password Hashing:** bcrypt
- **MongoDB Storage:** Users stored in `users` collection
- **Auto-generated Subject IDs:** Format S#### (e.g., S1001, S1002)

### 2. Empathy Engine Rewrite
- **Exact Behavioral Rules:** Implemented all 12 behavioral rules as specified
- **Greeting Handling:** "Hi, it's good to hear from you. How are you feeling today?"
- **Emotion-Specific Responses:** Sadness, anger, fear, stress, joy, neutral
- **Follow-up Questions:** Every response includes a follow-up question
- **Health Query Support:** Detects chest pain, dizziness, headache, etc.
- **No Wearable Messages:** Wellness data stored internally, never shown in chat

### 3. Safety Guard Enhancement
- **Stronger Crisis Detection:** Enhanced keyword patterns
- **Exact Crisis Response:** Uses specified emergency message with India helpline numbers
- **No Recommendations in Crisis:** Recommendations disabled during crisis mode

### 4. Relevance Checker Expansion
- **Irrelevant Question Detection:** Math, coding, politics, knowledge questions
- **Greeting Allowance:** Greetings and conversational phrases allowed
- **Pattern Matching:** Regex patterns for arithmetic, programming, etc.

### 5. Chat Response Changes
- **No Wearable References:** Chat responses never mention "wearable", "PWI", "health score"
- **Wellness Data Internal Only:** Stored in database, available via `/wellness/{subject_id}` endpoint
- **Pure Empathetic Text:** Chat responses are purely supportive and empathetic

## New Files Created

1. **`backend/utils/password_hasher.py`**
   - bcrypt password hashing wrapper
   - `hash_password()` and `verify_password()` functions

2. **`docs/FRONTEND_SIGNUP_INTEGRATION.md`**
   - Complete frontend integration guide
   - React and React Native examples
   - API documentation

## Updated Files

1. **`backend/main.py`**
   - Added `POST /register` endpoint
   - Updated chat endpoint to use new empathy engine
   - Removed wearable messages from chat responses
   - Enhanced error handling

2. **`backend/auth.py`**
   - Complete rewrite with MongoDB user storage
   - Registration function with duplicate email check
   - Subject ID auto-generation
   - Updated authentication to use MongoDB

3. **`backend/empathy_engine.py`**
   - Complete rewrite with exact behavioral rules
   - Emotion-specific response templates
   - Greeting detection and responses
   - Health query handling
   - Follow-up question generation

4. **`backend/safety_guard.py`**
   - Enhanced crisis detection patterns
   - Exact crisis response as specified
   - Stronger keyword matching

5. **`backend/relevance_checker.py`**
   - Expanded irrelevant question detection
   - Pattern matching for math, coding, politics
   - Greeting allowance

## Behavioral Rules Implemented

1. ✅ **Greetings:** "Hi, it's good to hear from you. How are you feeling today?"
2. ✅ **Neutral:** "Thanks for sharing. Sometimes being neutral can hide deeper feelings. How has your day been so far?"
3. ✅ **Joyful:** "That's wonderful to hear! What's making you feel happy today?"
4. ✅ **Sadness:** "I'm really sorry you're going through this. Do you want to talk about what made you feel this way?"
5. ✅ **Stress/Anxiety:** "That sounds overwhelming. What's causing the most stress right now?"
6. ✅ **Anger:** "I'm sorry something upset you. What happened?"
7. ✅ **Fear:** "I hear you. What's making you feel afraid?"
8. ✅ **Crisis Mode:** Exact emergency response with India helpline numbers
9. ✅ **Irrelevant Questions:** Polite redirect message
10. ✅ **Health Queries:** Supportive response with medical advice
11. ✅ **Follow-up Questions:** Every response includes a follow-up
12. ✅ **No Wearable Messages:** Wellness data never shown in chat

## API Endpoints

### Public Endpoints
- `GET /health` - Health check

### Authentication Endpoints
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token

### Protected Endpoints (Require JWT)
- `GET /chat` - Simple greeting
- `POST /chat` - Main chat endpoint with emotion detection
- `POST /emotion` - Emotion analysis only
- `GET /wellness/{subject_id}` - Get wellness data (dashboard)
- `GET /recommendations` - Get recommendations
- `GET /history` - Get chat history

## Dependencies

Ensure these Python packages are installed:

```bash
pip install bcrypt pymongo fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
```

Or add to `requirements.txt`:
```
bcrypt>=4.0.0
pymongo>=4.0.0
fastapi>=0.100.0
uvicorn>=0.23.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

## MongoDB Collections

### `users` Collection
```json
{
  "_id": ObjectId("..."),
  "name": "John Doe",
  "email": "john@example.com",
  "hashed_password": "$2b$12$...",
  "subject_id": "S1001",
  "created_at": ISODate("2024-01-01T00:00:00Z")
}
```

### Indexes Recommended
```javascript
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "subject_id": 1 }, { unique: true });
```

## Testing

### Test Registration
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123456"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }'
```

### Test Chat (with JWT token)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "text": "I'm feeling sad today"
  }'
```

## Migration Notes

1. **Existing Users:** If you have existing mock users, you'll need to migrate them to MongoDB
2. **Subject IDs:** Existing subject IDs will be preserved if provided during registration
3. **Backward Compatibility:** Login endpoint still works but now uses MongoDB
4. **Chat History:** Existing chat history remains intact

## Next Steps

1. Install bcrypt if not already installed: `pip install bcrypt`
2. Ensure MongoDB is running and accessible
3. Create indexes on `users` collection (see above)
4. Test registration and login endpoints
5. Update frontend with signup functionality (see `FRONTEND_SIGNUP_INTEGRATION.md`)
6. Test chat responses to verify empathetic behavior

## Notes

- All wellness data is stored internally but never shown in chat responses
- Recommendations are generated but not included in chat responses (use `/recommendations` endpoint)
- Crisis detection has highest priority and overrides all other responses
- Irrelevant questions are politely redirected
- Greetings are always allowed and get friendly responses

