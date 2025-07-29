import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { apiService, type ProfilePageData } from '../services/api';
import {
  UserIcon,
  KeyIcon,
  ClockIcon,
  ChartBarIcon,
  ArrowPathIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline';

const Profile: React.FC = () => {
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showToken, setShowToken] = useState(false);

  const { data: profileData, isLoading, error, refetch } = useQuery<ProfilePageData>({
    queryKey: ['profilePageData'],
    queryFn: apiService.getProfilePageData,
    staleTime: 5 * 60 * 1000,
  });

  const handleRegenerateToken = async () => {
    setIsRegenerating(true);
    try {
      await apiService.regenerateToken({
        validity_days: 0,
        save_old: true,
      });
      await refetch();
    } catch (error) {
      console.error('Failed to regenerate token:', error);
    } finally {
      setIsRegenerating(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !profileData) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900">Error loading profile</h2>
            <p className="mt-2 text-gray-600">Please try again later.</p>
          </div>
        </div>
      </div>
    );
  }

  const { user, token_info, daily_usage, current_plan } = profileData;

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
          <p className="mt-2 text-gray-600">Manage your account and API access</p>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <UserIcon className="h-6 w-6 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900">Account Information</h2>
              </div>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <p className="mt-1 text-sm text-gray-900">{user.first_name} {user.last_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <p className="mt-1 text-sm text-gray-900">{user.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Username</label>
                  <p className="mt-1 text-sm text-gray-900">{user.username}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Member since</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {new Date(user.date_joined).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <KeyIcon className="h-6 w-6 text-blue-600" />
                  <h2 className="text-xl font-semibold text-gray-900">API Token</h2>
                </div>
                <button
                  onClick={handleRegenerateToken}
                  disabled={isRegenerating}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <ArrowPathIcon className={`h-4 w-4 mr-2 ${isRegenerating ? 'animate-spin' : ''}`} />
                  {isRegenerating ? 'Regenerating...' : 'Regenerate'}
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">API Token</label>
                  <div className="mt-1 flex rounded-md shadow-sm">
                    <input
                      type={showToken ? 'text' : 'password'}
                      value={token_info.token}
                      readOnly
                      className="flex-1 rounded-l-md border-gray-300 bg-gray-50 text-sm"
                    />
                    <button
                      onClick={() => setShowToken(!showToken)}
                      className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 hover:bg-gray-100"
                    >
                      {showToken ? 'Hide' : 'Show'}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Created</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {new Date(token_info.created).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Expires</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {token_info.never_expires ? 'Never' : token_info.expires ? new Date(token_info.expires).toLocaleString() : 'N/A'}
                    </p>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => copyToClipboard(token_info.token)}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <ClipboardDocumentIcon className="h-4 w-4 mr-2" />
                    Copy Token
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <ChartBarIcon className="h-6 w-6 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900">Usage Statistics</h2>
              </div>
              
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{daily_usage.made}</p>
                  <p className="text-sm text-gray-600">Requests Made Today</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{daily_usage.remaining}</p>
                  <p className="text-sm text-gray-600">Requests Remaining</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-600">{daily_usage.limit}</p>
                  <p className="text-sm text-gray-600">Daily Limit</p>
                </div>
              </div>

              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Usage</span>
                  <span>{daily_usage.percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${daily_usage.percentage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-8">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <ClockIcon className="h-6 w-6 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900">Current Plan</h2>
              </div>
              
              {current_plan ? (
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{current_plan.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{current_plan.description}</p>
                  <div className="mt-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Daily Limit:</span>
                      <span className="font-medium">{current_plan.daily_request_limit.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Monthly Limit:</span>
                      <span className="font-medium">{current_plan.monthly_request_limit.toLocaleString()}</span>
                    </div>
                  </div>
                  <Link
                    to="/plans"
                    className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                  >
                    Choose a Plan
                  </Link>
                </div>
              ) : (
                <div>
                  <p className="text-gray-600">No active plan</p>
                  <Link
                    to="/plans"
                    className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    Choose a Plan
                  </Link>
                </div>
              )}
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <Link
                  to="/api-docs"
                  className="block w-full text-left px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md"
                >
                  API Documentation
                </Link>
                <Link
                  to="/plans"
                  className="block w-full text-left px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md"
                >
                  View Plans
                </Link>
                <Link
                  to="/faq"
                  className="block w-full text-left px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md"
                >
                  Help & FAQ
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile; 