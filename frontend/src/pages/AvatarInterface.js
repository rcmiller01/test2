import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import { 
  FaUser, 
  FaHeart, 
  FaSmile, 
  FaSadTear, 
  FaAngry, 
  FaSurprise,
  FaMeh,
  FaMagic,
  FaHandPaper,
  FaHandRock,
  FaHandScissors,
  FaHandPeace,
  FaHandPointUp,
  FaHandPointDown,
  FaHandPointLeft,
  FaHandPointRight,
  FaEye,
  FaEyeSlash,
  FaPalette,
  FaCog,
  FaSync,
  FaPlay,
  FaPause,
  FaStop,
  FaCamera,
  FaDownload,
  FaUpload
} from 'react-icons/fa';

import apiService from '../services/api';

// Styled Components
const AvatarContainer = styled.div`
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

const MainGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
  }
`;

const ControlPanel = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
  height: fit-content;
`;

const AvatarDisplay = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

const SectionTitle = styled.h3`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  color: ${props => props.theme.colors.primary};
  
  .icon {
    font-size: 1.5rem;
  }
`;

const AvatarPreview = styled.div`
  width: 300px;
  height: 400px;
  background: linear-gradient(135deg, ${props => props.theme.colors.background}, ${props => props.theme.colors.calm});
  border-radius: ${props => props.theme.borderRadius.large};
  border: 3px solid ${props => props.theme.colors.primary}30;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
  
  .avatar-placeholder {
    text-align: center;
    color: ${props => props.theme.colors.primary};
    
    .avatar-icon {
      font-size: 8rem;
      margin-bottom: 1rem;
      opacity: 0.7;
    }
    
    .avatar-text {
      font-size: 1.2rem;
      font-weight: 500;
    }
  }
  
  .mood-indicator {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: ${props => props.currentMood === 'love' ? '#E91E63' : 
                  props.currentMood === 'joy' ? '#FF9800' :
                  props.currentMood === 'sadness' ? '#2196F3' :
                  props.currentMood === 'anger' ? '#F44336' :
                  props.currentMood === 'surprise' ? '#9C27B0' : '#757575'};
    animation: pulse 2s infinite;
  }
`;

const MoodSelector = styled.div`
  margin-bottom: 2rem;
  
  .mood-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    gap: 0.75rem;
  }
`;

const MoodButton = styled.button`
  padding: 1rem 0.5rem;
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
  
  .mood-icon {
    font-size: 1.5rem;
  }
  
  .mood-label {
    font-size: 0.7rem;
  }
`;

const IntensitySlider = styled.div`
  margin-bottom: 2rem;
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: ${props => props.theme.colors.text};
  }
  
  .slider-container {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  input[type="range"] {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: ${props => props.theme.colors.background};
    outline: none;
    -webkit-appearance: none;
    
    &::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: ${props => props.theme.colors.primary};
      cursor: pointer;
      box-shadow: ${props => props.theme.shadows.small};
    }
    
    &::-moz-range-thumb {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: ${props => props.theme.colors.primary};
      cursor: pointer;
      border: none;
      box-shadow: ${props => props.theme.shadows.small};
    }
  }
  
  .intensity-value {
    min-width: 60px;
    text-align: center;
    font-weight: 600;
    color: ${props => props.theme.colors.primary};
  }
`;

const GestureSelector = styled.div`
  margin-bottom: 2rem;
  
  .gesture-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
    gap: 0.5rem;
  }
`;

const GestureButton = styled.button`
  padding: 0.75rem 0.5rem;
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
  gap: 0.25rem;
  
  &:hover {
    border-color: ${props => props.theme.colors.primary};
    background: ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.primary}10;
  }
  
  .gesture-icon {
    font-size: 1.2rem;
  }
  
  .gesture-label {
    font-size: 0.6rem;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Button = styled.button`
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
  
  &.danger {
    background: ${props => props.theme.colors.error};
    color: white;
    
    &:hover {
      background: #D32F2F;
      transform: translateY(-2px);
    }
  }
`;

const StatusPanel = styled.div`
  background: linear-gradient(135deg, ${props => props.theme.colors.background}, ${props => props.theme.colors.calm});
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: 1.5rem;
  margin-top: 2rem;
  
  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .status-label {
      font-weight: 500;
      color: ${props => props.theme.colors.text};
    }
    
    .status-value {
      font-weight: 600;
      color: ${props => props.theme.colors.primary};
    }
  }
`;

const CustomizationSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
  margin-top: 2rem;
`;

const AvatarInterface = () => {
  const [currentMood, setCurrentMood] = useState('neutral');
  const [moodIntensity, setMoodIntensity] = useState(0.5);
  const [currentGesture, setCurrentGesture] = useState(null);
  const [isAnimating, setIsAnimating] = useState(false);

  const queryClient = useQueryClient();

  // Queries
  const { data: avatarState } = useQuery('avatarState', apiService.getAvatarState, {
    refetchInterval: 2000, // Refetch every 2 seconds
  });

  const { data: customizationOptions } = useQuery('customizationOptions', apiService.getAvatarCustomizationOptions);

  // Mutations
  const updateMoodMutation = useMutation(
    (params) => apiService.updateAvatarMood(params.emotion, params.intensity),
    {
      onSuccess: () => {
        toast.success('Avatar mood updated successfully!');
        queryClient.invalidateQueries('avatarState');
      },
      onError: () => {
        toast.error('Failed to update avatar mood');
      },
    }
  );

  const triggerGestureMutation = useMutation(
    (gesture) => apiService.triggerAvatarGesture(gesture, moodIntensity),
    {
      onSuccess: () => {
        toast.success('Gesture triggered successfully!');
        queryClient.invalidateQueries('avatarState');
      },
      onError: () => {
        toast.error('Failed to trigger gesture');
      },
    }
  );

  const moods = [
    { key: 'love', label: 'Love', icon: FaHeart },
    { key: 'joy', label: 'Joy', icon: FaSmile },
    { key: 'sadness', label: 'Sadness', icon: FaSadTear },
    { key: 'anger', label: 'Anger', icon: FaAngry },
    { key: 'surprise', label: 'Surprise', icon: FaSurprise },
    { key: 'neutral', label: 'Neutral', icon: FaMeh },
  ];

  const gestures = [
    { key: 'wave', label: 'Wave', icon: FaHandPaper },
    { key: 'point_up', label: 'Point Up', icon: FaHandPointUp },
    { key: 'point_down', label: 'Point Down', icon: FaHandPointDown },
    { key: 'point_left', label: 'Point Left', icon: FaHandPointLeft },
    { key: 'point_right', label: 'Point Right', icon: FaHandPointRight },
    { key: 'peace', label: 'Peace', icon: FaHandPeace },
    { key: 'rock', label: 'Rock', icon: FaHandRock },
    { key: 'scissors', label: 'Scissors', icon: FaHandScissors },
  ];

  const handleMoodChange = (mood) => {
    setCurrentMood(mood);
    updateMoodMutation.mutate({
      emotion: mood,
      intensity: moodIntensity,
    });
  };

  const handleGestureTrigger = (gesture) => {
    setCurrentGesture(gesture);
    setIsAnimating(true);
    triggerGestureMutation.mutate(gesture);
    
    // Reset animation state after delay
    setTimeout(() => {
      setIsAnimating(false);
      setCurrentGesture(null);
    }, 3000);
  };

  const handleResetAvatar = () => {
    setCurrentMood('neutral');
    setMoodIntensity(0.5);
    setCurrentGesture(null);
    updateMoodMutation.mutate({
      emotion: 'neutral',
      intensity: 0.5,
    });
  };

  return (
    <AvatarContainer>
      <Header>
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Avatar Management
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Control Mia and Solene's mood, gestures, and appearance in real-time
        </motion.p>
      </Header>

      <MainGrid>
        <ControlPanel
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <SectionTitle>
            <FaUser className="icon" />
            Avatar Controls
          </SectionTitle>

          <MoodSelector>
            <label>Current Mood</label>
            <div className="mood-grid">
              {moods.map((mood) => {
                const Icon = mood.icon;
                return (
                  <MoodButton
                    key={mood.key}
                    isActive={currentMood === mood.key}
                    onClick={() => handleMoodChange(mood.key)}
                  >
                    <Icon className="mood-icon" />
                    <span className="mood-label">{mood.label}</span>
                  </MoodButton>
                );
              })}
            </div>
          </MoodSelector>

          <IntensitySlider>
            <label>Mood Intensity</label>
            <div className="slider-container">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={moodIntensity}
                onChange={(e) => setMoodIntensity(parseFloat(e.target.value))}
              />
              <span className="intensity-value">{Math.round(moodIntensity * 100)}%</span>
            </div>
          </IntensitySlider>

          <GestureSelector>
            <label>Gestures</label>
            <div className="gesture-grid">
              {gestures.map((gesture) => {
                const Icon = gesture.icon;
                return (
                  <GestureButton
                    key={gesture.key}
                    isActive={currentGesture === gesture.key}
                    onClick={() => handleGestureTrigger(gesture.key)}
                    disabled={isAnimating}
                  >
                    <Icon className="gesture-icon" />
                    <span className="gesture-label">{gesture.label}</span>
                  </GestureButton>
                );
              })}
            </div>
          </GestureSelector>

          <ActionButtons>
            <Button
              className="primary"
              onClick={() => handleMoodChange(currentMood)}
              disabled={updateMoodMutation.isLoading}
            >
              {updateMoodMutation.isLoading ? <FaPause /> : <FaPlay />}
              {updateMoodMutation.isLoading ? 'Updating...' : 'Apply Mood'}
            </Button>
            
            <Button className="secondary" onClick={handleResetAvatar}>
              <FaSync />
              Reset Avatar
            </Button>
            
            <Button className="secondary">
              <FaPalette />
              Customize Appearance
            </Button>
            
            <Button className="secondary">
              <FaCamera />
              Capture Screenshot
            </Button>
          </ActionButtons>

          <StatusPanel>
            <div className="status-item">
              <span className="status-label">Avatar Status:</span>
              <span className="status-value">
                {avatarState?.status === 'active' ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Current Mood:</span>
              <span className="status-value">{currentMood}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Mood Intensity:</span>
              <span className="status-value">{Math.round(moodIntensity * 100)}%</span>
            </div>
            <div className="status-item">
              <span className="status-label">Last Gesture:</span>
              <span className="status-value">
                {currentGesture ? currentGesture.replace('_', ' ') : 'None'}
              </span>
            </div>
          </StatusPanel>
        </ControlPanel>

        <AvatarDisplay
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <SectionTitle>
            <FaUser className="icon" />
            Avatar Preview
          </SectionTitle>

          <AvatarPreview currentMood={currentMood}>
            <div className="mood-indicator" />
            <div className="avatar-placeholder">
              <FaUser className="avatar-icon" />
              <div className="avatar-text">
                {currentMood === 'love' ? 'Mia' : 'Solene'}
              </div>
              <div style={{ fontSize: '0.9rem', marginTop: '0.5rem', opacity: 0.7 }}>
                {currentMood} • {Math.round(moodIntensity * 100)}%
              </div>
              {currentGesture && (
                <div style={{ fontSize: '0.8rem', marginTop: '0.5rem', opacity: 0.6 }}>
                  Gesturing: {currentGesture.replace('_', ' ')}
                </div>
              )}
            </div>
          </AvatarPreview>

          <div style={{ textAlign: 'center', color: '#757575' }}>
            <p>Avatar visualization will appear here</p>
            <p style={{ fontSize: '0.9rem' }}>
              Real-time mood and gesture updates will be reflected in the avatar
            </p>
          </div>
        </AvatarDisplay>
      </MainGrid>

      <CustomizationSection
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <SectionTitle>
          <FaPalette className="icon" />
          Appearance Customization
        </SectionTitle>
        
        <div style={{ textAlign: 'center', color: '#757575', padding: '2rem' }}>
          <FaPalette style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.3 }} />
          <p>Avatar customization options will appear here</p>
          <p style={{ fontSize: '0.9rem' }}>
            Customize hair, eyes, clothing, and other appearance features
          </p>
        </div>
      </CustomizationSection>
    </AvatarContainer>
  );
};

export default AvatarInterface; 