import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyBZLogK0LCNinkEhiLRzHIfABjeZoGWM4k",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "field-check-72967.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "field-check-72967",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "field-check-72967.firebasestorage.app",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_ID || "556920532741",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:556920532741:web:73c4de63bfcd698eb8d16c",
  measurementId: "G-0WVDGBT1ER"
};

const app = initializeApp(firebaseConfig);
export const analytics = getAnalytics(app);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
googleProvider.addScope(
  "https://www.googleapis.com/auth/cloud-platform"
);
export default app;
