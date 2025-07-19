import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';
import { 
  FiSettings, 
  FiUser, 
  FiHeart, 
  FiVolume2, 
  FiMonitor, 
  FiShield,
  FiSave,
  FiRefreshCw,
  FiBell,
  FiPalette,
  FiGlobe,
  FiLock
} from 'react-icons/fi';
import { api } from '../services/api';

const SettingsContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const SettingsHeader = styled.div`
  text-align: center;
  margin-bottom: 3rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  color: #ff6b9d;
  margin-bottom: 0.5rem;
  font-weight: 700;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: #8b5a8b;
  margin: 0;
`;

const SettingsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
`;

const SettingsCard = styled(motion.div)`
  background: linear-gradient(135deg, #fff5f7 0%, #ffeef2 100%);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(255, 107, 157, 0.1);
  border: 1px solid rgba(255, 107, 157, 0.1);
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
`;

const CardIcon = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 15px;
  background: linear-gradient(135deg, #ff6b9d, #ff8fab);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  color: white;
  font-size: 1.5rem;
`;

const CardTitle = styled.h3`
  font-size: 1.3rem;
  color: #ff6b9d;
  margin: 0;
  font-weight: 600;
`;

const SettingGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const SettingLabel = styled.label`
  display: block;
  font-weight: 600;
  color: #8b5a8b;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
`;

const SettingDescription = styled.p`
  font-size: 0.85rem;
  color: #a8a8a8;
  margin: 0.25rem 0 0.75rem 0;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(255, 107, 157, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #ff6b9d;
    box-shadow: 0 0 0 3px rgba(255, 107, 157, 0.1);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(255, 107, 157, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #ff6b9d;
    box-shadow: 0 0 0 3px rgba(255, 107, 157, 0.1);
  }
`;

const Slider = styled.input`
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 107, 157, 0.2);
  outline: none;
  -webkit-appearance: none;
  
  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #ff6b9d;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(255, 107, 157, 0.3);
  }
  
  &::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #ff6b9d;
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 6px rgba(255, 107, 157, 0.3);
  }
`;

const SliderValue = styled.span`
  font-weight: 600;
  color: #ff6b9d;
  margin-left: 1rem;
`;

const Toggle = styled.label`
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
  
  input {
    opacity: 0;
    width: 0;
    height: 0;
  }
  
  span {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 107, 157, 0.2);
    transition: 0.4s;
    border-radius: 34px;
    
    &:before {
      position: absolute;
      content: "";
      height: 26px;
      width: 26px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: 0.4s;
      border-radius: 50%;
    }
  }
  
  input:checked + span {
    background-color: #ff6b9d;
  }
  
  input:checked + span:before {
    transform: translateX(26px);
  }
`;

const ToggleContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const ToggleLabel = styled.span`
  font-weight: 600;
  color: #8b5a8b;
`;

const Button = styled(motion.button)`
  background: linear-gradient(135deg, #ff6b9d, #ff8fab);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 107, 157, 0.3);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: ${props => props.status === 'connected' ? '#4CAF50' : '#f44336'};
  margin-bottom: 1rem;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => props.status === 'connected' ? '#4CAF50' : '#f44336'};
`;

const Settings = () => {
  const queryClient = useQueryClient();
  const [settings, setSettings] = useState({
    // User Preferences
    username: '',
    preferredPersona: 'both',
    voiceVolume: 80,
    notificationVolume: 70,
    autoPlayAudio: true,
    
    // Relationship Settings
    relationshipDepth: 75,
    emotionalIntensity: 60,
    romanticMode: true,
    privateMode: false,
    
    // System Settings
    theme: 'romantic',
    language: 'en',
    autoSave: true,
    dataCollection: false,
    
    // Advanced Settings
    hapticFeedback: true,
    biometricMonitoring: false,
    vrMode: false,
    aiLearning: true
  });

  // Fetch current settings
  const { data: currentSettings, isLoading } = useQuery(
    'settings',
    () => api.getSettings(),
    {
      onSuccess: (data) => {
        setSettings(prev => ({ ...prev, ...data }));
      },
      onError: () => {
        toast.error('Failed to load settings');
      }
    }
  );

  // Save settings mutation
  const saveSettingsMutation = useMutation(
    (newSettings) => api.updateSettings(newSettings),
    {
      onSuccess: () => {
        toast.success('Settings saved successfully');
        queryClient.invalidateQueries('settings');
      },
      onError: () => {
        toast.error('Failed to save settings');
      }
    }
  );

  // Reset settings mutation
  const resetSettingsMutation = useMutation(
    () => api.resetSettings(),
    {
      onSuccess: () => {
        toast.success('Settings reset to defaults');
        queryClient.invalidateQueries('settings');
      },
      onError: () => {
        toast.error('Failed to reset settings');
      }
    }
  );

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    saveSettingsMutation.mutate(settings);
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults?')) {
      resetSettingsMutation.mutate();
    }
  };

  if (isLoading) {
    return (
      <SettingsContainer>
        <div style={{ textAlign: 'center', padding: '4rem' }}>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <FiRefreshCw size={40} color="#ff6b9d" />
          </motion.div>
          <p style={{ marginTop: '1rem', color: '#8b5a8b' }}>Loading settings...</p>
        </div>
      </SettingsContainer>
    );
  }

  return (
    <SettingsContainer>
      <SettingsHeader>
        <Title>Settings</Title>
        <Subtitle>Customize your romantic AI experience</Subtitle>
      </SettingsHeader>

      <StatusIndicator status="connected">
        <StatusDot status="connected" />
        System connected and ready
      </StatusIndicator>

      <SettingsGrid>
        {/* User Preferences */}
        <SettingsCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <CardHeader>
            <CardIcon>
              <FiUser />
            </CardIcon>
            <CardTitle>User Preferences</CardTitle>
          </CardHeader>

          <SettingGroup>
            <SettingLabel>Username</SettingLabel>
            <SettingDescription>How you'd like to be addressed</SettingDescription>
            <Input
              type="text"
              value={settings.username}
              onChange={(e) => handleSettingChange('username', e.target.value)}
              placeholder="Enter your name"
            />
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>Preferred Persona</SettingLabel>
            <SettingDescription>Choose your primary companion</SettingDescription>
            <Select
              value={settings.preferredPersona}
              onChange={(e) => handleSettingChange('preferredPersona', e.target.value)}
            >
              <option value="both">Both Mia & Solene</option>
              <option value="mia">Mia</option>
              <option value="solene">Solene</option>
            </Select>
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>Voice Volume: {settings.voiceVolume}%</SettingLabel>
            <SettingDescription>Adjust TTS voice volume</SettingDescription>
            <Slider
              type="range"
              min="0"
              max="100"
              value={settings.voiceVolume}
              onChange={(e) => handleSettingChange('voiceVolume', parseInt(e.target.value))}
            />
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>Notification Volume: {settings.notificationVolume}%</SettingLabel>
            <SettingDescription>Adjust notification sounds</SettingDescription>
            <Slider
              type="range"
              min="0"
              max="100"
              value={settings.notificationVolume}
              onChange={(e) => handleSettingChange('notificationVolume', parseInt(e.target.value))}
            />
          </SettingGroup>

          <ToggleContainer>
            <ToggleLabel>Auto-play Audio</ToggleLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={settings.autoPlayAudio}
                onChange={(e) => handleSettingChange('autoPlayAudio', e.target.checked)}
              />
              <span></span>
            </Toggle>
          </ToggleContainer>
        </SettingsCard>

        {/* Relationship Settings */}
        <SettingsCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <CardHeader>
            <CardIcon>
              <FiHeart />
            </CardIcon>
            <CardTitle>Relationship Settings</CardTitle>
          </CardHeader>

          <SettingGroup>
            <SettingLabel>Relationship Depth: {settings.relationshipDepth}%</SettingLabel>
            <SettingDescription>How deep and meaningful conversations should be</SettingDescription>
            <Slider
              type="range"
              min="0"
              max="100"
              value={settings.relationshipDepth}
              onChange={(e) => handleSettingChange('relationshipDepth', parseInt(e.target.value))}
            />
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>Emotional Intensity: {settings.emotionalIntensity}%</SettingLabel>
            <SettingDescription>Level of emotional expression and vulnerability</SettingDescription>
            <Slider
              type="range"
              min="0"
              max="100"
              value={settings.emotionalIntensity}
              onChange={(e) => handleSettingChange('emotionalIntensity', parseInt(e.target.value))}
            />
          </SettingGroup>

          <ToggleContainer>
            <ToggleLabel>Romantic Mode</ToggleLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={settings.romanticMode}
                onChange={(e) => handleSettingChange('romanticMode', e.target.checked)}
              />
              <span></span>
            </Toggle>
          </ToggleContainer>

          <ToggleContainer>
            <ToggleLabel>Private Mode</ToggleLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={settings.privateMode}
                onChange={(e) => handleSettingChange('privateMode', e.target.checked)}
              />
              <span></span>
            </Toggle>
          </ToggleContainer>
        </SettingsCard>

        {/* System Settings */}
        <SettingsCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <CardHeader>
            <CardIcon>
              <FiSettings />
            </CardIcon>
            <CardTitle>System Settings</CardTitle>
          </CardHeader>

          <SettingGroup>
            <SettingLabel>Theme</SettingLabel>
            <SettingDescription>Choose your preferred visual theme</SettingDescription>
            <Select
              value={settings.theme}
              onChange={(e) => handleSettingChange('theme', e.target.value)}
            >
              <option value="romantic">Romantic</option>
              <option value="elegant">Elegant</option>
              <option value="minimal">Minimal</option>
              <option value="dark">Dark</option>
            </Select>
          </SettingGroup>

          <SettingGroup>
            <SettingLabel>Language</SettingLabel>
            <SettingDescription>Interface language</SettingDescription>
            <Select
              value={settings.language}
              onChange={(e) => handleSettingChange('language', e.target.value)}
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </Select>
          </SettingGroup>

          <ToggleContainer>
            <ToggleLabel>Auto-save</ToggleLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={settings.autoSave}
                onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
              />
              <span></span>
            </Toggle>
          </ToggleContainer>

          <ToggleContainer>
            <ToggleLabel>Data Collection</ToggleLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={settings.dataCollection}
                onChange={(e) => handleSettingChange('dataCollection', e.target.checked)}
              />
              <span></span>
            </Toggle>
          </ToggleContainer>
        </SettingsCard>

        {/* Advanced Settings */}
        <SettingsCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <CardHeader>
            <CardIcon>
              <FiMonitor />
            </CardIcon>
            <CardTitle>Advanced Features</CardTitle>
          </CardHeader>

          <ToggleContainer>
            <ToggleLabel>Haptic Feedback</ToggleLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={settings.hapticFeedback}
                onChange={(e) => handleSettingChange('hapticFeedback', e.target.checked)}
              />
              <span></span>
            </Toggle>
          </ToggleContainer>

          <ToggleContainer>
            <ToggleLabel>Biometric Monitoring</ToggleLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={settings.biometricMonitoring}
                onChange={(e) => handleSettingChange('biometricMonitoring', e.target.checked)}
              />
              <span></span>
            </Toggle>
          </ToggleContainer>

          <ToggleContainer>
            <ToggleLabel>VR Mode</ToggleLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={settings.vrMode}
                onChange={(e) => handleSettingChange('vrMode', e.target.checked)}
              />
              <span></span>
            </Toggle>
          </ToggleContainer>

          <ToggleContainer>
            <ToggleLabel>AI Learning</ToggleLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={settings.aiLearning}
                onChange={(e) => handleSettingChange('aiLearning', e.target.checked)}
              />
              <span></span>
            </Toggle>
          </ToggleContainer>
        </SettingsCard>
      </SettingsGrid>

      <ButtonGroup>
        <Button
          onClick={handleSave}
          disabled={saveSettingsMutation.isLoading}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <FiSave />
          {saveSettingsMutation.isLoading ? 'Saving...' : 'Save Settings'}
        </Button>
        
        <Button
          onClick={handleReset}
          disabled={resetSettingsMutation.isLoading}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          style={{ background: 'linear-gradient(135deg, #8b5a8b, #a8a8a8)' }}
        >
          <FiRefreshCw />
          {resetSettingsMutation.isLoading ? 'Resetting...' : 'Reset to Defaults'}
        </Button>
      </ButtonGroup>
    </SettingsContainer>
  );
};

export default Settings; 