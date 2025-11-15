# PAI-MHC: Personalized AI Mental Health Companion

<div align="center">


![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-teal.svg)
![React](https://img.shields.io/badge/React-18.3.1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**An empathetic AI-powered mental health companion that combines emotion detection, wearable data fusion, and personalized wellness recommendations.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API Documentation](#-api-documentation) • [Project Structure](#-project-structure)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

PAI-MHC (Personalized AI Mental Health Companion) is a comprehensive mental health support system that provides:

- **Emotion-Aware Conversations**: Real-time emotion detection using LSTM and Transformer models
- **Wearable Data Integration**: Personalized Wellness Index (PWI) computed from physiological signals
- **Empathetic Responses**: Context-aware, supportive chatbot interactions
- **Personalized Recommendations**: Tailored wellness suggestions based on emotional state and wellness metrics
- **Crisis Detection**: Automatic identification of self-harm intent with emergency resources
- **Multi-Platform Access**: Web frontend (React) and mobile app (React Native)

---

## ✨ Features

### Core Features

- 🔐 **User Authentication**: Secure JWT-based authentication with user registration
- 💬 **Intelligent Chatbot**: Empathetic, context-aware conversations with follow-up questions
- 😊 **Emotion Detection**: Multi-model emotion classification (sadness, anger, fear, joy, stress, neutral)
- 📊 **Wellness Tracking**: Personalized Wellness Index (PWI) from wearable sensor data
- 🎯 **Personalized Recommendations**: Contextual wellness suggestions (breathing exercises, journaling, CBT techniques)
- 🚨 **Crisis Intervention**: Automatic detection of self-harm intent with emergency contact information
- 📱 **Cross-Platform**: Web dashboard (React) and mobile app (React Native/Expo)
- 📈 **MLOps Integration**: MLflow tracking for model versioning and inference logging
- 🔒 **Security**: Password hashing, JWT tokens, CORS protection, input validation

### Advanced Features

- **Context Memory**: Short-term conversation history for contextual responses
- **Relevance Filtering**: Detects and handles irrelevant questions gracefully
- **Fallback Mechanisms**: Robust emotion detection with multiple model fallbacks
- **Real-time Logging**: Comprehensive logging to MongoDB and MLflow
- **Wearable Data Processing**: WESAD dataset integration with baseline normalization

---

## 🛠 Tech Stack

### Backend

- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB (PyMongo 4.5.0)
- **Authentication**: JWT (PyJWT 2.8.0), bcrypt 4.0.0
- **ML/NLP**: 
  - PyTorch 2.1.0
  - Transformers 4.40.0
  - scikit-learn 1.3.0
  - NLTK 3.8.1
- **MLOps**: MLflow 2.9.2
- **Data Processing**: pandas 2.1.1, numpy 1.24.3

### Frontend (Web)

- **Framework**: React 18.3.1 with TypeScript
- **Build Tool**: Vite 7.2.2
- **UI Library**: Radix UI, Tailwind CSS
- **State Management**: Zustand 5.0.8
- **Routing**: React Router DOM 6.30.1
- **HTTP Client**: Axios 1.13.2
- **Animations**: Framer Motion 12.23.24

### Mobile App

- **Framework**: React Native 0.81.5 with Expo ~54.0.23
- **Navigation**: React Navigation 7.x
- **State Management**: React Context API
- **Storage**: Expo Secure Store

### Development Tools

- **Python**: 3.10+
- **Node.js**: 18+
- **Package Managers**: pip, npm/yarn
- **Containerization**: Docker, Docker Compose

---

## 📁 Project Structure

```
Semester7Capstone/
├── backend/                    # FastAPI backend application
│   ├── main.py                # Main FastAPI app and routes
│   ├── auth.py                # JWT authentication & user management
│   ├── emotion_service.py     # Emotion detection service
│   ├── empathy_engine.py     # Empathetic response generation
│   ├── safety_guard.py        # Crisis detection
│   ├── relevance_checker.py   # Relevance filtering
│   ├── wellness_fusion.py     # PWI computation
│   ├── recommendations.py     # Recommendation engine
│   ├── context_memory.py      # Conversation context
│   ├── models/                # Trained ML models
│   │   ├── emotion_lstm_model.h5
│   │   ├── tokenizer.pkl
│   │   └── mlb.pkl
│   └── utils/                 # Utility modules
│
├── frontend/                  # React web application
│   ├── src/
│   │   ├── pages/             # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── Signup.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── Wellness.tsx
│   │   │   └── Recommendations.tsx
│   │   ├── components/        # Reusable UI components
│   │   ├── lib/               # API client, store
│   │   └── hooks/             # Custom React hooks
│   └── package.json
│
├── mobile_app_new/            # React Native mobile app
│   ├── src/
│   │   ├── screens/           # Screen components
│   │   ├── navigation/       # Navigation setup
│   │   ├── api/              # API client
│   │   └── context/          # Context providers
│   └── package.json
│
├── database/                  # Database utilities
│   ├── db_connection.py      # MongoDB connection
│   ├── chat_logger.py        # Chat logging
│   └── wearable_preprocess.py # Wearable data processing
│
├── mlops/                     # MLOps utilities
│   ├── mlflow_config.py      # MLflow configuration
│   ├── log_inference.py      # Inference logging
│   └── train_and_register.py # Model training
│
├── data/                      # Datasets
│   ├── goemotions_*.csv      # Emotion training data
│   └── wearable/             # WESAD dataset
│
├── docs/                      # Documentation
│   ├── system_architecture.md
│   ├── demo_script.md
│   └── data_governance_plan.md
│
├── requirements.txt           # Python dependencies
├── docker-compose.yml        # Docker configuration
├── Dockerfile                # Backend Docker image
└── README.md                 # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm/yarn
- MongoDB 4.4+ (running locally or remote)
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Semester7Capstone
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv310
   # Windows
   venv310\Scripts\activate
   # Linux/Mac
   source venv310/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the `backend/` directory:
   ```env
   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DB=pai_mhc_db
   JWT_SECRET=your-secret-key-here-change-in-production
   JWT_ALGORITHM=HS256
   JWT_EXP_MINUTES=60
   ```

5. **Initialize MongoDB**
   - Ensure MongoDB is running on `localhost:27017`
   - The database and collections will be created automatically on first run

6. **Create test user (optional)**
   ```bash
   python backend/init_test_user.py
   ```
   This creates a test user: `test@pai.com` / `123456`

### Frontend Setup (Web)

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**
   Create a `.env` file in the `frontend/` directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Mobile App Setup

1. **Navigate to mobile app directory**
   ```bash
   cd mobile_app_new
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure API URL** (if needed)
   Edit `app.json` to set `apiBaseUrl` for physical devices

---

## ⚙️ Configuration

### Backend Configuration

Edit `backend/config.py` or use environment variables:

- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB`: Database name
- `JWT_SECRET`: Secret key for JWT tokens (use a strong random string in production)
- `JWT_ALGORITHM`: JWT algorithm (default: HS256)
- `JWT_EXP_MINUTES`: Token expiration time in minutes

### Frontend Configuration

- `VITE_API_BASE_URL`: Backend API base URL (default: `http://localhost:8000`)

### Mobile App Configuration

- Edit `mobile_app_new/app.json` to configure `apiBaseUrl` for physical devices
- For Android emulator: uses `http://10.0.2.2:8000` automatically
- For iOS simulator: uses `http://localhost:8000` automatically

---

## 💻 Usage

### Starting the Backend

1. **Activate virtual environment**
   ```bash
   venv310\Scripts\activate  # Windows
   # or
   source venv310/bin/activate  # Linux/Mac
   ```

2. **Start the FastAPI server**
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

### Starting the Web Frontend

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Start the development server**
   ```bash
   npm run dev
   ```

   The app will be available at http://localhost:5173 (or the port shown in terminal)

### Starting the Mobile App

1. **Navigate to mobile app directory**
   ```bash
   cd mobile_app_new
   ```

2. **Start Expo**
   ```bash
   npx expo start
   ```

3. **Run on device/emulator**
   - Press `a` for Android emulator
   - Press `i` for iOS simulator
   - Scan QR code with Expo Go app for physical device

### Using Docker (Optional)

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f
   ```

---

## 📚 API Documentation

### Authentication Endpoints

#### `POST /register`
Register a new user.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "subject_id": "S10"
}
```

#### `POST /login`
Authenticate and get JWT token.

**Request Body:**
```json
{
  "email": "test@pai.com",
  "password": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Chat Endpoints

#### `POST /chat`
Send a message to the chatbot (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "text": "I'm feeling really stressed today",
  "subject_id": "S10"
}
```

**Response:**
```json
{
  "text": "I'm really sorry you're feeling this way...",
  "emotion": "stress",
  "probability": 0.85,
  "wellness": {
    "subject_id": "S10",
    "pwi": 45.2,
    "status": "Stressed"
  },
  "recommendations": [
    "Try a 4-7-8 breathing exercise",
    "Practice progressive muscle relaxation"
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "tags": ["stress", "breathing"],
  "tone": "gentle",
  "escalate": false
}
```

#### `GET /history`
Get chat history for the authenticated user.

**Response:**
```json
[
  {
    "text": "I'm feeling stressed",
    "emotion": "stress",
    "timestamp": "2024-01-15T10:30:00Z"
  }
]
```

### Wellness Endpoints

#### `GET /wellness/{subject_id}`
Get current wellness status for a subject.

**Response:**
```json
{
  "subject_id": "S10",
  "pwi": 45.2,
  "status": "Stressed",
  "features": {
    "eda_mean": 0.15,
    "hr_mean": 75.2
  }
}
```

#### `GET /recommendations`
Get personalized recommendations.

**Query Parameters:**
- `emotion`: Emotion label (required)
- `wellness_status`: Wellness status (optional)

**Response:**
```json
{
  "emotion": "stress",
  "pwi_status": "Stressed",
  "items": [
    "Try a 4-7-8 breathing exercise",
    "Practice progressive muscle relaxation"
  ]
}
```

### Health Check

#### `GET /health`
Check API health status.

**Response:**
```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest backend/tests/

# Run specific test file
pytest backend/tests/test_empathy.py

# Test login
python backend/test_login.py
```

### API Testing

Use the interactive API docs at http://localhost:8000/docs or test with curl:

```bash
# Register
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Chat (replace TOKEN with actual token)
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel sad", "subject_id": "S10"}'
```

---

## 🚢 Deployment

### Backend Deployment

1. **Set production environment variables**
2. **Use a production ASGI server** (e.g., Gunicorn with Uvicorn workers)
   ```bash
   gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **Set up MongoDB** (use MongoDB Atlas for cloud deployment)

4. **Configure reverse proxy** (Nginx, Caddy, etc.)

### Frontend Deployment

1. **Build the production bundle**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy to static hosting** (Vercel, Netlify, AWS S3, etc.)

### Mobile App Deployment

1. **Build for production**
   ```bash
   cd mobile_app_new
   expo build:android  # or expo build:ios
   ```

2. **Submit to app stores** (Google Play, Apple App Store)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript/JavaScript**: Follow ESLint rules, use TypeScript for type safety
- **Commit Messages**: Use clear, descriptive messages

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

For issues, questions, or contributions:

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the `docs/` directory
- **Security**: See `SECURITY.md` for security-related concerns

---

## 🙏 Acknowledgments

- **WESAD Dataset**: For wearable sensor data
- **GoEmotions Dataset**: For emotion classification training
- **FastAPI**: For the excellent web framework
- **React & React Native**: For frontend frameworks
- **MLflow**: For MLOps capabilities

---

## 📊 Project Status

- ✅ **Phase 1**: Core backend API, emotion detection, basic chatbot
- ✅ **Phase 2**: Empathy engine, context memory, safety features
- ✅ **Phase 3**: User authentication, frontend, mobile app
- 🚧 **Phase 4**: Advanced features, MLOps integration, deployment

---

<div align="center">


[⬆ Back to Top](#pai-mhc-personalized-ai-mental-health-companion)

</div>

