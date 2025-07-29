import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { apiService, type WaitingListData } from '../services/api';
import { CheckIcon } from '@heroicons/react/24/outline';

const WaitingList: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    company_name: '',
    company_size: '',
    desired_plan: '',
    desired_billing_cycle: '',
    api_features: [] as string[],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const { data: waitingListData, isLoading } = useQuery<WaitingListData>({
    queryKey: ['waitingListData'],
    queryFn: apiService.getWaitingListData,
    staleTime: 5 * 60 * 1000,
  });

  const plans = waitingListData?.plans || [];

  const apiFeatures = [
    'Real-time Stock Data',
    'Historical Data',
    'Forex Data',
    'Crypto Data',
    'Economic Indicators',
    'News Data',
    'Technical Analysis',
    'Options Data',
    'Futures Data',
    'Commodities Data',
  ];

  const companySizes = [
    '1-10 employees',
    '11-50 employees',
    '51-200 employees',
    '201-500 employees',
    '500+ employees',
  ];

  useEffect(() => {
    const plan = searchParams.get('plan');
    const billingCycle = searchParams.get('billing_cycle');
    
    if (plan) {
      setFormData(prev => ({ ...prev, desired_plan: plan }));
    }
    if (billingCycle) {
      setFormData(prev => ({ ...prev, desired_billing_cycle: billingCycle }));
    }
  }, [searchParams]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFeatureToggle = (feature: string) => {
    setFormData(prev => ({
      ...prev,
      api_features: prev.api_features.includes(feature)
        ? prev.api_features.filter(f => f !== feature)
        : [...prev.api_features, feature]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const response = await fetch('/api/waiting-list/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        navigate('/waiting-list-success');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to submit. Please try again.');
      }
    } catch (err) {
      setError('Failed to submit. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white">
      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Join Our Waiting List
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Be among the first to access our comprehensive financial data API. 
              Get early access and exclusive benefits when we launch.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-blue-600">What to Expect</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Early access to comprehensive financial data
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Our API provides real-time stock data, forex rates, crypto prices, and more. 
              Join our waiting list to get early access and exclusive benefits.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white py-24 sm:py-32">
        <div className="mx-auto max-w-2xl px-6 lg:px-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium leading-6 text-gray-900">
                  First name *
                </label>
                <div className="mt-2">
                  <input
                    type="text"
                    name="first_name"
                    id="first_name"
                    required
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-medium leading-6 text-gray-900">
                  Last name *
                </label>
                <div className="mt-2">
                  <input
                    type="text"
                    name="last_name"
                    id="last_name"
                    required
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">
                Email address *
              </label>
              <div className="mt-2">
                <input
                  type="email"
                  name="email"
                  id="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div>
              <label htmlFor="company_name" className="block text-sm font-medium leading-6 text-gray-900">
                Company name
              </label>
              <div className="mt-2">
                <input
                  type="text"
                  name="company_name"
                  id="company_name"
                  value={formData.company_name}
                  onChange={handleInputChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div>
              <label htmlFor="company_size" className="block text-sm font-medium leading-6 text-gray-900">
                Company size
              </label>
              <div className="mt-2">
                <select
                  name="company_size"
                  id="company_size"
                  value={formData.company_size}
                  onChange={handleInputChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                >
                  <option value="">Select company size</option>
                  {companySizes.map((size) => (
                    <option key={size} value={size}>
                      {size}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium leading-6 text-gray-900 mb-4">
                Which API features are you most interested in? (Select all that apply)
              </label>
              <div className="space-y-3">
                {apiFeatures.map((feature) => (
                  <div key={feature} className="flex items-center">
                    <input
                      type="checkbox"
                      id={feature}
                      checked={formData.api_features.includes(feature)}
                      onChange={() => handleFeatureToggle(feature)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"
                    />
                    <label htmlFor={feature} className="ml-3 text-sm text-gray-900">
                      {feature}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium leading-6 text-gray-900 mb-4">
                Which billing cycle are you most interested in?
              </label>
              <div className="space-y-3">
                <div className="flex items-center">
                  <input
                    type="radio"
                    name="desired_billing_cycle"
                    id="monthly"
                    value="monthly"
                    checked={formData.desired_billing_cycle === 'monthly'}
                    onChange={handleInputChange}
                    className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-600"
                  />
                  <label htmlFor="monthly" className="ml-3 text-sm text-gray-900">
                    Monthly billing
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="radio"
                    name="desired_billing_cycle"
                    id="yearly"
                    value="yearly"
                    checked={formData.desired_billing_cycle === 'yearly'}
                    onChange={handleInputChange}
                    className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-600"
                  />
                  <label htmlFor="yearly" className="ml-3 text-sm text-gray-900">
                    Yearly billing (20% discount)
                  </label>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium leading-6 text-gray-900 mb-4">
                Which plan are you most interested in?
              </label>
              <div className="space-y-3">
                {plans.map((plan) => (
                  <div key={plan.id} className="flex items-center">
                    <input
                      type="radio"
                      name="desired_plan"
                      id={`plan-${plan.id}`}
                      value={plan.name}
                      checked={formData.desired_plan === plan.name}
                      onChange={handleInputChange}
                      className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-600"
                    />
                    <label htmlFor={`plan-${plan.id}`} className="ml-3 text-sm text-gray-900">
                      {plan.name} - ${plan.price_monthly}/month
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex w-full justify-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Submitting...' : 'Join Waiting List'}
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="bg-gray-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Launch Timeline
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              We're working hard to bring you the best financial data API. 
              Join our waiting list to be notified when we launch.
            </p>
            <div className="mt-10 grid grid-cols-1 gap-8 sm:grid-cols-3">
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-600">
                  <span className="text-lg font-semibold text-white">1</span>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">Beta Access</h3>
                <p className="mt-2 text-sm text-gray-600">Early access for waiting list members</p>
              </div>
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-600">
                  <span className="text-lg font-semibold text-white">2</span>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">Public Launch</h3>
                <p className="mt-2 text-sm text-gray-600">Full API access for all users</p>
              </div>
              <div className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-600">
                  <span className="text-lg font-semibold text-white">3</span>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">Advanced Features</h3>
                <p className="mt-2 text-sm text-gray-600">Additional data sources and tools</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WaitingList; 