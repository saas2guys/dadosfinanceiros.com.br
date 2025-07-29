import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Bars3Icon,
  XMarkIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const { isAuthenticated, logout } = useAuth();
  const location = useLocation();

  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Plans', href: '/plans' },
    { name: 'API Docs', href: '/api-docs' },
    { name: 'FAQ', href: '/faq' },
  ];

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="flex flex-col min-h-screen">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <nav className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8" aria-label="Global">
          <div className="flex lg:flex-1">
            <Link to="/" className="-m-1.5 p-1.5 flex items-center">
              <ChartBarIcon className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">Financial Data API</span>
            </Link>
          </div>
          <div className="flex lg:hidden">
            <button
              type="button"
              className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700"
              onClick={() => setMobileMenuOpen(true)}
            >
              <span className="sr-only">Open main menu</span>
              <Bars3Icon className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div className="hidden lg:flex lg:gap-x-12">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`text-sm font-semibold leading-6 ${
                  location.pathname === item.href
                    ? 'text-blue-600'
                    : 'text-gray-900 hover:text-blue-600'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </div>
          <div className="hidden lg:flex lg:flex-1 lg:justify-end lg:gap-x-4">
            {isAuthenticated ? (
              <>
                <Link
                  to="/profile"
                  className="text-sm font-semibold leading-6 text-gray-900 hover:text-blue-600"
                >
                  Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-sm font-semibold leading-6 text-gray-900 hover:text-blue-600"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/waiting-list"
                  className="text-sm font-semibold leading-6 text-gray-900 hover:text-blue-600"
                >
                  Join Waiting List
                </Link>
                <Link
                  to="/waiting-list"
                  className="text-sm font-semibold leading-6 text-gray-900 hover:text-blue-600"
                >
                  Get Early Access
                </Link>
              </>
            )}
          </div>
        </nav>
        
        <div className={`lg:hidden ${mobileMenuOpen ? 'block' : 'hidden'}`}>
          <div className="fixed inset-0 z-50" />
          <div className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-white px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10">
            <div className="flex items-center justify-between">
              <Link to="/" className="-m-1.5 p-1.5 flex items-center">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">Financial Data API</span>
              </Link>
              <button
                type="button"
                className="-m-2.5 rounded-md p-2.5 text-gray-700"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="sr-only">Close menu</span>
                <XMarkIcon className="h-6 w-6" aria-hidden="true" />
              </button>
            </div>
            <div className="mt-6 flow-root">
              <div className="-my-6 divide-y divide-gray-500/10">
                <div className="space-y-2 py-6">
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 ${
                        location.pathname === item.href
                          ? 'text-blue-600 bg-blue-50'
                          : 'text-gray-900 hover:bg-gray-50'
                      }`}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
                <div className="py-6">
                  {isAuthenticated ? (
                    <>
                      <Link
                        to="/profile"
                        className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        Profile
                      </Link>
                      <button
                        onClick={() => {
                          handleLogout();
                          setMobileMenuOpen(false);
                        }}
                        className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50 w-full text-left"
                      >
                        Logout
                      </button>
                    </>
                  ) : (
                    <>
                      <Link
                        to="/waiting-list"
                        className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        Join Waiting List
                      </Link>
                      <Link
                        to="/waiting-list"
                        className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        Get Early Access
                      </Link>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {children}
      </main>

      <footer className="bg-gray-900">
        <div className="mx-auto max-w-7xl px-6 py-12 md:flex md:items-center md:justify-between lg:px-8">
          <div className="flex justify-center space-x-6 md:order-2">
            <Link to="/" className="text-gray-400 hover:text-gray-300">
              Home
            </Link>
            <Link to="/plans" className="text-gray-400 hover:text-gray-300">
              Plans
            </Link>
            <Link to="/api-docs" className="text-gray-400 hover:text-gray-300">
              API Docs
            </Link>
            <Link to="/faq" className="text-gray-400 hover:text-gray-300">
              FAQ
            </Link>
          </div>
          <div className="mt-8 md:order-1 md:mt-0">
            <p className="text-center text-xs leading-5 text-gray-400">
              &copy; 2024 Financial Data API. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout; 