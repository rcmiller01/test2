import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FaHome, 
  FaMicrophone, 
  FaUser, 
  FaHeart, 
  FaCog, 
  FaBars, 
  FaTimes,
  FaMagic,
  FaBrain,
  FaHandHoldingHeart,
  FaComments,
  FaUserCircle
} from 'react-icons/fa';

const NavContainer = styled.nav`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 2px solid ${props => props.theme.colors.primary};
  box-shadow: ${props => props.theme.shadows.romantic};
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const NavContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 0 1rem;
  }
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: ${props => props.theme.colors.primary};
  font-family: ${props => props.theme.fonts.romantic};
  font-size: 1.8rem;
  font-weight: 700;
  transition: ${props => props.theme.transitions.medium};
  
  &:hover {
    color: ${props => props.theme.colors.accent};
    transform: scale(1.05);
  }
  
  .logo-icon {
    font-size: 2rem;
    animation: heartbeat 2s infinite;
  }
`;

const NavLinks = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    display: none;
  }
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: ${props => props.theme.colors.text};
  font-weight: 500;
  border-radius: ${props => props.theme.borderRadius.small};
  transition: ${props => props.theme.transitions.fast};
  position: relative;
  
  &:hover {
    color: ${props => props.theme.colors.primary};
    background: rgba(233, 30, 99, 0.1);
  }
  
  &.active {
    color: ${props => props.theme.colors.primary};
    background: rgba(233, 30, 99, 0.15);
    box-shadow: ${props => props.theme.shadows.small};
    
    &::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 50%;
      transform: translateX(-50%);
      width: 80%;
      height: 2px;
      background: ${props => props.theme.colors.primary};
      border-radius: 1px;
    }
  }
  
  .nav-icon {
    font-size: 1.1rem;
  }
`;

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: ${props => props.theme.colors.primary};
  cursor: pointer;
  padding: 0.5rem;
  border-radius: ${props => props.theme.borderRadius.small};
  transition: ${props => props.theme.transitions.fast};
  
  &:hover {
    background: rgba(233, 30, 99, 0.1);
  }
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    display: block;
  }
`;

const MobileMenu = styled(motion.div)`
  display: none;
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-bottom: 2px solid ${props => props.theme.colors.primary};
  box-shadow: ${props => props.theme.shadows.large};
  z-index: 999;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    display: block;
  }
`;

const MobileNavLinks = styled.div`
  display: flex;
  flex-direction: column;
  padding: 1rem;
  gap: 0.5rem;
`;

const MobileNavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  text-decoration: none;
  color: ${props => props.theme.colors.text};
  font-weight: 500;
  border-radius: ${props => props.theme.borderRadius.small};
  transition: ${props => props.theme.transitions.fast};
  
  &:hover {
    color: ${props => props.theme.colors.primary};
    background: rgba(233, 30, 99, 0.1);
  }
  
  &.active {
    color: ${props => props.theme.colors.primary};
    background: rgba(233, 30, 99, 0.15);
    box-shadow: ${props => props.theme.shadows.small};
  }
  
  .nav-icon {
    font-size: 1.2rem;
    width: 20px;
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: ${props => props.isConnected ? props.theme.colors.success : props.theme.colors.error};
  color: white;
  border-radius: ${props => props.theme.borderRadius.small};
  font-size: 0.8rem;
  font-weight: 500;
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: white;
    animation: ${props => props.isConnected ? 'pulse' : 'none'} 2s infinite;
  }
`;

const Navigation = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(true); // TODO: Connect to API health check

  const navItems = [
    { path: '/', label: 'Dashboard', icon: FaHome },
    { path: '/chat', label: 'Chat', icon: FaComments },
    { path: '/tts', label: 'Voice Synthesis', icon: FaMicrophone },
    { path: '/avatar', label: 'Avatar', icon: FaUser },
    { path: '/memory', label: 'Memories', icon: FaHeart },
    { path: '/profile', label: 'Profile', icon: FaUserCircle },
    { path: '/settings', label: 'Settings', icon: FaCog },
    { path: '/phase3', label: 'Advanced Features', icon: FaMagic },
  ];

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <NavContainer>
      <NavContent>
        <Logo to="/">
          <FaHandHoldingHeart className="logo-icon" />
          Mia & Solene
        </Logo>

        <NavLinks>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
              >
                <Icon className="nav-icon" />
                {item.label}
              </NavLink>
            );
          })}
        </NavLinks>

        <StatusIndicator isConnected={isConnected}>
          <div className="status-dot" />
          {isConnected ? 'Connected' : 'Disconnected'}
        </StatusIndicator>

        <MobileMenuButton onClick={toggleMobileMenu}>
          {isMobileMenuOpen ? <FaTimes /> : <FaBars />}
        </MobileMenuButton>
      </NavContent>

      <MobileMenu
        initial={{ opacity: 0, y: -20 }}
        animate={{ 
          opacity: isMobileMenuOpen ? 1 : 0, 
          y: isMobileMenuOpen ? 0 : -20 
        }}
        transition={{ duration: 0.3 }}
        style={{ display: isMobileMenuOpen ? 'block' : 'none' }}
      >
        <MobileNavLinks>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <MobileNavLink
                key={item.path}
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
                onClick={closeMobileMenu}
              >
                <Icon className="nav-icon" />
                {item.label}
              </MobileNavLink>
            );
          })}
        </MobileNavLinks>
      </MobileMenu>
    </NavContainer>
  );
};

export default Navigation; 