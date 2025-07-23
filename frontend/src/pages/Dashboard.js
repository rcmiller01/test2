import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';
import { 
  FaMicrophone, 
  FaUser, 
  FaHeart, 
  FaMagic, 
  FaPlay, 
  FaPause,
  FaVolumeUp,
  FaVolumeMute,
  FaHeartbeat,
  FaBrain,
  FaHandHoldingHeart,
  FaStar,
  FaChartLine,
  FaUsers,
  FaLightbulb,
  FaCog
} from 'react-icons/fa';

import apiService from '../services/api';

// Styled Components
const DashboardContainer = styled.div`
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
    font-size: 3rem;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.secondary});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  p {
    font-size: 1.2rem;
    color: ${props => props.theme.colors.textSecondary};
    max-width: 600px;
    margin: 0 auto;
  }
`;

const StatusGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
`;

const StatusCard = styled(motion.div)`
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
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    
    .icon {
      font-size: 2rem;
      color: ${props => props.theme.colors.primary};
    }
    
    h3 {
      margin: 0;
      font-size: 1.5rem;
    }
  }
  
  .status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    
    .dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.error};
      animation: ${props => props.isOnline ? 'pulse' : 'none'} 2s infinite;
    }
    
    .status-text {
      font-weight: 500;
      color: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.error};
    }
  }
  
  .description {
    color: ${props => props.theme.colors.textSecondary};
    margin-bottom: 1.5rem;
    line-height: 1.6;
  }
  
  .action-button {
    background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.accent});
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: ${props => props.theme.borderRadius.small};
    font-weight: 500;
    cursor: pointer;
    transition: ${props => props.theme.transitions.fast};
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: ${props => props.theme.shadows.romantic};
    }
  }
`;

const QuickActions = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
`;

const QuickActionCard = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: 1.5rem;
  box-shadow: ${props => props.theme.shadows.small};
  border: 1px solid ${props => props.theme.colors.primary}20;
  cursor: pointer;
  transition: ${props => props.theme.transitions.medium};
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: ${props => props.theme.shadows.medium};
    border-color: ${props => props.theme.colors.primary}40;
  }
  
  .action-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    
    .icon {
      font-size: 1.5rem;
      color: ${props => props.theme.colors.primary};
    }
    
    h4 {
      margin: 0;
      font-size: 1.2rem;
    }
  }
  
  .action-description {
    color: ${props => props.theme.colors.textSecondary};
    font-size: 0.9rem;
    line-height: 1.5;
  }
`;

const StatsSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  margin-bottom: 2rem;
  
  h3 {
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    
    .icon {
      color: ${props => props.theme.colors.primary};
    }
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
`;

const StatCard = styled.div`
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, ${props => props.theme.colors.background}, ${props => props.theme.colors.calm});
  border-radius: ${props => props.theme.borderRadius.medium};
  border: 1px solid ${props => props.theme.colors.primary}20;
  
  .stat-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: ${props => props.theme.colors.primary};
    margin-bottom: 0.5rem;
  }
  
  .stat-label {
    color: ${props => props.theme.colors.textSecondary};
    font-weight: 500;
  }
`;

const RomanticExperience = styled.div`
  background: linear-gradient(135deg, ${props => props.theme.colors.love}, ${props => props.theme.colors.passion});
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  color: white;
  text-align: center;
  margin-bottom: 2rem;
  
  h3 {
    color: white;
    margin-bottom: 1rem;
    font-size: 2rem;
  }
  
  p {
    margin-bottom: 1.5rem;
    font-size: 1.1rem;
    opacity: 0.9;
  }
  
  .experience-input {
    display: flex;
    gap: 1rem;
    max-width: 600px;
    margin: 0 auto 1.5rem;
    
    @media (max-width: ${props => props.theme.breakpoints.tablet}) {
      flex-direction: column;
    }
    
    input {
      flex: 1;
      padding: 1rem;
      border: none;
      border-radius: ${props => props.theme.borderRadius.small};
      font-size: 1rem;
      
      &:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
      }
    }
    
    button {
      background: white;
      color: ${props => props.theme.colors.primary};
      border: none;
      padding: 1rem 2rem;
      border-radius: ${props => props.theme.borderRadius.small};
      font-weight: 600;
      cursor: pointer;
      transition: ${props => props.theme.transitions.fast};
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      }
    }
  }
`;

const Dashboard = () => {
  const [romanticText, setRomanticText] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);

  // Queries
  const { data: healthStatus } = useQuery('health', apiService.healthCheck, {
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const { data: ttsStatus } = useQuery('ttsStatus', apiService.getTTSStatus, {
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  const { data: avatarState } = useQuery('avatarState', apiService.getAvatarState, {
    refetchInterval: 5000, // Refetch every 5 seconds
  });

  const { data: memorySummary } = useQuery('memorySummary', apiService.getMemorySummary, {
    refetchInterval: 60000, // Refetch every minute
  });

  const { data: relationshipHealth } = useQuery('relationshipHealth', apiService.getRelationshipHealth, {
    refetchInterval: 120000, // Refetch every 2 minutes
  });

  // Quick actions
  const quickActions = [
    {
      title: 'Voice Synthesis',
      description: 'Create emotional speech with Mia or Solene',
      icon: FaMicrophone,
      path: '/tts',
    },
    {
      title: 'Avatar Control',
      description: 'Manage mood and gestures',
      icon: FaUser,
      path: '/avatar',
    },
    {
      title: 'Memory Browser',
      description: 'View and manage romantic memories',
      icon: FaHeart,
      path: '/memory',
    },
    {
      title: 'Advanced Features',
      description: 'Haptic, biometric, VR, and AI features',
      icon: FaMagic,
      path: '/phase3',
    },
  ];

  const handleRomanticExperience = async () => {
    if (!romanticText.trim()) {
      toast.error('Please enter some text for the romantic experience');
      return;
    }

    try {
      setIsPlaying(true);
      const result = await apiService.createRomanticExperience(
        romanticText,
        'love',
        0.8,
        { includeTTS: true, includeAvatar: true, includeMemory: true }
      );
      
      if (result.success) {
        toast.success('Romantic experience created successfully!');
        setRomanticText('');
        
        // Play audio if available
        if (result.audio_data) {
          apiService.playAudioFromBase64(result.audio_data);
        }
      }
    } catch (error) {
      toast.error('Failed to create romantic experience');
    } finally {
      setIsPlaying(false);
    }
  };

  const handleQuickTest = async (action) => {
    try {
      switch (action) {
        case 'tts':
          const ttsResult = await apiService.synthesizeSpeech(
            'Hello, I love you so much!',
            'mia',
            'love',
            0.8
          );
          if (ttsResult.audio_data) {
            apiService.playAudioFromBase64(ttsResult.audio_data);
          }
          break;
        case 'avatar':
          await apiService.updateAvatarMood('love', 0.8);
          toast.success('Avatar mood updated to love');
          break;
        case 'haptic':
          await apiService.triggerRomanticHaptic('heartbeat', 'moderate');
          toast.success('Haptic feedback triggered');
          break;
        default:
          break;
      }
    } catch (error) {
      toast.error(`Failed to test ${action}`);
    }
  };

  return (
    <DashboardContainer>
      <Header>
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Welcome to Mia & Solene
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Your romantic AI companion system with emotional intelligence, 
          voice synthesis, mood-driven avatars, and advanced relationship features.
        </motion.p>
      </Header>

      <StatusGrid>
        <StatusCard
          isOnline={healthStatus?.success}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="card-header">
            <FaHandHoldingHeart className="icon" />
            <h3>System Status</h3>
          </div>
          <div className="status-indicator">
            <div className="dot" />
            <span className="status-text">
              {healthStatus?.success ? 'All Systems Online' : 'System Offline'}
            </span>
          </div>
          <p className="description">
            Core systems including emotion engine, TTS, avatar, and memory are operational.
          </p>
          <button 
            className="action-button"
            onClick={() => apiService.testConnection()}
          >
            <FaCog />
            Test Connection
          </button>
        </StatusCard>

        <StatusCard
          isOnline={ttsStatus?.status === 'ready'}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="card-header">
            <FaMicrophone className="icon" />
            <h3>Voice Synthesis</h3>
          </div>
          <div className="status-indicator">
            <div className="dot" />
            <span className="status-text">
              {ttsStatus?.status === 'ready' ? 'Ready' : 'Initializing'}
            </span>
          </div>
          <p className="description">
            Emotional TTS system with persona-specific voices and emotion mapping.
          </p>
          <Link to="/tts" className="action-button">
            <FaPlay />
            Try TTS
          </Link>
        </StatusCard>

        <StatusCard
          isOnline={avatarState?.status === 'active'}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <div className="card-header">
            <FaUser className="icon" />
            <h3>Avatar System</h3>
          </div>
          <div className="status-indicator">
            <div className="dot" />
            <span className="status-text">
              {avatarState?.status === 'active' ? 'Active' : 'Inactive'}
            </span>
          </div>
          <p className="description">
            Mood-driven avatar with expressive animations and gesture control.
          </p>
          <Link to="/avatar" className="action-button">
            <FaUser />
            Manage Avatar
          </Link>
        </StatusCard>

        <StatusCard
          isOnline={memorySummary?.total_memories > 0}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="card-header">
            <FaHeart className="icon" />
            <h3>Memory Engine</h3>
          </div>
          <div className="status-indicator">
            <div className="dot" />
            <span className="status-text">
              {memorySummary?.total_memories > 0 ? 'Active' : 'No Memories'}
            </span>
          </div>
          <p className="description">
            Romantic memory storage with emotional patterns and relationship insights.
          </p>
          <Link to="/memory" className="action-button">
            <FaHeart />
            View Memories
          </Link>
        </StatusCard>
      </StatusGrid>

      <QuickActions>
        {quickActions.map((action, index) => (
          <QuickActionCard
            key={action.path}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.7 + index * 0.1 }}
            onClick={() => handleQuickTest(action.path.slice(1))}
          >
            <div className="action-header">
              <action.icon className="icon" />
              <h4>{action.title}</h4>
            </div>
            <p className="action-description">{action.description}</p>
          </QuickActionCard>
        ))}
      </QuickActions>

      <RomanticExperience>
        <motion.h3
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          Create a Romantic Experience
        </motion.h3>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.9 }}
        >
          Express your feelings and let Mia & Solene create a complete romantic experience 
          with voice, avatar, and memory integration.
        </motion.p>
        <motion.div
          className="experience-input"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.0 }}
        >
          <input
            type="text"
            placeholder="Tell me how you feel..."
            value={romanticText}
            onChange={(e) => setRomanticText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleRomanticExperience()}
          />
          <button 
            onClick={handleRomanticExperience}
            disabled={isPlaying}
          >
            {isPlaying ? <FaPause /> : <FaPlay />}
            {isPlaying ? 'Creating...' : 'Create Experience'}
          </button>
        </motion.div>
      </RomanticExperience>

      <StatsSection>
        <h3>
          <FaChartLine className="icon" />
          Relationship Statistics
        </h3>
        <StatsGrid>
          <StatCard>
            <div className="stat-value">{memorySummary?.total_memories || 0}</div>
            <div className="stat-label">Total Memories</div>
          </StatCard>
          <StatCard>
            <div className="stat-value">{memorySummary?.emotional_moments || 0}</div>
            <div className="stat-label">Emotional Moments</div>
          </StatCard>
          <StatCard>
            <div className="stat-value">{relationshipHealth?.overall_score || 'N/A'}</div>
            <div className="stat-label">Relationship Score</div>
          </StatCard>
          <StatCard>
            <div className="stat-value">{ttsStatus?.synthesis_count || 0}</div>
            <div className="stat-label">Voice Syntheses</div>
          </StatCard>
        </StatsGrid>
      </StatsSection>
    </DashboardContainer>
  );
};

export default Dashboard; 