import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';
import { 
  FiUser, 
  FiHeart, 
  FiEdit3, 
  FiSave, 
  FiCamera, 
  FiCalendar,
  FiMapPin,
  FiMail,
  FiPhone,
  FiStar,
  FiAward,
  FiTrendingUp,
  FiActivity,
  FiSettings,
  FiLock,
  FiEye,
  FiEyeOff
} from 'react-icons/fi';
import { api } from '../services/api';

const ProfileContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const ProfileHeader = styled.div`
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

const ProfileGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ProfileCard = styled(motion.div)`
  background: linear-gradient(135deg, #fff5f7 0%, #ffeef2 100%);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(255, 107, 157, 0.1);
  border: 1px solid rgba(255, 107, 157, 0.1);
`;

const AvatarSection = styled.div`
  text-align: center;
  margin-bottom: 2rem;
`;

const Avatar = styled.div`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b9d, #ff8fab);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3rem;
  font-weight: 600;
  margin: 0 auto 1rem;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 25px rgba(255, 107, 157, 0.3);
  }
`;

const AvatarOverlay = styled.div`
  position: absolute;
  bottom: 0;
  right: 0;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ff6b9d;
  font-size: 1rem;
  border: 2px solid #ff6b9d;
`;

const AvatarButton = styled.button`
  background: none;
  border: none;
  color: #8b5a8b;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  border: 2px solid rgba(255, 107, 157, 0.2);
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 107, 157, 0.1);
    border-color: #ff6b9d;
    color: #ff6b9d;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: white;
  border-radius: 15px;
  padding: 1rem;
  text-align: center;
  border: 1px solid rgba(255, 107, 157, 0.1);
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: #ff6b9d;
  margin-bottom: 0.25rem;
`;

const StatLabel = styled.div`
  font-size: 0.8rem;
  color: #8b5a8b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const SectionTitle = styled.h3`
  font-size: 1.3rem;
  color: #ff6b9d;
  margin-bottom: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  font-weight: 600;
  color: #8b5a8b;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
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
  
  &:disabled {
    background: rgba(255, 107, 157, 0.05);
    color: #8b5a8b;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(255, 107, 157, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  resize: vertical;
  min-height: 100px;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #ff6b9d;
    box-shadow: 0 0 0 3px rgba(255, 107, 157, 0.1);
  }
  
  &:disabled {
    background: rgba(255, 107, 157, 0.05);
    color: #8b5a8b;
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
  
  &:disabled {
    background: rgba(255, 107, 157, 0.05);
    color: #8b5a8b;
  }
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
  
  &.secondary {
    background: linear-gradient(135deg, #8b5a8b, #a8a8a8);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
`;

const RelationshipSection = styled.div`
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 107, 157, 0.1);
`;

const RelationshipHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
`;

const RelationshipTitle = styled.h4`
  font-size: 1.1rem;
  color: #ff6b9d;
  margin: 0;
  font-weight: 600;
`;

const RelationshipStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #8b5a8b;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #4CAF50;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 107, 157, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(135deg, #ff6b9d, #ff8fab);
  border-radius: 4px;
  transition: width 0.3s ease;
  width: ${props => props.value}%;
`;

const ProgressLabel = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #8b5a8b;
`;

const PrivacyToggle = styled.label`
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

const Profile = () => {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const [profile, setProfile] = useState({
    // Personal Info
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    location: '',
    bio: '',
    
    // Relationship Preferences
    relationshipStatus: 'single',
    lookingFor: 'romance',
    privacyLevel: 'public',
    
    // Account Settings
    username: '',
    password: '',
    emailNotifications: true,
    pushNotifications: true,
    profileVisibility: true
  });

  // Fetch profile data
  const { data: profileData, isLoading } = useQuery(
    'profile',
    () => api.getProfile(),
    {
      onSuccess: (data) => {
        setProfile(prev => ({ ...prev, ...data }));
      },
      onError: () => {
        toast.error('Failed to load profile');
      }
    }
  );

  // Fetch relationship data
  const { data: relationshipData } = useQuery(
    'relationship',
    () => api.getRelationshipData(),
    {
      onError: () => {
        toast.error('Failed to load relationship data');
      }
    }
  );

  // Update profile mutation
  const updateProfileMutation = useMutation(
    (profileData) => api.updateProfile(profileData),
    {
      onSuccess: () => {
        toast.success('Profile updated successfully');
        setIsEditing(false);
        queryClient.invalidateQueries('profile');
      },
      onError: () => {
        toast.error('Failed to update profile');
      }
    }
  );

  // Upload avatar mutation
  const uploadAvatarMutation = useMutation(
    (file) => api.uploadAvatar(file),
    {
      onSuccess: () => {
        toast.success('Avatar updated successfully');
        queryClient.invalidateQueries('profile');
      },
      onError: () => {
        toast.error('Failed to upload avatar');
      }
    }
  );

  const handleProfileChange = (key, value) => {
    setProfile(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    updateProfileMutation.mutate(profile);
  };

  const handleAvatarUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      uploadAvatarMutation.mutate(file);
    }
  };

  const handleCancel = () => {
    setProfile(prev => ({ ...prev, ...profileData }));
    setIsEditing(false);
  };

  if (isLoading) {
    return (
      <ProfileContainer>
        <div style={{ textAlign: 'center', padding: '4rem' }}>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <FiUser size={40} color="#ff6b9d" />
          </motion.div>
          <p style={{ marginTop: '1rem', color: '#8b5a8b' }}>Loading profile...</p>
        </div>
      </ProfileContainer>
    );
  }

  return (
    <ProfileContainer>
      <ProfileHeader>
        <Title>Profile</Title>
        <Subtitle>Manage your personal information and relationship preferences</Subtitle>
      </ProfileHeader>

      <ProfileGrid>
        {/* Left Column - Avatar & Stats */}
        <div>
          <ProfileCard
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <AvatarSection>
              <Avatar>
                {profile.firstName ? profile.firstName[0].toUpperCase() : 'U'}
                <AvatarOverlay>
                  <FiCamera />
                </AvatarOverlay>
              </Avatar>
              <input
                type="file"
                id="avatar-upload"
                accept="image/*"
                onChange={handleAvatarUpload}
                style={{ display: 'none' }}
              />
              <label htmlFor="avatar-upload">
                <AvatarButton as="span">
                  Change Photo
                </AvatarButton>
              </label>
            </AvatarSection>

            <StatsGrid>
              <StatCard>
                <StatValue>{relationshipData?.totalMemories || 0}</StatValue>
                <StatLabel>Memories</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{relationshipData?.relationshipLevel || 0}</StatValue>
                <StatLabel>Level</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{relationshipData?.daysTogether || 0}</StatValue>
                <StatLabel>Days</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{relationshipData?.conversations || 0}</StatValue>
                <StatLabel>Chats</StatLabel>
              </StatCard>
            </StatsGrid>

            <RelationshipSection>
              <RelationshipHeader>
                <RelationshipTitle>Relationship Status</RelationshipTitle>
                <RelationshipStatus>
                  <StatusDot />
                  Active
                </RelationshipStatus>
              </RelationshipHeader>
              
              <div style={{ marginBottom: '1rem' }}>
                <ProgressLabel>
                  <span>Trust Level</span>
                  <span>{relationshipData?.trustLevel || 0}%</span>
                </ProgressLabel>
                <ProgressBar>
                  <ProgressFill value={relationshipData?.trustLevel || 0} />
                </ProgressBar>
              </div>
              
              <div style={{ marginBottom: '1rem' }}>
                <ProgressLabel>
                  <span>Intimacy</span>
                  <span>{relationshipData?.intimacyLevel || 0}%</span>
                </ProgressLabel>
                <ProgressBar>
                  <ProgressFill value={relationshipData?.intimacyLevel || 0} />
                </ProgressBar>
              </div>
              
              <div>
                <ProgressLabel>
                  <span>Romance</span>
                  <span>{relationshipData?.romanceLevel || 0}%</span>
                </ProgressLabel>
                <ProgressBar>
                  <ProgressFill value={relationshipData?.romanceLevel || 0} />
                </ProgressBar>
              </div>
            </RelationshipSection>
          </ProfileCard>
        </div>

        {/* Right Column - Profile Form */}
        <ProfileCard
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <SectionTitle>
              <FiUser />
              Personal Information
            </SectionTitle>
            <Button
              onClick={() => setIsEditing(!isEditing)}
              className={isEditing ? 'secondary' : ''}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isEditing ? <FiSave /> : <FiEdit3 />}
              {isEditing ? 'Save' : 'Edit'}
            </Button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
            <FormGroup>
              <Label>First Name</Label>
              <Input
                type="text"
                value={profile.firstName}
                onChange={(e) => handleProfileChange('firstName', e.target.value)}
                disabled={!isEditing}
                placeholder="Enter first name"
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Last Name</Label>
              <Input
                type="text"
                value={profile.lastName}
                onChange={(e) => handleProfileChange('lastName', e.target.value)}
                disabled={!isEditing}
                placeholder="Enter last name"
              />
            </FormGroup>
          </div>

          <FormGroup>
            <Label>Email</Label>
            <Input
              type="email"
              value={profile.email}
              onChange={(e) => handleProfileChange('email', e.target.value)}
              disabled={!isEditing}
              placeholder="Enter email address"
            />
          </FormGroup>

          <FormGroup>
            <Label>Phone</Label>
            <Input
              type="tel"
              value={profile.phone}
              onChange={(e) => handleProfileChange('phone', e.target.value)}
              disabled={!isEditing}
              placeholder="Enter phone number"
            />
          </FormGroup>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
            <FormGroup>
              <Label>Date of Birth</Label>
              <Input
                type="date"
                value={profile.dateOfBirth}
                onChange={(e) => handleProfileChange('dateOfBirth', e.target.value)}
                disabled={!isEditing}
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Location</Label>
              <Input
                type="text"
                value={profile.location}
                onChange={(e) => handleProfileChange('location', e.target.value)}
                disabled={!isEditing}
                placeholder="Enter location"
              />
            </FormGroup>
          </div>

          <FormGroup>
            <Label>Bio</Label>
            <TextArea
              value={profile.bio}
              onChange={(e) => handleProfileChange('bio', e.target.value)}
              disabled={!isEditing}
              placeholder="Tell us about yourself..."
            />
          </FormGroup>

          <SectionTitle style={{ marginTop: '2rem' }}>
            <FiHeart />
            Relationship Preferences
          </SectionTitle>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
            <FormGroup>
              <Label>Relationship Status</Label>
              <Select
                value={profile.relationshipStatus}
                onChange={(e) => handleProfileChange('relationshipStatus', e.target.value)}
                disabled={!isEditing}
              >
                <option value="single">Single</option>
                <option value="dating">Dating</option>
                <option value="committed">Committed</option>
                <option value="married">Married</option>
              </Select>
            </FormGroup>
            
            <FormGroup>
              <Label>Looking For</Label>
              <Select
                value={profile.lookingFor}
                onChange={(e) => handleProfileChange('lookingFor', e.target.value)}
                disabled={!isEditing}
              >
                <option value="romance">Romance</option>
                <option value="friendship">Friendship</option>
                <option value="companionship">Companionship</option>
                <option value="casual">Casual</option>
              </Select>
            </FormGroup>
          </div>

          <SectionTitle style={{ marginTop: '2rem' }}>
            <FiSettings />
            Account Settings
          </SectionTitle>

          <FormGroup>
            <Label>Username</Label>
            <Input
              type="text"
              value={profile.username}
              onChange={(e) => handleProfileChange('username', e.target.value)}
              disabled={!isEditing}
              placeholder="Choose a username"
            />
          </FormGroup>

          <FormGroup>
            <Label>Password</Label>
            <div style={{ position: 'relative' }}>
              <Input
                type={showPassword ? 'text' : 'password'}
                value={profile.password}
                onChange={(e) => handleProfileChange('password', e.target.value)}
                disabled={!isEditing}
                placeholder="Enter new password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#8b5a8b',
                  cursor: 'pointer'
                }}
              >
                {showPassword ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
          </FormGroup>

          <ToggleContainer>
            <ToggleLabel>Email Notifications</ToggleLabel>
            <PrivacyToggle>
              <input
                type="checkbox"
                checked={profile.emailNotifications}
                onChange={(e) => handleProfileChange('emailNotifications', e.target.checked)}
                disabled={!isEditing}
              />
              <span></span>
            </PrivacyToggle>
          </ToggleContainer>

          <ToggleContainer>
            <ToggleLabel>Push Notifications</ToggleLabel>
            <PrivacyToggle>
              <input
                type="checkbox"
                checked={profile.pushNotifications}
                onChange={(e) => handleProfileChange('pushNotifications', e.target.checked)}
                disabled={!isEditing}
              />
              <span></span>
            </PrivacyToggle>
          </ToggleContainer>

          <ToggleContainer>
            <ToggleLabel>Profile Visibility</ToggleLabel>
            <PrivacyToggle>
              <input
                type="checkbox"
                checked={profile.profileVisibility}
                onChange={(e) => handleProfileChange('profileVisibility', e.target.checked)}
                disabled={!isEditing}
              />
              <span></span>
            </PrivacyToggle>
          </ToggleContainer>

          {isEditing && (
            <ButtonGroup>
              <Button
                onClick={handleSave}
                disabled={updateProfileMutation.isLoading}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <FiSave />
                {updateProfileMutation.isLoading ? 'Saving...' : 'Save Changes'}
              </Button>
              
              <Button
                onClick={handleCancel}
                className="secondary"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Cancel
              </Button>
            </ButtonGroup>
          )}
        </ProfileCard>
      </ProfileGrid>
    </ProfileContainer>
  );
};

export default Profile; 