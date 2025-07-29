import axios, { type AxiosInstance, type AxiosResponse } from 'axios';

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
  request_token: string;
  token_auto_renew: boolean;
  token_validity_days: number;
  current_period_start?: string;
  current_period_end?: string;
  subscription_started_at?: string;
  payment_failed_at?: string;
}

export interface Feature {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
}

export interface Plan {
  id: number;
  name: string;
  description: string;
  price_monthly: number;
  price_yearly?: number;
  daily_request_limit: number;
  hourly_request_limit: number;
  monthly_request_limit: number;
  burst_limit: number;
  features: Feature[];
  is_active: boolean;
  is_free: boolean;
  is_metered: boolean;
  stripe_price_id?: string;
  stripe_yearly_price_id?: string;
  created_at: string;
  updated_at: string;
}

export interface TokenHistory {
  id: number;
  token: string;
  created_at: string;
  expires_at?: string;
  is_active: boolean;
  never_expires: boolean;
  is_current: boolean;
  status_display: string;
}

export interface Subscription {
  id: string;
  status: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  plan: Plan;
}

export interface CheckoutSession {
  id: string;
  url: string;
}

export interface FinancialDataResponse {
  data: Record<string, unknown>;
  status: string;
  message?: string;
}

export interface DailyUsage {
  made: number;
  limit: number;
  remaining: number;
  percentage: number;
}

export interface UserProfile extends User {
  current_plan?: Plan;
  subscription_status: string;
  subscription_expires_at?: string;
  subscription_days_remaining?: number;
  is_subscription_active: boolean;
  daily_request_limit: number;
  daily_requests_made: number;
  requests_remaining: number;
  request_token: string;
  request_token_created: string;
  request_token_expires?: string;
  token_never_expires: boolean;
  token_auto_renew: boolean;
  token_validity_days: number;
  previous_tokens: string[];
}

export interface HomePageData {
  plans: Plan[];
  all_features: Feature[];
  current_plan?: Plan;
  user?: UserProfile;
}

export interface ProfilePageData {
  user: UserProfile;
  token_info: {
    request_token: string;
    token: string;
    created: string;
    expires?: string;
    never_expires: boolean;
    auto_renew: boolean;
    validity_days: number;
    is_expired: boolean;
    previous_tokens: string[];
  };
  all_tokens: TokenHistory[];
  daily_usage: DailyUsage;
  plans: Plan[];
  current_plan?: Plan;
  plan_id_map: Record<string, number>;
}

export interface WaitingListData {
  plans: Plan[];
}

const getApiBaseUrl = (): string => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  if (import.meta.env.PROD) {
    const currentOrigin = window.location.origin;
    
    if (currentOrigin.includes('ondigitalocean.app')) {
      return '';
    }
    
    return 'https://api.dadosfinanceiros.com.br';
  }
  
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await this.refreshToken(refreshToken);
              localStorage.setItem('access_token', response.data.access);
              originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
              return this.api(originalRequest);
            }
          } catch {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  async login(email: string, password: string): Promise<AxiosResponse> {
    return this.api.post('/api/token/', { email, password });
  }

  async register(userData: {
    email: string;
    password: string;
    username: string;
    first_name: string;
    last_name: string;
  }): Promise<AxiosResponse> {
    return this.api.post('/api/register/', userData);
  }

  async refreshToken(refreshToken: string): Promise<AxiosResponse> {
    return this.api.post('/api/token/refresh/', { refresh: refreshToken });
  }

  async verifyToken(token: string): Promise<AxiosResponse> {
    return this.api.post('/api/token/verify/', { token });
  }

  async getUserProfile(): Promise<AxiosResponse<User>> {
    return this.api.get('/api/profile/');
  }

  async updateUserProfile(userData: Partial<User>): Promise<AxiosResponse<User>> {
    return this.api.patch('/api/profile/', userData);
  }

  async regenerateToken(data: {
    auto_renew?: boolean;
    validity_days?: number;
    save_old?: boolean;
  }): Promise<AxiosResponse> {
    return this.api.post('/api/regenerate-token/', data);
  }

  async getTokenHistory(): Promise<AxiosResponse<TokenHistory[]>> {
    return this.api.get('/api/token-history/');
  }

  async getPlans(): Promise<AxiosResponse<Plan[]>> {
    return this.api.get('/api/plans/');
  }

  async getUserSubscription(): Promise<AxiosResponse<Subscription>> {
    return this.api.get('/api/subscription/');
  }

  async createCheckoutSession(planId: number, billingCycle?: 'monthly' | 'yearly'): Promise<AxiosResponse<CheckoutSession>> {
    const payload: Record<string, unknown> = { plan_id: planId };
    if (billingCycle) {
      payload.billing_cycle = billingCycle;
    }
    return this.api.post('/api/create-checkout-session/', payload);
  }

  async getFinancialData(endpoint: string, params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get(`/api/financial-data/${endpoint}/`, { params });
  }

  async getStockData(symbol: string, params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get(`/api/stock-data/${symbol}/`, { params });
  }

  async getForexData(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/forex-data/', { params });
  }

  async getCryptoData(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/crypto-data/', { params });
  }

  async getIndicesData(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/indices-data/', { params });
  }

  async getOptionsData(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/options-data/', { params });
  }

  async getFuturesData(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/futures-data/', { params });
  }

  async getCommoditiesData(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/commodities-data/', { params });
  }

  async getEconomicIndicators(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/economic-indicators/', { params });
  }

  async getFundamentalsData(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/fundamentals-data/', { params });
  }

  async getNewsData(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/news-data/', { params });
  }

  async getTechnicalAnalysis(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/technical-analysis/', { params });
  }

  async getEarningsData(params?: Record<string, string | number | boolean>): Promise<AxiosResponse<FinancialDataResponse>> {
    return this.api.get('/api/earnings-data/', { params });
  }

  async getHealth(): Promise<AxiosResponse> {
    return this.api.get('/api/health/');
  }

  async getApiDocs(): Promise<AxiosResponse> {
    return this.api.get('/api/docs/');
  }

  async getEndpoints(): Promise<AxiosResponse> {
    return this.api.get('/api/endpoints/');
  }

  async getHomePageData(): Promise<HomePageData> {
    const response = await this.api.get('/api/home-page-data/');
    return response.data;
  }

  async getProfilePageData(): Promise<ProfilePageData> {
    const response = await this.api.get('/api/profile-page-data/');
    return response.data;
  }

  async getWaitingListData(): Promise<WaitingListData> {
    const response = await this.api.get('/api/waiting-list-data/');
    return response.data;
  }

  async getFeatures(): Promise<Feature[]> {
    const response = await this.api.get('/api/features/');
    return response.data;
  }
}

export const apiService = new ApiService(); 