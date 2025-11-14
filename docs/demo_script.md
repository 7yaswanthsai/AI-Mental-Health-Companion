# PAI-MHC Demo Script

This document provides step-by-step instructions for demonstrating the PAI-MHC (Personalized AI Mental Health Companion) system.

## Prerequisites

1. **Backend running**: `uvicorn backend.main:app --reload`
2. **MongoDB running**: Ensure MongoDB is accessible (default: `mongodb://localhost:27017`)
3. **MLflow tracking** (optional): Set `MLFLOW_TRACKING_URI` environment variable
4. **Streamlit frontend** (optional): `streamlit run frontend_streamlit/app.py`
5. **React Native app** (optional): `cd mobile_app_new && npx expo start`

## Demo Flow

### 1. Automated Test Script

Run the comprehensive test script:

```bash
python backend/demo_test.py
```

This script will:
- ✅ Test login authentication
- ✅ Test chat endpoint with emotion detection
- ✅ Test wellness/PWI endpoint
- ✅ Test recommendations endpoint
- ✅ Test chat history endpoint

### 2. Manual Demo via Streamlit

#### Step 1: Login
1. Open Streamlit app: `streamlit run frontend_streamlit/app.py`
2. Login with credentials:
   - Email: `test@pai.com`
   - Password: `123456`
3. Set Subject ID (default: `S10`)

#### Step 2: Demonstrate Empathetic Chat
Send these messages to showcase different emotions:

**Sadness:**
```
"I'm feeling really down today. Nothing seems to be going right."
```
Expected: Empathetic response, sadness detection, grounding recommendations

**Joy:**
```
"I'm so happy! I just got accepted to my dream university!"
```
Expected: Celebratory response, joy detection, gratitude suggestions

**Anxiety:**
```
"I'm really anxious about my presentation tomorrow. I can't stop worrying."
```
Expected: Calming response, anxiety detection, breathing exercises

**Crisis Detection:**
```
"I don't see the point anymore. I'm thinking about ending it all."
```
Expected: Crisis response, escalation flag, emergency resources

#### Step 3: Show Wellness Dashboard
1. Click "🔄 Refresh Wellness" in sidebar
2. Observe:
   - **PWI Card**: Color-coded (Green ≥70, Yellow 40-70, Red <40)
   - **Trend Chart**: Historical PWI values
   - **Recommendations History**: Collapsible list with timestamps

#### Step 4: Show Chat History
1. Click "📜 Load History" in sidebar
2. Verify messages are stored in MongoDB

### 3. Mobile App Demo (React Native)

#### Setup
```bash
cd mobile_app_new
npm install
npx expo start
```

#### Demo Flow
1. **Login Screen**: Enter `test@pai.com` / `123456`
2. **Chat Screen**: 
   - Send messages
   - View recommendations at bottom
   - Navigate to Wellness/Recommendations via header buttons
3. **Wellness Screen**:
   - View current PWI score
   - See trend chart
   - View feature breakdown
4. **Recommendations Screen**:
   - View current recommendations
   - See recommendation history
   - Refresh to get new recommendations

### 4. MLflow Tracking Demo

#### View Training Runs
```bash
mlflow ui
# Open http://localhost:5000
```

Navigate to experiment: `emotion-model` or `emotion-classifier`

#### View Inference Logs
1. Send chat messages via API or Streamlit
2. Check MLflow UI for:
   - Emotion predictions
   - Wellness snapshots
   - Recommendation triggers
   - Chat interaction summaries

### 5. API Testing with curl

#### Login
```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@pai.com", "password": "123456"}'
```

#### Chat (with token)
```bash
TOKEN="your_token_here"
curl -X POST http://127.0.0.1:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel sad today", "subject_id": "S10"}'
```

#### Wellness
```bash
curl -X GET http://127.0.0.1:8000/wellness/S10 \
  -H "Authorization: Bearer $TOKEN"
```

#### Recommendations
```bash
curl -X GET "http://127.0.0.1:8000/recommendations?emotion=sadness&wellness_status=Stressed" \
  -H "Authorization: Bearer $TOKEN"
```

## Key Features to Highlight

### 1. Empathy Engine
- Multi-sentence contextual responses
- Emotion-aware validation
- PWI-integrated suggestions
- Crisis detection and escalation

### 2. Emotion Detection
- LSTM-based model with transformer fallback
- Multi-label emotion classification
- Confidence scoring
- Fallback to sentiment analysis

### 3. Wellness Fusion (PWI)
- Wearable data integration (WESAD dataset)
- Real-time PWI calculation
- Status classification (Calm, Neutral, Stressed, etc.)
- Historical trend tracking

### 4. Recommendations
- Emotion-based suggestions
- Wellness-status aware
- CBT/DBT techniques
- Breathing exercises, journaling, grounding

### 5. Security
- JWT authentication
- Protected endpoints
- Secure token storage (mobile)
- Input validation

### 6. MLOps
- MLflow tracking for training
- Inference logging
- Model versioning
- Artifact storage

## Troubleshooting

### Backend not starting
- Check MongoDB connection
- Verify environment variables (JWT_SECRET)
- Check port 8000 availability

### No emotion predictions
- Verify model files exist: `backend/models/emotion_lstm_model.h5`
- Check tokenizer: `backend/models/tokenizer.pkl`
- Run training: `python mlops/train_and_register.py`

### No PWI data
- Verify wearable data exists for subject (e.g., `S10`)
- Check `database/wearable_preprocess.py` has processed data
- Verify MongoDB has `wearable_data` collection

### MLflow not logging
- Check `MLFLOW_TRACKING_URI` environment variable
- Verify MLflow server is running (if using remote tracking)
- Check file permissions for local tracking

## Success Criteria

✅ All endpoints return 200 status codes  
✅ Emotion predictions show reasonable confidence (>0.3)  
✅ PWI scores are in range [0, 100]  
✅ Recommendations are relevant to emotion/wellness  
✅ Chat responses are empathetic and contextual  
✅ Crisis detection triggers appropriate response  
✅ MLflow logs show inference data  
✅ Mobile app can login and navigate all screens  

## Next Steps After Demo

1. Review MLflow metrics and model performance
2. Check MongoDB collections for data integrity
3. Review chat logs for quality of responses
4. Analyze PWI trends for subjects
5. Gather feedback on empathy and recommendations

