import React, { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import { Camera, LogIn } from 'lucide-react';
import toast from 'react-hot-toast';

const LoginPage: React.FC = () => {
  useEffect(() => { document.title = "Login | Space360"; }, []);
  const { user, signIn } = useAuth();

  if (user) {
    return <Navigate to="/" replace />;
  }

  const handleSignIn = async () => {
    try {
      await signIn();
      toast.success('Successfully signed in!');
    } catch (error) {
      toast.error('Failed to sign in. Please try again.');
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
        
        <div className="mt-8">
          <button
            onClick={handleSignIn}
            className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <LogIn className="w-5 h-5 mr-2" />
            Sign in with Google
          </button>
        </div>
        <p className="mt-6 text-xs text-gray-400">by SGB Dev Apps</p>
      </div>
    </div>
  );
};

export default LoginPage;
