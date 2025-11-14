# PAI-MHC Mobile App

React Native mobile client for the Personalized AI Mental Health Companion.

## Features

- 🔐 **Secure Login** - JWT-based authentication
- 💬 **Chat Interface** - Real-time empathetic conversations with emotion detection
- 🩺 **Wellness Dashboard** - Personalized Wellness Index (PWI) tracking with visualizations
- 💡 **Recommendations** - Personalized wellness suggestions based on emotions and PWI
- 📈 **Trend Charts** - Visual wellness trend tracking over time

## Prerequisites

- Node.js 18+ and npm/yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (Mac) or Android Emulator / Physical device with Expo Go app

## Installation

```bash
cd mobile_app
npm install
```

## Configuration

Update the API base URL in `app.json` if your backend is not running on `http://127.0.0.1:8000`:

```json
{
  "extra": {
    "apiBaseUrl": "http://YOUR_BACKEND_URL:8000"
  }
}
```

For physical devices, use your computer's local IP address instead of `127.0.0.1`.

## Running the App

### Development Mode

```bash
npm start
```

Then:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app on physical device

### Build for Production

```bash
# iOS
expo build:ios

# Android
expo build:android
```

## Demo Credentials

- **Email**: `test@pai.com`
- **Password**: `123456`

## Project Structure

```
mobile_app/
├── App.js                 # Root component
├── app.json              # Expo configuration
├── src/
│   ├── api/
│   │   └── client.js     # Axios API client with JWT
│   ├── context/
│   │   └── AuthContext.js # Authentication context
│   ├── navigation/
│   │   └── AppNavigator.js # Navigation setup
│   └── screens/
│       ├── LoginScreen.js   # Login screen
│       ├── ChatScreen.js    # Chat interface
│       └── WellnessScreen.js # Wellness dashboard
```

## Features in Detail

### Chat Screen
- Real-time messaging with empathetic AI responses
- Emotion tags displayed for each response
- Recommendation chips shown below chat
- Auto-scroll to latest message
- Loading indicators during API calls

### Wellness Screen
- Current PWI score with color-coded status
- Interactive trend chart (simple line visualization)
- Feature breakdown (EDA, ECG, BVP, TEMP, RESP)
- Recent history with pull-to-refresh
- Status badges (Calm, Neutral, Mild Stress, Stressed)

## Troubleshooting

### Connection Issues
- Ensure backend is running on the configured URL
- For physical devices, ensure phone and computer are on same network
- Check firewall settings

### Build Issues
- Clear cache: `expo start -c`
- Reinstall dependencies: `rm -rf node_modules && npm install`

## License

Part of the PAI-MHC project.
