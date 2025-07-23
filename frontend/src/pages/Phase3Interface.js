import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import { 
  FaMagic, 
  FaHeartbeat, 
  FaBrain, 
  FaVrCardboard, 
  FaHandHoldingHeart,
  FaPlay,
  FaPause,
  FaStop,
  FaCog,
  FaChartLine,
  FaThermometerHalf,
  FaHeart,
  FaEye,
  FaHandPaper,
  FaHandRock,
  FaHandScissors,
  FaHandPeace,
  FaHandPointUp,
  FaHandPointDown,
  FaHandPointLeft,
  FaHandPointRight,
  FaMagic,
  FaLightbulb,
  FaUsers,
  FaComments,
  FaShieldAlt,
  FaSync,
  FaDownload,
  FaUpload
} from 'react-icons/fa';

import apiService from '../services/api';

// Styled Components
const Phase3Container = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 1rem;
  }
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 3rem;
  
  h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.secondary});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  p {
    font-size: 1.1rem;
    color: ${props => props.theme.colors.textSecondary};
    max-width: 600px;
    margin: 0 auto;
  }
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
`;

const FeatureCard = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
  transition: ${props => props.theme.transitions.medium};
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: ${props => props.theme.shadows.large};
    border-color: ${props => props.theme.colors.primary}40;
  }
`;

const FeatureHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  
  .feature-icon {
    font-size: 2rem;
    color: ${props => props.theme.colors.primary};
  }
  
  .feature-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: ${props => props.theme.colors.primary};
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  
  .status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: ${props => props.isActive ? props.theme.colors.success : props.theme.colors.error};
    animation: ${props => props.isActive ? 'pulse' : 'none'} 2s infinite;
  }
  
  .status-text {
    font-weight: 500;
    color: ${props => props.isActive ? props.theme.colors.success : props.theme.colors.error};
  }
`;

const ControlGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const ControlButton = styled.button`
  padding: 1rem;
  border: 2px solid ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.textSecondary};
  border-radius: ${props => props.theme.borderRadius.small};
  background: ${props => props.isActive ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.isActive ? 'white' : props.theme.colors.text};
  font-weight: 500;
  cursor: pointer;
  transition: ${props => props.theme.transitions.fast};
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    border-color: ${props => props.theme.colors.primary};
    background: ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.primary}10;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .control-icon {
    font-size: 1.5rem;
  }
  
  .control-label {
    font-size: 0.8rem;
  }
`;

const DataDisplay = styled.div`
  background: linear-gradient(135deg, ${props => props.theme.colors.background}, ${props => props.theme.colors.calm});
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: 1.5rem;
  margin-bottom: 1rem;
  
  .data-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .data-label {
      font-weight: 500;
      color: ${props => props.theme.colors.text};
    }
    
    .data-value {
      font-weight: 600;
      color: ${props => props.theme.colors.primary};
    }
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex-direction: column;
  }
`;

const Button = styled.button`
  flex: 1;
  padding: 1rem 2rem;
  border: none;
  border-radius: ${props => props.theme.borderRadius.medium};
  font-weight: 600;
  cursor: pointer;
  transition: ${props => props.theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  
  &.primary {
    background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.accent});
    color: white;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: ${props => props.theme.shadows.romantic};
    }
    
    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }
  }
  
  &.secondary {
    background: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.primary};
    border: 2px solid ${props => props.theme.colors.primary};
    
    &:hover {
      background: ${props => props.theme.colors.primary};
      color: white;
    }
  }
`;

const InsightsSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
  margin-top: 2rem;
`;

const InsightCard = styled.div`
  background: linear-gradient(135deg, ${props => props.theme.colors.love}, ${props => props.theme.colors.passion});
  color: white;
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: 1.5rem;
  margin-bottom: 1rem;
  
  .insight-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .insight-content {
    opacity: 0.9;
    line-height: 1.6;
  }
`;

const Phase3Interface = () => {
  const [hapticPattern, setHapticPattern] = useState('heartbeat');
  const [hapticIntensity, setHapticIntensity] = useState('moderate');
  const [isBiometricMonitoring, setIsBiometricMonitoring] = useState(false);
  const [vrScene, setVrScene] = useState('romantic_garden');
  const [isVRActive, setIsVRActive] = useState(false);

  const queryClient = useQueryClient();

  // Queries
  const { data: hapticStatus } = useQuery('hapticStatus', apiService.getHapticStatus);
  const { data: romanticSyncStatus } = useQuery('romanticSyncStatus', apiService.getRomanticSyncStatus);
  const { data: vrStatus } = useQuery('vrStatus', apiService.getVRStatus);
  const { data: availableVRScenes } = useQuery('availableVRScenes', apiService.getAvailableVRScenes);
  const { data: relationshipHealth } = useQuery('relationshipHealth', apiService.getRelationshipHealth);
  const { data: relationshipInsights } = useQuery('relationshipInsights', apiService.getRelationshipInsights);

  // Mutations
  const triggerHapticMutation = useMutation(
    (params) => apiService.triggerHapticFeedback(params.pattern, params.intensity),
    {
      onSuccess: () => {
        toast.success('Haptic feedback triggered successfully!');
      },
      onError: () => {
        toast.error('Failed to trigger haptic feedback');
      },
    }
  );

  const startBiometricMutation = useMutation(
    () => apiService.startBiometricMonitoring(),
    {
      onSuccess: () => {
        setIsBiometricMonitoring(true);
        toast.success('Biometric monitoring started!');
      },
      onError: () => {
        toast.error('Failed to start biometric monitoring');
      },
    }
  );

  const startVRMutation = useMutation(
    (sceneType) => apiService.startVRSession(sceneType),
    {
      onSuccess: () => {
        setIsVRActive(true);
        toast.success('VR session started!');
      },
      onError: () => {
        toast.error('Failed to start VR session');
      },
    }
  );

  const hapticPatterns = [
    { key: 'heartbeat', label: 'Heartbeat', icon: FaHeart },
    { key: 'wave', label: 'Wave', icon: FaHandPaper },
    { key: 'pulse', label: 'Pulse', icon: FaHeartbeat },
    { key: 'vibration', label: 'Vibration', icon: FaHandRock },
  ];

  const hapticIntensities = [
    { key: 'light', label: 'Light' },
    { key: 'moderate', label: 'Moderate' },
    { key: 'strong', label: 'Strong' },
    { key: 'intense', label: 'Intense' },
  ];

  const handleHapticTrigger = (pattern, intensity) => {
    triggerHapticMutation.mutate({ pattern, intensity });
  };

  const handleBiometricToggle = () => {
    if (isBiometricMonitoring) {
      setIsBiometricMonitoring(false);
      toast.success('Biometric monitoring stopped');
    } else {
      startBiometricMutation.mutate();
    }
  };

  const handleVRToggle = () => {
    if (isVRActive) {
      setIsVRActive(false);
      toast.success('VR session stopped');
    } else {
      startVRMutation.mutate(vrScene);
    }
  };

  return (
    <Phase3Container>
      <Header>
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Advanced Features
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Experience the future of romantic AI with haptic feedback, biometric monitoring, VR, and relationship AI
        </motion.p>
      </Header>

      <FeatureGrid>
        {/* Haptic Feedback */}
        <FeatureCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <FeatureHeader>
            <FaHandHoldingHeart className="feature-icon" />
            <div className="feature-title">Haptic Feedback</div>
          </FeatureHeader>

          <StatusIndicator isActive={hapticStatus?.status === 'ready'}>
            <div className="status-dot" />
            <span className="status-text">
              {hapticStatus?.status === 'ready' ? 'Ready' : 'Initializing'}
            </span>
          </StatusIndicator>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Pattern</label>
            <ControlGrid>
              {hapticPatterns.map((pattern) => {
                const Icon = pattern.icon;
                return (
                  <ControlButton
                    key={pattern.key}
                    isActive={hapticPattern === pattern.key}
                    onClick={() => setHapticPattern(pattern.key)}
                  >
                    <Icon className="control-icon" />
                    <span className="control-label">{pattern.label}</span>
                  </ControlButton>
                );
              })}
            </ControlGrid>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Intensity</label>
            <ControlGrid>
              {hapticIntensities.map((intensity) => (
                <ControlButton
                  key={intensity.key}
                  isActive={hapticIntensity === intensity.key}
                  onClick={() => setHapticIntensity(intensity.key)}
                >
                  <span className="control-label">{intensity.label}</span>
                </ControlButton>
              ))}
            </ControlGrid>
          </div>

          <ActionButtons>
            <Button
              className="primary"
              onClick={() => handleHapticTrigger(hapticPattern, hapticIntensity)}
              disabled={triggerHapticMutation.isLoading}
            >
              {triggerHapticMutation.isLoading ? <FaPause /> : <FaPlay />}
              {triggerHapticMutation.isLoading ? 'Triggering...' : 'Trigger Haptic'}
            </Button>
            <Button className="secondary">
              <FaCog />
              Settings
            </Button>
          </ActionButtons>
        </FeatureCard>

        {/* Biometric Monitoring */}
        <FeatureCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <FeatureHeader>
            <FaHeartbeat className="feature-icon" />
            <div className="feature-title">Biometric Monitoring</div>
          </FeatureHeader>

          <StatusIndicator isActive={isBiometricMonitoring}>
            <div className="status-dot" />
            <span className="status-text">
              {isBiometricMonitoring ? 'Active' : 'Inactive'}
            </span>
          </StatusIndicator>

          <DataDisplay>
            <div className="data-item">
              <span className="data-label">Heart Rate:</span>
              <span className="data-value">{romanticSyncStatus?.heart_rate || '--'} BPM</span>
            </div>
            <div className="data-item">
              <span className="data-label">Heart Rate Variability:</span>
              <span className="data-value">{romanticSyncStatus?.hrv || '--'} ms</span>
            </div>
            <div className="data-item">
              <span className="data-label">Romantic Sync:</span>
              <span className="data-value">{romanticSyncStatus?.sync_level || '--'}%</span>
            </div>
            <div className="data-item">
              <span className="data-label">Emotional State:</span>
              <span className="data-value">{romanticSyncStatus?.emotional_state || '--'}</span>
            </div>
          </DataDisplay>

          <ActionButtons>
            <Button
              className="primary"
              onClick={handleBiometricToggle}
              disabled={startBiometricMutation.isLoading}
            >
              {startBiometricMutation.isLoading ? <FaPause /> : isBiometricMonitoring ? <FaStop /> : <FaPlay />}
              {startBiometricMutation.isLoading ? 'Starting...' : isBiometricMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
            </Button>
            <Button className="secondary">
              <FaChartLine />
              Analytics
            </Button>
          </ActionButtons>
        </FeatureCard>

        {/* VR Integration */}
        <FeatureCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <FeatureHeader>
            <FaVrCardboard className="feature-icon" />
            <div className="feature-title">VR Experience</div>
          </FeatureHeader>

          <StatusIndicator isActive={isVRActive}>
            <div className="status-dot" />
            <span className="status-text">
              {isVRActive ? 'Active' : 'Inactive'}
            </span>
          </StatusIndicator>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Scene</label>
            <select
              value={vrScene}
              onChange={(e) => setVrScene(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '2px solid #757575',
                borderRadius: '8px',
                fontSize: '1rem'
              }}
            >
              <option value="romantic_garden">Romantic Garden</option>
              <option value="sunset_beach">Sunset Beach</option>
              <option value="mountain_cabin">Mountain Cabin</option>
              <option value="starry_night">Starry Night</option>
            </select>
          </div>

          <DataDisplay>
            <div className="data-item">
              <span className="data-label">VR Status:</span>
              <span className="data-value">{vrStatus?.status || '--'}</span>
            </div>
            <div className="data-item">
              <span className="data-label">Current Scene:</span>
              <span className="data-value">{vrScene.replace('_', ' ')}</span>
            </div>
            <div className="data-item">
              <span className="data-label">Session Duration:</span>
              <span className="data-value">{vrStatus?.session_duration || '--'}</span>
            </div>
          </DataDisplay>

          <ActionButtons>
            <Button
              className="primary"
              onClick={handleVRToggle}
              disabled={startVRMutation.isLoading}
            >
              {startVRMutation.isLoading ? <FaPause /> : isVRActive ? <FaStop /> : <FaPlay />}
              {startVRMutation.isLoading ? 'Starting...' : isVRActive ? 'Stop VR' : 'Start VR'}
            </Button>
            <Button className="secondary">
              <FaCog />
              VR Settings
            </Button>
          </ActionButtons>
        </FeatureCard>

        {/* Relationship AI */}
        <FeatureCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <FeatureHeader>
            <FaBrain className="feature-icon" />
            <div className="feature-title">Relationship AI</div>
          </FeatureHeader>

          <StatusIndicator isActive={relationshipHealth?.status === 'active'}>
            <div className="status-dot" />
            <span className="status-text">
              {relationshipHealth?.status === 'active' ? 'Active' : 'Inactive'}
            </span>
          </StatusIndicator>

          <DataDisplay>
            <div className="data-item">
              <span className="data-label">Overall Score:</span>
              <span className="data-value">{relationshipHealth?.overall_score || '--'}/100</span>
            </div>
            <div className="data-item">
              <span className="data-label">Communication:</span>
              <span className="data-value">{relationshipHealth?.communication_score || '--'}/100</span>
            </div>
            <div className="data-item">
              <span className="data-label">Emotional Bond:</span>
              <span className="data-value">{relationshipHealth?.emotional_bond_score || '--'}/100</span>
            </div>
            <div className="data-item">
              <span className="data-label">Trust Level:</span>
              <span className="data-value">{relationshipHealth?.trust_score || '--'}/100</span>
            </div>
          </DataDisplay>

          <ActionButtons>
            <Button className="primary">
              <FaLightbulb />
              Get Advice
            </Button>
            <Button className="secondary">
              <FaChartLine />
              Analytics
            </Button>
          </ActionButtons>
        </FeatureCard>
      </FeatureGrid>

      <InsightsSection
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
      >
        <h3 style={{ marginBottom: '1.5rem', color: '#E91E63' }}>
          <FaLightbulb style={{ marginRight: '0.5rem' }} />
          AI Insights & Recommendations
        </h3>
        
        {relationshipInsights?.insights?.map((insight, index) => (
          <InsightCard key={index}>
            <div className="insight-title">
              <FaMagic />
              {insight.title}
            </div>
            <div className="insight-content">
              {insight.content}
            </div>
          </InsightCard>
        ))}
        
        {(!relationshipInsights?.insights || relationshipInsights.insights.length === 0) && (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#757575' }}>
            <FaBrain style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.3 }} />
            <p>AI insights and recommendations will appear here</p>
            <p style={{ fontSize: '0.9rem' }}>
              Use the advanced features to generate personalized relationship insights
            </p>
          </div>
        )}
      </InsightsSection>
    </Phase3Container>
  );
};

export default Phase3Interface; 