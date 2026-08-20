import React, { useEffect, useState } from 'react';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { store, persistor } from './src/store/store';
import AppNavigator from './src/navigation/AppNavigator';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { getAuth } from '@react-native-firebase/auth';
import type { User as FirebaseAuthTypesUser } from '@react-native-firebase/auth';
import { setAuthUser, clearAuth } from './src/store/slices/authSlice';
import { ActivityIndicator, View } from 'react-native';

// Helper component to handle auth state changes and hydrate Redux
function AuthHandler({ children }: { children: React.ReactNode }) {
  const [initializing, setInitializing] = useState(true);
  const auth = getAuth();

  // Handle user state changes
  async function onAuthStateChanged(user: FirebaseAuthTypesUser | null) {
    if (user) {
      try {
        const token = await user.getIdToken();
        store.dispatch(setAuthUser({
          uid: user.uid,
          email: user.email,
          token: token,
        }));
      } catch (error) {
        console.error('Failed to get token on auth state change', error);
      }
    } else {
      store.dispatch(clearAuth());
    }
    
    if (initializing) setInitializing(false);
  }

  useEffect(() => {
    const subscriber = auth.onAuthStateChanged(onAuthStateChanged);
    return subscriber; // unsubscribe on unmount
  }, []);

  if (initializing) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#1D9E75" />
      </View>
    );
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <SafeAreaProvider>
          <AuthHandler>
            <AppNavigator />
          </AuthHandler>
        </SafeAreaProvider>
      </PersistGate>
    </Provider>
  );
}
