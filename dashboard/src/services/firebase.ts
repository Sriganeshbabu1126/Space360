import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyBZLogK0LCNinkEhiLRzHIfABjeZoGWM4k",
  authDomain: "field-check-72967.firebaseapp.com",
  projectId: "field-check-72967",
  storageBucket: "field-check-72967.firebasestorage.app",
  messagingSenderId: "556920532741",
  appId: "1:556920532741:web:73c4de63bfcd698eb8d16c",
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
