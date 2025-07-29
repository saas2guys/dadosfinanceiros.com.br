import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { apiService, type Plan } from '../services/api';
import { CheckIcon } from '@heroicons/react/24/outline';

const Plans: React.FC = () => {
  const navigate = useNavigate();
  const [selectedPlan, setSelectedPlan] = useState<number | null>(null);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  const { data: plans, isLoading, error } = useQuery<Plan[]>({
    queryKey: ['plans'],
    queryFn: apiService.getPlans,
    staleTime: 5 * 60 * 1000,
  });

  const handlePlanSelect = (planId: number) => {
    setSelectedPlan(planId);
  };

  const handleJoinWaitingList = () => {
    if (selectedPlan) {
      const plan = plans?.find(p => p.id === selectedPlan);
      const params = new URLSearchParams({
        plan: plan?.name || '',
        billing_cycle: billingCycle,
      });
      navigate(`/waiting-list?${params.toString()}`);
    } else {
      navigate('/waiting-list');
    }
  };

  const getPrice = (plan: Plan) => {
    return billingCycle === 'yearly' ? plan.price_yearly : plan.price_monthly;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !plans) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900">Error loading plans</h2>
            <p className="mt-2 text-gray-600">Please try again later.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 py-24 sm:py-32">
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
                onClick={() => setBillingCycle('monthly')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  billingCycle === 'monthly'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  billingCycle === 'yearly'
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
                  /{billingCycle === 'yearly' ? 'year' : 'month'}
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
              className="rounded-md bg-blue-600 px-6 py-3 text-lg font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
              Join Waiting List for {plans.find(p => p.id === selectedPlan)?.name}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Plans; 