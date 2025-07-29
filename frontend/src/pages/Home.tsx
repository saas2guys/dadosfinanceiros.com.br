import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { apiService, type HomePageData } from '../services/api';
import {
  CheckIcon,
  StarIcon,
  ArrowRightIcon,
  ChartBarIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  BoltIcon,
} from '@heroicons/react/24/outline';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [selectedPlan, setSelectedPlan] = useState<number | null>(null);
  const [selectedBillingCycle, setSelectedBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  const { data: homePageData, isLoading, error } = useQuery<HomePageData>({
    queryKey: ['homePageData'],
    queryFn: apiService.getHomePageData,
    staleTime: 5 * 60 * 1000,
  });

  const fallbackData: HomePageData = {
    plans: [
      {
        id: 1,
        name: 'Starter',
        description: 'Perfect for developers getting started',
        price_monthly: 29,
        price_yearly: 290,
        daily_request_limit: 1000,
        hourly_request_limit: 100,
        monthly_request_limit: 30000,
        burst_limit: 10,
        features: [
          { id: 1, name: 'Real-time Stock Data', description: 'Live stock prices and quotes', is_active: true },
          { id: 2, name: 'Basic API Access', description: 'Core financial data endpoints', is_active: true },
        ],
        is_active: true,
        is_free: false,
        is_metered: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 2,
        name: 'Professional',
        description: 'For growing applications and teams',
        price_monthly: 99,
        price_yearly: 990,
        daily_request_limit: 10000,
        hourly_request_limit: 1000,
        monthly_request_limit: 300000,
        burst_limit: 100,
        features: [
          { id: 1, name: 'Real-time Stock Data', description: 'Live stock prices and quotes', is_active: true },
          { id: 2, name: 'Advanced API Access', description: 'All financial data endpoints', is_active: true },
          { id: 3, name: 'Historical Data', description: 'Historical price data and charts', is_active: true },
          { id: 4, name: 'WebSocket Feeds', description: 'Real-time data streaming', is_active: true },
        ],
        is_active: true,
        is_free: false,
        is_metered: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 3,
        name: 'Enterprise',
        description: 'For large-scale applications',
        price_monthly: 299,
        price_yearly: 2990,
        daily_request_limit: 100000,
        hourly_request_limit: 10000,
        monthly_request_limit: 3000000,
        burst_limit: 1000,
        features: [
          { id: 1, name: 'Real-time Stock Data', description: 'Live stock prices and quotes', is_active: true },
          { id: 2, name: 'Advanced API Access', description: 'All financial data endpoints', is_active: true },
          { id: 3, name: 'Historical Data', description: 'Historical price data and charts', is_active: true },
          { id: 4, name: 'WebSocket Feeds', description: 'Real-time data streaming', is_active: true },
          { id: 5, name: 'Custom Integrations', description: 'Dedicated support and custom solutions', is_active: true },
          { id: 6, name: 'Priority Support', description: '24/7 dedicated support team', is_active: true },
        ],
        is_active: true,
        is_free: false,
        is_metered: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ],
    all_features: [
      { id: 1, name: 'Real-time Stock Data', description: 'Live stock prices and quotes', is_active: true },
      { id: 2, name: 'Advanced API Access', description: 'All financial data endpoints', is_active: true },
      { id: 3, name: 'Historical Data', description: 'Historical price data and charts', is_active: true },
      { id: 4, name: 'WebSocket Feeds', description: 'Real-time data streaming', is_active: true },
      { id: 5, name: 'Custom Integrations', description: 'Dedicated support and custom solutions', is_active: true },
      { id: 6, name: 'Priority Support', description: '24/7 dedicated support team', is_active: true },
    ],
  };

  const data = homePageData || fallbackData;
  const plans = data.plans;

  const handlePlanSelect = (planId: number) => {
    setSelectedPlan(planId);
  };

  const handleJoinWaitingList = () => {
    if (selectedPlan) {
      const plan = plans.find(p => p.id === selectedPlan);
      const params = new URLSearchParams({
        plan: plan?.name || '',
        billing_cycle: selectedBillingCycle,
      });
      navigate(`/waiting-list?${params.toString()}`);
    } else {
      navigate('/waiting-list');
    }
  };

  const getPrice = (plan: any) => {
    return selectedBillingCycle === 'yearly' ? plan.price_yearly : plan.price_monthly;
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
              Global Financial Data API
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Access real-time stock data, forex rates, crypto prices, and more. 
              Built for developers who need reliable, fast, and comprehensive financial data.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                to="/plans"
                className="rounded-md bg-blue-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
              >
                View Pricing Plans
              </Link>
              <Link to="/api-docs" className="text-sm font-semibold leading-6 text-gray-900">
                API Documentation <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-blue-600">Why Choose Us</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Everything you need to build financial applications
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Our comprehensive API provides real-time data, historical information, and powerful analytics 
              to help you build the next generation of financial applications.
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
              <div className="flex flex-col">
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                  <ChartBarIcon className="h-5 w-5 flex-none text-blue-600" aria-hidden="true" />
                  Real-time Data
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">Get live stock prices, forex rates, and crypto data with millisecond precision.</p>
                </dd>
              </div>
              <div className="flex flex-col">
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                  <GlobeAltIcon className="h-5 w-5 flex-none text-blue-600" aria-hidden="true" />
                  Global Coverage
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">Access data from major exchanges worldwide, including NYSE, NASDAQ, LSE, and more.</p>
                </dd>
              </div>
              <div className="flex flex-col">
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                  <ShieldCheckIcon className="h-5 w-5 flex-none text-blue-600" aria-hidden="true" />
                  Enterprise Security
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">Bank-level security with SSL encryption, rate limiting, and comprehensive monitoring.</p>
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <div className="bg-white py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Simple, Transparent Pricing
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Choose the plan that fits your needs. All plans include our core features with different usage limits.
            </p>
          </div>

          <div className="mt-16 flex justify-center">
            <div className="relative">
              <div className="flex rounded-lg bg-gray-100 p-1">
                <button
                  onClick={() => setSelectedBillingCycle('monthly')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    selectedBillingCycle === 'monthly'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Monthly
                </button>
                <button
                  onClick={() => setSelectedBillingCycle('yearly')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    selectedBillingCycle === 'yearly'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Yearly
                  <span className="ml-1 text-xs text-blue-600">Save 20%</span>
                </button>
              </div>
            </div>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`relative rounded-3xl p-8 ring-1 ring-gray-200 xl:p-10 ${
                  selectedPlan === plan.id ? 'ring-2 ring-blue-600 bg-blue-50' : 'hover:ring-gray-300'
                }`}
              >
                <div className="flex items-center justify-between gap-x-4">
                  <h3 className="text-lg font-semibold leading-8 text-gray-900">{plan.name}</h3>
                  {plan.name === 'Professional' && (
                    <p className="rounded-full bg-blue-600/10 px-2.5 py-1 text-xs font-semibold leading-5 text-blue-600">
                      Most popular
                    </p>
                  )}
                </div>
                <p className="mt-4 text-sm leading-6 text-gray-600">{plan.description}</p>
                <p className="mt-6 flex items-baseline gap-x-1">
                  <span className="text-4xl font-bold tracking-tight text-gray-900">${getPrice(plan)}</span>
                  <span className="text-sm font-semibold leading-6 text-gray-600">
                    /{selectedBillingCycle === 'yearly' ? 'year' : 'month'}
                  </span>
                </p>
                <ul role="list" className="mt-8 space-y-3 text-sm leading-6 text-gray-600">
                  {plan.features.map((feature) => (
                    <li key={feature.id} className="flex gap-x-3">
                      <CheckIcon className="h-6 w-5 flex-none text-blue-600" aria-hidden="true" />
                      {feature.name}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => handlePlanSelect(plan.id)}
                  className={`mt-8 block w-full rounded-md px-3 py-2 text-center text-sm font-semibold leading-6 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
                    selectedPlan === plan.id
                      ? 'bg-blue-600 text-white focus-visible:outline-blue-600'
                      : 'bg-gray-900 text-white hover:bg-gray-700 focus-visible:outline-gray-900'
                  }`}
                >
                  {selectedPlan === plan.id ? 'Selected' : 'Select Plan'}
                </button>
              </div>
            ))}
          </div>

          {selectedPlan && (
            <div className="mt-12 flex justify-center">
              <button
                onClick={handleJoinWaitingList}
                className="flex items-center gap-x-2 rounded-md bg-blue-600 px-6 py-3 text-lg font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
              >
                Join Waiting List for {plans.find(p => p.id === selectedPlan)?.name}
                <ArrowRightIcon className="h-5 w-5" />
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Ready to get started?
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Join our waiting list to be among the first to access our comprehensive financial data API.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                to="/waiting-list"
                className="rounded-md bg-blue-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
              >
                Join Waiting List
              </Link>
              <Link to="/api-docs" className="text-sm font-semibold leading-6 text-gray-900">
                View API Documentation <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home; 