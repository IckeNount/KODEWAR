"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/app/contexts/AuthContext";
import { RegisterCredentials } from "@/app/types/auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [credentials, setCredentials] = useState<RegisterCredentials>({
    username: "",
    email: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await register(credentials);
    } catch (error) {
      // Error is handled by the auth context
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className='min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex items-center justify-center'>
      <div className='w-full max-w-md p-8 space-y-8 bg-gray-800 rounded-lg shadow-lg'>
        <div className='text-center'>
          <h1 className='text-4xl font-bold'>Join KODEWAR</h1>
          <p className='mt-2 text-gray-400'>Start your space adventure today</p>
        </div>

        <form onSubmit={handleSubmit} className='mt-8 space-y-6'>
          <div className='space-y-4'>
            <div>
              <label
                htmlFor='username'
                className='block text-sm font-medium text-gray-300'
              >
                Username
              </label>
              <input
                id='username'
                type='text'
                required
                value={credentials.username}
                onChange={(e) =>
                  setCredentials({ ...credentials, username: e.target.value })
                }
                className='mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500'
                placeholder='Choose a username'
              />
            </div>

            <div>
              <label
                htmlFor='email'
                className='block text-sm font-medium text-gray-300'
              >
                Email
              </label>
              <input
                id='email'
                type='email'
                required
                value={credentials.email}
                onChange={(e) =>
                  setCredentials({ ...credentials, email: e.target.value })
                }
                className='mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500'
                placeholder='Enter your email'
              />
            </div>

            <div>
              <label
                htmlFor='password'
                className='block text-sm font-medium text-gray-300'
              >
                Password
              </label>
              <input
                id='password'
                type='password'
                required
                value={credentials.password}
                onChange={(e) =>
                  setCredentials({ ...credentials, password: e.target.value })
                }
                className='mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500'
                placeholder='Create a password'
              />
            </div>
          </div>

          <button
            type='submit'
            disabled={isLoading}
            className={`w-full py-3 px-4 rounded-md text-white font-medium ${
              isLoading
                ? "bg-blue-600 opacity-50 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {isLoading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <div className='text-center mt-4'>
          <p className='text-gray-400'>
            Already have an account?{" "}
            <Link
              href='/auth/login'
              className='text-blue-400 hover:text-blue-300'
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
