import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';

// Components
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import TTSInterface from './pages/TTSInterface';
import AvatarInterface from './pages/AvatarInterface';
import MemoryInterface from './pages/MemoryInterface';
import Phase3Interface from './pages/Phase3Interface';
import Settings from './pages/Settings';
import Chat from './pages/Chat';
import Profile from './pages/Profile';

// Theme
const theme = {
  colors: {
    primary: '#E91E63',      // Romantic Pink
    secondary: '#9C27B0',    // Purple
    accent: '#FF4081',       // Light Pink
    background: '#FFF5F7',   // Very Light Pink
    surface: '#FFFFFF',      // White
    text: '#424242',         // Dark Gray
    textSecondary: '#757575', // Medium Gray
    success: '#4CAF50',      // Green
    error: '#F44336',        // Red
    warning: '#FF9800',      // Orange
    info: '#2196F3',         // Blue
    love: '#E91E63',         // Love Pink
    passion: '#FF1744',      // Passion Red
    tenderness: '#F8BBD9',   // Tenderness Pink
    calm: '#E3F2FD',         // Calm Blue
    excitement: '#FFF3E0',   // Excitement Orange
  },
  fonts: {
    primary: "'Poppins', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    romantic: "'Dancing Script', cursive",
    mono: "'Fira Code', 'Courier New', monospace",
  },
  shadows: {
    small: '0 2px 4px rgba(0,0,0,0.1)',
    medium: '0 4px 8px rgba(0,0,0,0.12)',
    large: '0 8px 16px rgba(0,0,0,0.15)',
    romantic: '0 4px 12px rgba(233, 30, 99, 0.2)',
  },
  borderRadius: {
    small: '8px',
    medium: '12px',
    large: '16px',
    round: '50%',
  },
  transitions: {
    fast: '0.2s ease',
    medium: '0.3s ease',
    slow: '0.5s ease',
  },
  breakpoints: {
    mobile: '480px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1200px',
  }
};

// Global Styles
const GlobalStyle = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Dancing+Script:wght@400;500;600;700&display=swap');
  
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: ${props => props.theme.fonts.primary};
    background: linear-gradient(135deg, ${props => props.theme.colors.background} 0%, #FFE5F0 100%);
    color: ${props => props.theme.colors.text};
    line-height: 1.6;
    min-height: 100vh;
    overflow-x: hidden;
  }
  
  h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    color: ${props => props.theme.colors.primary};
  }
  
  h1 {
    font-family: ${props => props.theme.fonts.romantic};
    font-size: 2.5rem;
    font-weight: 700;
  }
  
  h2 {
    font-size: 2rem;
    margin-bottom: 1rem;
  }
  
  h3 {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
  }
  
  p {
    margin-bottom: 1rem;
  }
  
  a {
    color: ${props => props.theme.colors.primary};
    text-decoration: none;
    transition: ${props => props.theme.transitions.fast};
    
    &:hover {
      color: ${props => props.theme.colors.accent};
    }
  }
  
  button {
    font-family: ${props => props.theme.fonts.primary};
    cursor: pointer;
    border: none;
    outline: none;
    transition: ${props => props.theme.transitions.fast};
  }
  
  input, textarea, select {
    font-family: ${props => props.theme.fonts.primary};
    border: 2px solid ${props => props.theme.colors.textSecondary};
    border-radius: ${props => props.theme.borderRadius.small};
    padding: 0.75rem;
    transition: ${props => props.theme.transitions.fast};
    
    &:focus {
      border-color: ${props => props.theme.colors.primary};
      outline: none;
      box-shadow: 0 0 0 3px rgba(233, 30, 99, 0.1);
    }
  }
  
  /* Custom scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
  }
  
  ::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.background};
  }
  
  ::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.primary};
    border-radius: 4px;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: ${props => props.theme.colors.accent};
  }
  
  /* Animations */
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
  }
  
  @keyframes heartbeat {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.1);
    }
  }
  
  .fade-in {
    animation: fadeIn 0.6s ease-out;
  }
  
  .pulse {
    animation: pulse 2s infinite;
  }
  
  .heartbeat {
    animation: heartbeat 1.5s infinite;
  }
`;

// App Container
const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.main`
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 1rem;
  }
`;

// Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <QueryClientProvider client={queryClient}>
        <Router>
          <AppContainer>
            <Navigation />
            <MainContent>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/tts" element={<TTSInterface />} />
                <Route path="/avatar" element={<AvatarInterface />} />
                <Route path="/memory" element={<MemoryInterface />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/phase3" element={<Phase3Interface />} />
              </Routes>
            </MainContent>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: theme.colors.surface,
                  color: theme.colors.text,
                  border: `1px solid ${theme.colors.primary}`,
                  borderRadius: theme.borderRadius.small,
                  boxShadow: theme.shadows.medium,
                },
                success: {
                  iconTheme: {
                    primary: theme.colors.success,
                    secondary: theme.colors.surface,
                  },
                },
                error: {
                  iconTheme: {
                    primary: theme.colors.error,
                    secondary: theme.colors.surface,
                  },
                },
              }}
            />
          </AppContainer>
        </Router>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App; 