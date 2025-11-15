# Frontend Signup Integration Guide

This document provides API integration instructions for adding user registration (signup) functionality to your frontend.

## Overview

The backend now supports user registration via `POST /register`. After successful registration, users should be automatically navigated to the login screen.

## API Endpoint

### POST /register

**URL:** `http://your-backend-url/register`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "subject_id": "S1012"  // Optional - auto-generated if not provided
}
```

**Response (Success - 200):**
```json
{
  "message": "User registered successfully",
  "subject_id": "S1012"
}
```

**Response (Error - 400):**
```json
{
  "detail": "Email already registered"
}
```

**Response (Error - 500):**
```json
{
  "detail": "Registration failed"
}
```

## Frontend Implementation Steps

### 1. Update API Client

Add the registration function to your API client (e.g., `frontend/src/lib/api.ts`):

```typescript
// Add to your API client
export const authApi = {
  // ... existing login function ...
  
  register: async (data: {
    name: string;
    email: string;
    password: string;
    subject_id?: string;
  }): Promise<{ message: string; subject_id: string }> => {
    const response = await axios.post(`${BASE_URL}/register`, data);
    return response.data;
  },
};
```

### 2. Create Signup Page Component

Create a new signup page component (e.g., `frontend/src/pages/Signup.tsx`):

```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../lib/api';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authApi.register({
        name,
        email,
        password,
      });
      
      // Show success message
      alert(`Registration successful! Your subject ID is: ${response.subject_id}`);
      
      // Navigate to login screen
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <h2>Create Account</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSignup}>
        <input
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Sign Up'}
        </button>
      </form>
      <p>
        Already have an account?{' '}
        <a href="/login">Login here</a>
      </p>
    </div>
  );
}
```

### 3. Add Signup Button to Login Page

Update your login page (e.g., `frontend/src/pages/Login.tsx`) to include a signup button:

```typescript
// Add this button/link in your login form
<button type="button" onClick={() => navigate('/signup')}>
  Create New Account
</button>
// OR
<Link to="/signup">Don't have an account? Sign up</Link>
```

### 4. Update Routing

Add the signup route to your router (e.g., `frontend/src/App.tsx` or your router file):

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Signup from './pages/Signup';
import Login from './pages/Login';
// ... other imports

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        {/* ... other routes ... */}
      </Routes>
    </BrowserRouter>
  );
}
```

## React Native (Mobile App) Implementation

If you're using React Native, follow similar patterns:

### 1. Update API Client

In `mobile_app_new/src/api/client.js` or similar:

```javascript
export const register = async (name, email, password) => {
  const response = await api.post('/register', {
    name,
    email,
    password,
  });
  return response.data;
};
```

### 2. Create Signup Screen

Create `mobile_app_new/src/screens/SignupScreen.js`:

```javascript
import React, { useState } from 'react';
import { View, TextInput, Button, Alert, Text } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { register } from '../api/client';

export default function SignupScreen() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigation = useNavigation();

  const handleSignup = async () => {
    if (!name || !email || !password) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await register(name, email, password);
      Alert.alert(
        'Success',
        `Registered! Subject ID: ${response.subject_id}`,
        [{ text: 'OK', onPress: () => navigation.navigate('Login') }]
      );
    } catch (error) {
      Alert.alert('Error', error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text>Create Account</Text>
      <TextInput
        placeholder="Full Name"
        value={name}
        onChangeText={setName}
      />
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button
        title={loading ? 'Registering...' : 'Sign Up'}
        onPress={handleSignup}
        disabled={loading}
      />
      <Button
        title="Already have an account? Login"
        onPress={() => navigation.navigate('Login')}
      />
    </View>
  );
}
```

### 3. Add to Navigation

In your navigation stack:

```javascript
import SignupScreen from './screens/SignupScreen';

// Add to your stack
<Stack.Screen name="Signup" component={SignupScreen} />
```

## Testing

1. **Test successful registration:**
   - Fill all fields
   - Submit form
   - Should see success message with subject_id
   - Should navigate to login screen

2. **Test duplicate email:**
   - Try registering with an existing email
   - Should see "Email already registered" error

3. **Test validation:**
   - Try submitting empty fields
   - Should see validation errors

4. **Test login after signup:**
   - Register new user
   - Navigate to login
   - Login with new credentials
   - Should work correctly

## Notes

- Passwords are hashed using bcrypt on the backend
- Subject IDs are auto-generated if not provided (format: S####)
- After registration, users must login to get a JWT token
- The login endpoint works with the new user model automatically

## Error Handling

Handle these error cases:
- **400 Bad Request:** Email already exists or invalid input
- **500 Internal Server Error:** Server-side error during registration
- **Network Error:** Backend not reachable

Display user-friendly error messages in your UI.

