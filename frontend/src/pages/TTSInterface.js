import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import { 
  FaMicrophone, 
  FaPlay, 
  FaPause, 
  FaVolumeUp, 
  FaVolumeMute,
  FaHeart,
  FaSmile,
  FaSadTear,
  FaAngry,
  FaSurprise,
  FaMeh,
  FaMagic,
  FaDownload,
  FaHistory,
  FaCog
} from 'react-icons/fa';

import apiService from '../services/api';

// Styled Components
const TTSContainer = styled.div`
  max-width: 1200px;
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
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
  }
`;

const InputSection = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
`;

const OutputSection = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
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

const PersonaSelector = styled.div`
  margin-bottom: 2rem;
  
  .persona-options {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    
    @media (max-width: ${props => props.theme.breakpoints.tablet}) {
      flex-direction: column;
    }
  }
`;

const PersonaButton = styled.button`
  flex: 1;
  padding: 1rem;
  border: 2px solid ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.textSecondary};
  border-radius: ${props => props.theme.borderRadius.medium};
  background: ${props => props.isActive ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.isActive ? 'white' : props.theme.colors.text};
  font-weight: 600;
  cursor: pointer;
  transition: ${props => props.theme.transitions.medium};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  
  &:hover {
    border-color: ${props => props.theme.colors.primary};
    background: ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.primary}10;
  }
  
  .persona-icon {
    font-size: 1.2rem;
  }
`;

const TextInput = styled.div`
  margin-bottom: 2rem;
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: ${props => props.theme.colors.text};
  }
  
  textarea {
    width: 100%;
    min-height: 120px;
    padding: 1rem;
    border: 2px solid ${props => props.theme.colors.textSecondary};
    border-radius: ${props => props.theme.borderRadius.medium};
    font-family: ${props => props.theme.fonts.primary};
    font-size: 1rem;
    resize: vertical;
    transition: ${props => props.theme.transitions.fast};
    
    &:focus {
      border-color: ${props => props.theme.colors.primary};
      outline: none;
      box-shadow: 0 0 0 3px rgba(233, 30, 99, 0.1);
    }
  }
`;

const EmotionSelector = styled.div`
  margin-bottom: 2rem;
  
  .emotion-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.75rem;
  }
`;

const EmotionButton = styled.button`
  padding: 1rem 0.75rem;
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
  
  .emotion-icon {
    font-size: 1.5rem;
  }
  
  .emotion-label {
    font-size: 0.8rem;
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

const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  
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

const AudioPlayer = styled.div`
  background: linear-gradient(135deg, ${props => props.theme.colors.background}, ${props => props.theme.colors.calm});
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: 2rem;
  text-align: center;
  margin-bottom: 2rem;
  
  .audio-controls {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .play-button {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: ${props => props.theme.colors.primary};
    color: white;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    transition: ${props => props.theme.transitions.fast};
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      transform: scale(1.1);
      box-shadow: ${props => props.theme.shadows.romantic};
    }
  }
  
  .audio-info {
    color: ${props => props.theme.colors.textSecondary};
    font-size: 0.9rem;
  }
`;

const HistorySection = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
`;

const HistoryItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border: 1px solid ${props => props.theme.colors.primary}20;
  border-radius: ${props => props.theme.borderRadius.small};
  margin-bottom: 1rem;
  transition: ${props => props.theme.transitions.fast};
  
  &:hover {
    border-color: ${props => props.theme.colors.primary}40;
    background: ${props => props.theme.colors.background};
  }
  
  .history-content {
    flex: 1;
    
    .history-text {
      font-weight: 500;
      margin-bottom: 0.25rem;
    }
    
    .history-meta {
      font-size: 0.8rem;
      color: ${props => props.theme.colors.textSecondary};
    }
  }
  
  .history-actions {
    display: flex;
    gap: 0.5rem;
  }
`;

const TTSInterface = () => {
  const [text, setText] = useState('');
  const [persona, setPersona] = useState('mia');
  const [emotion, setEmotion] = useState('neutral');
  const [intensity, setIntensity] = useState(0.5);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);

  const queryClient = useQueryClient();

  // Queries
  const { data: ttsStatus } = useQuery('ttsStatus', apiService.getTTSStatus);
  const { data: availableEmotions } = useQuery('availableEmotions', apiService.getAvailableEmotions);

  // Mutations
  const synthesizeMutation = useMutation(
    (params) => apiService.synthesizeSpeech(params.text, params.persona, params.emotion, params.intensity),
    {
      onSuccess: (data) => {
        if (data.audio_data) {
          setCurrentAudio(data.audio_data);
          toast.success('Speech synthesized successfully!');
        }
      },
      onError: (error) => {
        toast.error('Failed to synthesize speech');
      },
    }
  );

  const emotions = [
    { key: 'love', label: 'Love', icon: FaHeart },
    { key: 'joy', label: 'Joy', icon: FaSmile },
    { key: 'sadness', label: 'Sadness', icon: FaSadTear },
    { key: 'anger', label: 'Anger', icon: FaAngry },
    { key: 'surprise', label: 'Surprise', icon: FaSurprise },
    { key: 'neutral', label: 'Neutral', icon: FaMeh },
  ];

  const handleSynthesize = () => {
    if (!text.trim()) {
      toast.error('Please enter some text to synthesize');
      return;
    }

    synthesizeMutation.mutate({
      text: text.trim(),
      persona,
      emotion,
      intensity,
    });
  };

  const handlePlayAudio = () => {
    if (currentAudio) {
      setIsPlaying(true);
      apiService.playAudioFromBase64(currentAudio);
      
      // Reset playing state after a delay
      setTimeout(() => setIsPlaying(false), 3000);
    }
  };

  const handleDownload = () => {
    if (currentAudio) {
      try {
        const audioData = atob(currentAudio);
        const arrayBuffer = new ArrayBuffer(audioData.length);
        const view = new Uint8Array(arrayBuffer);
        for (let i = 0; i < audioData.length; i++) {
          view[i] = audioData.charCodeAt(i);
        }
        
        const blob = new Blob([arrayBuffer], { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `miasolene-${persona}-${emotion}.wav`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        toast.success('Audio downloaded successfully!');
      } catch (error) {
        toast.error('Failed to download audio');
      }
    }
  };

  return (
    <TTSContainer>
      <Header>
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Voice Synthesis
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Create emotional speech with Mia and Solene using advanced TTS technology
        </motion.p>
      </Header>

      <MainGrid>
        <InputSection
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <SectionTitle>
            <FaMicrophone className="icon" />
            Input Configuration
          </SectionTitle>

          <PersonaSelector>
            <label>Choose Persona</label>
            <div className="persona-options">
              <PersonaButton
                isActive={persona === 'mia'}
                onClick={() => setPersona('mia')}
              >
                <FaHeart className="persona-icon" />
                Mia
              </PersonaButton>
              <PersonaButton
                isActive={persona === 'solene'}
                onClick={() => setPersona('solene')}
              >
                <FaMagic className="persona-icon" />
                Solene
              </PersonaButton>
            </div>
          </PersonaSelector>

          <TextInput>
            <label>Text to Synthesize</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter the text you want to convert to speech..."
              maxLength={500}
            />
            <div style={{ textAlign: 'right', marginTop: '0.5rem', fontSize: '0.8rem', color: '#757575' }}>
              {text.length}/500 characters
            </div>
          </TextInput>

          <EmotionSelector>
            <label>Emotion</label>
            <div className="emotion-grid">
              {emotions.map((emotionOption) => {
                const Icon = emotionOption.icon;
                return (
                  <EmotionButton
                    key={emotionOption.key}
                    isActive={emotion === emotionOption.key}
                    onClick={() => setEmotion(emotionOption.key)}
                  >
                    <Icon className="emotion-icon" />
                    <span className="emotion-label">{emotionOption.label}</span>
                  </EmotionButton>
                );
              })}
            </div>
          </EmotionSelector>

          <IntensitySlider>
            <label>Emotion Intensity</label>
            <div className="slider-container">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={intensity}
                onChange={(e) => setIntensity(parseFloat(e.target.value))}
              />
              <span className="intensity-value">{Math.round(intensity * 100)}%</span>
            </div>
          </IntensitySlider>

          <ActionButtons>
            <Button
              className="primary"
              onClick={handleSynthesize}
              disabled={synthesizeMutation.isLoading || !text.trim()}
            >
              {synthesizeMutation.isLoading ? <FaPause /> : <FaPlay />}
              {synthesizeMutation.isLoading ? 'Synthesizing...' : 'Synthesize Speech'}
            </Button>
            <Button className="secondary">
              <FaCog />
              Advanced Settings
            </Button>
          </ActionButtons>
        </InputSection>

        <OutputSection
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <SectionTitle>
            <FaVolumeUp className="icon" />
            Audio Output
          </SectionTitle>

          <AudioPlayer>
            <div className="audio-controls">
              <button
                className="play-button"
                onClick={handlePlayAudio}
                disabled={!currentAudio || isPlaying}
              >
                {isPlaying ? <FaPause /> : <FaPlay />}
              </button>
            </div>
            <div className="audio-info">
              {currentAudio ? (
                <>
                  <div>Audio ready for playback</div>
                  <div>Persona: {persona} | Emotion: {emotion} | Intensity: {Math.round(intensity * 100)}%</div>
                </>
              ) : (
                <div>No audio generated yet</div>
              )}
            </div>
          </AudioPlayer>

          {currentAudio && (
            <ActionButtons>
              <Button className="primary" onClick={handlePlayAudio} disabled={isPlaying}>
                <FaPlay />
                Play Again
              </Button>
              <Button className="secondary" onClick={handleDownload}>
                <FaDownload />
                Download
              </Button>
            </ActionButtons>
          )}

          <div style={{ marginTop: '2rem' }}>
            <h4 style={{ marginBottom: '1rem', color: '#757575' }}>System Status</h4>
            <div style={{ 
              padding: '1rem', 
              background: ttsStatus?.status === 'ready' ? '#4CAF50' : '#F44336',
              color: 'white',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              TTS System: {ttsStatus?.status === 'ready' ? 'Ready' : 'Initializing'}
            </div>
          </div>
        </OutputSection>
      </MainGrid>

      <HistorySection
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <SectionTitle>
          <FaHistory className="icon" />
          Recent Syntheses
        </SectionTitle>
        
        <div style={{ textAlign: 'center', color: '#757575', padding: '2rem' }}>
          <FaHistory style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.3 }} />
          <p>Recent synthesis history will appear here</p>
          <p style={{ fontSize: '0.9rem' }}>Your synthesized audio clips will be saved for easy access</p>
        </div>
      </HistorySection>
    </TTSContainer>
  );
};

export default TTSInterface; 