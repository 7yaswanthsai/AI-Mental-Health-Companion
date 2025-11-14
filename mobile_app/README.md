# PAI-MHC Mobile (Expo)

Quick-start Expo project providing a mobile companion for the PAI-MHC platform.

## Screens

- **Login** – Authenticates against `/login` and stores JWT securely.
- **Chat** – Sends user messages to `/chat` with bearer token, displays responses and recommendations.
- **Wellness** – Fetches `/wellness/{subject_id}` to show latest Personalized Wellness Index snapshots.

## Getting Started

```bash
cd mobile_app
npm install        # or yarn
npx expo start     # choose iOS/Android/Web emulator or Expo Go
```

Ensure the FastAPI backend is running locally at `http://127.0.0.1:8000`. Update `app.json` → `extra.apiBaseUrl` if your backend runs elsewhere.

## Environment Notes

- JWT token and subject ID persist via `expo-secure-store`.
- Axios automatically attaches `Authorization: Bearer <token>` headers once logged in.
- To adjust the default subject, update the Auth context or UI as needed.


