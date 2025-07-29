import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import Plans from './pages/Plans'
import FAQ from './pages/FAQ'
import ApiDocs from './pages/ApiDocs'
import WaitingList from './pages/WaitingList'
import WaitingListSuccess from './pages/WaitingListSuccess'
import SubscriptionSuccess from './pages/SubscriptionSuccess'

import StockMarketApi from './pages/apis/StockMarketApi'
import ForexApi from './pages/apis/ForexApi'
import CryptoApi from './pages/apis/CryptoApi'
import IndicesApi from './pages/apis/IndicesApi'
import OptionsApi from './pages/apis/OptionsApi'
import FuturesApi from './pages/apis/FuturesApi'
import CommoditiesApi from './pages/apis/CommoditiesApi'
import EconomicIndicatorsApi from './pages/apis/EconomicIndicatorsApi'
import FundamentalsApi from './pages/apis/FundamentalsApi'
import NewsApi from './pages/apis/NewsApi'
import TechnicalAnalysisApi from './pages/apis/TechnicalAnalysisApi'
import EarningsApi from './pages/apis/EarningsApi'

function App() {
  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/plans" element={<Plans />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/api-docs" element={<ApiDocs />} />
          <Route path="/waiting-list" element={<WaitingList />} />
          <Route path="/waiting-list-success" element={<WaitingListSuccess />} />
          <Route path="/subscription-success" element={<SubscriptionSuccess />} />
          
          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
          
          <Route path="/apis/stock-market" element={<StockMarketApi />} />
          <Route path="/apis/forex" element={<ForexApi />} />
          <Route path="/apis/crypto" element={<CryptoApi />} />
          <Route path="/apis/indices" element={<IndicesApi />} />
          <Route path="/apis/options" element={<OptionsApi />} />
          <Route path="/apis/futures" element={<FuturesApi />} />
          <Route path="/apis/commodities" element={<CommoditiesApi />} />
          <Route path="/apis/economic-indicators" element={<EconomicIndicatorsApi />} />
          <Route path="/apis/fundamentals" element={<FundamentalsApi />} />
          <Route path="/apis/news" element={<NewsApi />} />
          <Route path="/apis/technical-analysis" element={<TechnicalAnalysisApi />} />
          <Route path="/apis/earnings" element={<EarningsApi />} />
        </Routes>
      </Layout>
    </AuthProvider>
  )
}

export default App 