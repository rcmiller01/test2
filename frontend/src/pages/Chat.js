import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';
import { 
  FiSend, 
  FiMic, 
  FiMicOff, 
  FiHeart, 
  FiSmile, 
  FiImage,
  FiPaperclip,
  FiMoreVertical,
  FiUser,
  FiMessageCircle,
  FiClock,
  FiVolume2,
  FiVolumeX
} from 'react-icons/fi';
import { api } from '../services/api';

const ChatContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
`;

const ChatHeader = styled.div`
  background: linear-gradient(135deg, #fff5f7 0%, #ffeef2 100%);
  border-radius: 20px 20px 0 0;
  padding: 1.5rem;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const Avatar = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b9d, #ff8fab);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 2px;
    right: 2px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: ${props => props.status === 'online' ? '#4CAF50' : '#f44336'};
    border: 2px solid white;
  }
`;

const UserInfo = styled.div`
  h3 {
    margin: 0;
    color: #ff6b9d;
    font-size: 1.2rem;
    font-weight: 600;
  }
  
  p {
    margin: 0;
    color: #8b5a8b;
    font-size: 0.9rem;
  }
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const IconButton = styled(motion.button)`
  background: none;
  border: none;
  color: #8b5a8b;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 107, 157, 0.1);
    color: #ff6b9d;
  }
  
  &.active {
    color: #ff6b9d;
    background: rgba(255, 107, 157, 0.1);
  }
`;

const ChatMessages = styled.div`
  flex: 1;
  background: white;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 107, 157, 0.1);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 107, 157, 0.3);
    border-radius: 3px;
  }
`;

const Message = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  max-width: 80%;
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  flex-direction: ${props => props.isUser ? 'row-reverse' : 'row'};
`;

const MessageAvatar = styled.div`
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background: ${props => props.isUser 
    ? 'linear-gradient(135deg, #8b5a8b, #a8a8a8)' 
    : 'linear-gradient(135deg, #ff6b9d, #ff8fab)'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  flex-shrink: 0;
`;

const MessageContent = styled.div`
  background: ${props => props.isUser 
    ? 'linear-gradient(135deg, #ff6b9d, #ff8fab)' 
    : 'linear-gradient(135deg, #fff5f7, #ffeef2)'};
  color: ${props => props.isUser ? 'white' : '#8b5a8b'};
  padding: 0.75rem 1rem;
  border-radius: 18px;
  border: 1px solid ${props => props.isUser 
    ? 'rgba(255, 255, 255, 0.2)' 
    : 'rgba(255, 107, 157, 0.1)'};
  position: relative;
  word-wrap: break-word;
  
  ${props => props.isUser && `
    border-bottom-right-radius: 4px;
  `}
  
  ${!props.isUser && `
    border-bottom-left-radius: 4px;
  `}
`;

const MessageTime = styled.div`
  font-size: 0.75rem;
  color: ${props => props.isUser ? 'rgba(255, 255, 255, 0.7)' : '#a8a8a8'};
  margin-top: 0.25rem;
  text-align: ${props => props.isUser ? 'right' : 'left'};
`;

const TypingIndicator = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #fff5f7, #ffeef2);
  border-radius: 18px;
  border: 1px solid rgba(255, 107, 157, 0.1);
  border-bottom-left-radius: 4px;
  max-width: 80px;
  align-self: flex-start;
`;

const TypingDot = styled(motion.div)`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff6b9d;
`;

const ChatInput = styled.div`
  background: linear-gradient(135deg, #fff5f7 0%, #ffeef2 100%);
  border-radius: 0 0 20px 20px;
  padding: 1.5rem;
  border-top: 2px solid rgba(255, 107, 157, 0.1);
`;

const InputContainer = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  background: white;
  border-radius: 25px;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(255, 107, 157, 0.2);
  transition: all 0.3s ease;
  
  &:focus-within {
    border-color: #ff6b9d;
    box-shadow: 0 0 0 3px rgba(255, 107, 157, 0.1);
  }
`;

const TextArea = styled.textarea`
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 1rem;
  font-family: inherit;
  line-height: 1.4;
  max-height: 120px;
  min-height: 24px;
  
  &::placeholder {
    color: #a8a8a8;
  }
`;

const InputActions = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ActionButton = styled(motion.button)`
  background: none;
  border: none;
  color: #8b5a8b;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 107, 157, 0.1);
    color: #ff6b9d;
  }
  
  &.active {
    color: #ff6b9d;
    background: rgba(255, 107, 157, 0.1);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const SendButton = styled(motion.button)`
  background: linear-gradient(135deg, #ff6b9d, #ff8fab);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    transform: scale(1.1);
    box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const PersonaSelector = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
`;

const PersonaButton = styled(motion.button)`
  background: ${props => props.active 
    ? 'linear-gradient(135deg, #ff6b9d, #ff8fab)' 
    : 'rgba(255, 107, 157, 0.1)'};
  color: ${props => props.active ? 'white' : '#8b5a8b'};
  border: 2px solid ${props => props.active 
    ? 'rgba(255, 255, 255, 0.2)' 
    : 'rgba(255, 107, 157, 0.2)'};
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: ${props => props.active 
      ? 'linear-gradient(135deg, #ff6b9d, #ff8fab)' 
      : 'rgba(255, 107, 157, 0.2)'};
  }
`;

const Chat = () => {
  const queryClient = useQueryClient();
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  
  const [message, setMessage] = useState('');
  const [selectedPersona, setSelectedPersona] = useState('both');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  // Fetch chat history
  const { data: messages = [], isLoading } = useQuery(
    ['chat', selectedPersona],
    () => api.getChatHistory(selectedPersona),
    {
      refetchInterval: 3000, // Poll every 3 seconds for new messages
      onError: () => {
        toast.error('Failed to load chat history');
      }
    }
  );

  // Send message mutation
  const sendMessageMutation = useMutation(
    (messageData) => api.sendMessage(messageData),
    {
      onSuccess: () => {
        setMessage('');
        queryClient.invalidateQueries(['chat', selectedPersona]);
        scrollToBottom();
      },
      onError: () => {
        toast.error('Failed to send message');
      }
    }
  );

  // Start voice recording mutation
  const startRecordingMutation = useMutation(
    () => api.startVoiceRecording(),
    {
      onSuccess: () => {
        setIsRecording(true);
        toast.success('Voice recording started');
      },
      onError: () => {
        toast.error('Failed to start voice recording');
      }
    }
  );

  // Stop voice recording mutation
  const stopRecordingMutation = useMutation(
    () => api.stopVoiceRecording(),
    {
      onSuccess: () => {
        setIsRecording(false);
        toast.success('Voice recording stopped');
        queryClient.invalidateQueries(['chat', selectedPersona]);
      },
      onError: () => {
        toast.error('Failed to stop voice recording');
      }
    }
  );

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = () => {
    if (!message.trim()) return;
    
    const messageData = {
      content: message.trim(),
      persona: selectedPersona,
      timestamp: new Date().toISOString()
    };
    
    sendMessageMutation.mutate(messageData);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleVoiceToggle = () => {
    if (isRecording) {
      stopRecordingMutation.mutate();
    } else {
      startRecordingMutation.mutate();
    }
  };

  const handleMuteToggle = () => {
    setIsMuted(!isMuted);
    toast.success(isMuted ? 'Audio unmuted' : 'Audio muted');
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [message]);

  if (isLoading) {
    return (
      <ChatContainer>
        <div style={{ textAlign: 'center', padding: '4rem' }}>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <FiMessageCircle size={40} color="#ff6b9d" />
          </motion.div>
          <p style={{ marginTop: '1rem', color: '#8b5a8b' }}>Loading chat...</p>
        </div>
      </ChatContainer>
    );
  }

  return (
    <ChatContainer>
      <PersonaSelector>
        <PersonaButton
          active={selectedPersona === 'both'}
          onClick={() => setSelectedPersona('both')}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Both Mia & Solene
        </PersonaButton>
        <PersonaButton
          active={selectedPersona === 'mia'}
          onClick={() => setSelectedPersona('mia')}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Mia
        </PersonaButton>
        <PersonaButton
          active={selectedPersona === 'solene'}
          onClick={() => setSelectedPersona('solene')}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Solene
        </PersonaButton>
      </PersonaSelector>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', borderRadius: '20px', overflow: 'hidden', boxShadow: '0 8px 32px rgba(255, 107, 157, 0.1)' }}>
        <ChatHeader>
          <HeaderLeft>
            <Avatar status="online">
              {selectedPersona === 'both' ? 'M&S' : selectedPersona === 'mia' ? 'M' : 'S'}
            </Avatar>
            <UserInfo>
              <h3>
                {selectedPersona === 'both' ? 'Mia & Solene' : 
                 selectedPersona === 'mia' ? 'Mia' : 'Solene'}
              </h3>
              <p>Online • Ready to chat</p>
            </UserInfo>
          </HeaderLeft>
          <HeaderRight>
            <IconButton
              onClick={handleMuteToggle}
              className={isMuted ? 'active' : ''}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              {isMuted ? <FiVolumeX /> : <FiVolume2 />}
            </IconButton>
            <IconButton
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <FiMoreVertical />
            </IconButton>
          </HeaderRight>
        </ChatHeader>

        <ChatMessages>
          <AnimatePresence>
            {messages.map((msg, index) => (
              <Message
                key={msg.id || index}
                isUser={msg.sender === 'user'}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <MessageAvatar isUser={msg.sender === 'user'}>
                  {msg.sender === 'user' ? <FiUser /> : 
                   msg.persona === 'mia' ? 'M' : 'S'}
                </MessageAvatar>
                <div>
                  <MessageContent isUser={msg.sender === 'user'}>
                    {msg.content}
                  </MessageContent>
                  <MessageTime isUser={msg.sender === 'user'}>
                    {formatTime(msg.timestamp)}
                  </MessageTime>
                </div>
              </Message>
            ))}
            
            {isTyping && (
              <TypingIndicator
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <TypingDot
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity }}
                />
                <TypingDot
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                />
                <TypingDot
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                />
              </TypingIndicator>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </ChatMessages>

        <ChatInput>
          <InputContainer>
            <TextArea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Message ${selectedPersona === 'both' ? 'Mia & Solene' : selectedPersona === 'mia' ? 'Mia' : 'Solene'}...`}
              rows={1}
            />
            <InputActions>
              <ActionButton
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <FiSmile />
              </ActionButton>
              <ActionButton
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <FiImage />
              </ActionButton>
              <ActionButton
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <FiPaperclip />
              </ActionButton>
              <ActionButton
                onClick={handleVoiceToggle}
                className={isRecording ? 'active' : ''}
                disabled={sendMessageMutation.isLoading}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                {isRecording ? <FiMicOff /> : <FiMic />}
              </ActionButton>
              <SendButton
                onClick={handleSendMessage}
                disabled={!message.trim() || sendMessageMutation.isLoading}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <FiSend />
              </SendButton>
            </InputActions>
          </InputContainer>
        </ChatInput>
      </div>
    </ChatContainer>
  );
};

export default Chat; 