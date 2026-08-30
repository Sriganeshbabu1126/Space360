import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import { Camera, LogIn, Mail, Lock } from 'lucide-react';
import toast from 'react-hot-toast';

const LoginPage: React.FC = () => {
  useEffect(() => { document.title = "Login | Space360"; }, []);
  const { user, signIn, signInWithEmail } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  if (user) {
    return <Navigate to="/" replace />;
  }

  const handleGoogleSignIn = async () => {
    try {
      await signIn();
      toast.success('Successfully signed in!');
    } catch (error) {
      toast.error('Google Sign-in failed. This project may not have it enabled.');
    }
  };

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return toast.error('Please enter email and password');
    try {
      await signInWithEmail(email, password);
      toast.success('Successfully signed in!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to sign in. Please check credentials.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-sm border border-gray-100 text-center">
        <div className="flex flex-col items-center">
          <div className="bg-brand-50 p-4 rounded-full mb-4">
            <Camera className="w-12 h-12 text-brand-600" />
          </div>
          <h2 className="mt-2 text-3xl font-extrabold text-gray-900">
            Space360
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Construction Progress Monitoring
          </p>
        </div>
        
        <form className="mt-8 space-y-4" onSubmit={handleEmailSignIn}>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="pl-10 w-full py-3 px-4 border border-gray-300 rounded-lg shadow-sm focus:ring-brand-500 focus:border-brand-500 text-sm"
              placeholder="Email address"
            />
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="pl-10 w-full py-3 px-4 border border-gray-300 rounded-lg shadow-sm focus:ring-brand-500 focus:border-brand-500 text-sm"
              placeholder="Password"
            />
          </div>
          <button
            type="submit"
            className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500 transition-colors"
          >
            Sign in
          </button>
        </form>

        <div className="mt-6 relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or continue with</span>
          </div>
        </div>

        <div className="mt-6">
          <button
            type="button"
            onClick={handleGoogleSignIn}
            className="w-full flex justify-center items-center py-3 px-4 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
          >
            <LogIn className="w-5 h-5 mr-2 text-gray-400" />
            Sign in with Google
          </button>
        </div>
        <p className="mt-6 text-xs text-gray-400">by SGB Dev Apps</p>
      </div>
    </div>
  );
};

export default LoginPage;
