import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyBbiel5T3pFgiMFvdVweWC0RsJa5juVhZA",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "space360-production.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "space360-production",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "space360-production.firebasestorage.app",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_ID || "356278681043",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:556920532741:web:73c4de63bfcd698eb8d16c",
  measurementId: "G-0WVDGBT1ER"
};

const app = initializeApp(firebaseConfig);
export const analytics = getAnalytics(app);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const googleProvider = new GoogleAuthProvider();
googleProvider.addScope(
  "https://www.googleapis.com/auth/cloud-platform"
);
export default app;
