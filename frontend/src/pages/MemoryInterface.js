import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import { 
  FaHeart, 
  FaSearch, 
  FaPlus, 
  FaEdit, 
  FaTrash, 
  FaCalendar,
  FaClock,
  FaTag,
  FaFilter,
  FaSort,
  FaDownload,
  FaShare,
  FaBookmark,
  FaStar,
  FaChartLine,
  FaLightbulb,
  FaMagic
} from 'react-icons/fa';

import apiService from '../services/api';

// Styled Components
const MemoryContainer = styled.div`
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

const SearchAndFilters = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
  margin-bottom: 2rem;
`;

const SearchBar = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex-direction: column;
  }
  
  input {
    flex: 1;
    padding: 1rem;
    border: 2px solid ${props => props.theme.colors.textSecondary};
    border-radius: ${props => props.theme.borderRadius.medium};
    font-size: 1rem;
    
    &:focus {
      border-color: ${props => props.theme.colors.primary};
      outline: none;
      box-shadow: 0 0 0 3px rgba(233, 30, 99, 0.1);
    }
  }
  
  button {
    padding: 1rem 2rem;
    background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.accent});
    color: white;
    border: none;
    border-radius: ${props => props.theme.borderRadius.medium};
    font-weight: 600;
    cursor: pointer;
    transition: ${props => props.theme.transitions.fast};
    display: flex;
    align-items: center;
    gap: 0.5rem;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: ${props => props.theme.shadows.romantic};
    }
  }
`;

const FilterGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
`;

const FilterSelect = styled.select`
  padding: 0.75rem;
  border: 2px solid ${props => props.theme.colors.textSecondary};
  border-radius: ${props => props.theme.borderRadius.small};
  background: white;
  font-size: 0.9rem;
  
  &:focus {
    border-color: ${props => props.theme.colors.primary};
    outline: none;
    box-shadow: 0 0 0 3px rgba(233, 30, 99, 0.1);
  }
`;

const MemoryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
`;

const MemoryCard = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 1.5rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
  transition: ${props => props.theme.transitions.medium};
  cursor: pointer;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: ${props => props.theme.shadows.large};
    border-color: ${props => props.theme.colors.primary}40;
  }
  
  .memory-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
    
    .memory-title {
      font-size: 1.2rem;
      font-weight: 600;
      color: ${props => props.theme.colors.primary};
      margin-bottom: 0.5rem;
    }
    
    .memory-date {
      font-size: 0.8rem;
      color: ${props => props.theme.colors.textSecondary};
      display: flex;
      align-items: center;
      gap: 0.25rem;
    }
  }
  
  .memory-content {
    color: ${props => props.theme.colors.text};
    line-height: 1.6;
    margin-bottom: 1rem;
  }
  
  .memory-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
    
    .tag {
      background: ${props => props.theme.colors.background};
      color: ${props => props.theme.colors.primary};
      padding: 0.25rem 0.75rem;
      border-radius: ${props => props.theme.borderRadius.small};
      font-size: 0.8rem;
      font-weight: 500;
    }
  }
  
  .memory-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
    
    button {
      padding: 0.5rem;
      border: none;
      border-radius: ${props => props.theme.borderRadius.small};
      background: ${props => props.theme.colors.background};
      color: ${props => props.theme.colors.primary};
      cursor: pointer;
      transition: ${props => props.theme.transitions.fast};
      
      &:hover {
        background: ${props => props.theme.colors.primary};
        color: white;
      }
    }
  }
`;

const StatsSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
  margin-bottom: 2rem;
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
    font-size: 2rem;
    font-weight: 700;
    color: ${props => props.theme.colors.primary};
    margin-bottom: 0.5rem;
  }
  
  .stat-label {
    color: ${props => props.theme.colors.textSecondary};
    font-weight: 500;
  }
`;

const InsightsSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: 2rem;
  box-shadow: ${props => props.theme.shadows.medium};
  border: 2px solid ${props => props.theme.colors.primary}20;
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

const MemoryInterface = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEmotion, setSelectedEmotion] = useState('all');
  const [selectedDateRange, setSelectedDateRange] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  const queryClient = useQueryClient();

  // Queries
  const { data: memories } = useQuery('memories', () => 
    apiService.recallMemories({
      emotion: selectedEmotion !== 'all' ? selectedEmotion : undefined,
      date_range: selectedDateRange !== 'all' ? selectedDateRange : undefined,
      search: searchTerm || undefined,
      sort_by: sortBy,
    })
  );

  const { data: memorySummary } = useQuery('memorySummary', apiService.getMemorySummary);
  const { data: relationshipInsights } = useQuery('relationshipInsights', apiService.getRelationshipInsights);

  // Mutations
  const deleteMemoryMutation = useMutation(
    (memoryId) => apiService.deleteMemory(memoryId),
    {
      onSuccess: () => {
        toast.success('Memory deleted successfully');
        queryClient.invalidateQueries('memories');
        queryClient.invalidateQueries('memorySummary');
      },
      onError: () => {
        toast.error('Failed to delete memory');
      },
    }
  );

  const emotions = [
    { value: 'all', label: 'All Emotions' },
    { value: 'love', label: 'Love' },
    { value: 'joy', label: 'Joy' },
    { value: 'sadness', label: 'Sadness' },
    { value: 'anger', label: 'Anger' },
    { value: 'surprise', label: 'Surprise' },
  ];

  const dateRanges = [
    { value: 'all', label: 'All Time' },
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'year', label: 'This Year' },
  ];

  const sortOptions = [
    { value: 'date', label: 'Date' },
    { value: 'emotion', label: 'Emotion' },
    { value: 'relevance', label: 'Relevance' },
  ];

  const handleSearch = () => {
    queryClient.invalidateQueries('memories');
  };

  const handleDeleteMemory = (memoryId) => {
    if (window.confirm('Are you sure you want to delete this memory?')) {
      deleteMemoryMutation.mutate(memoryId);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <MemoryContainer>
      <Header>
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Memory Browser
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Browse and manage your romantic memories with Mia and Solene
        </motion.p>
      </Header>

      <SearchAndFilters
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <SearchBar>
          <input
            type="text"
            placeholder="Search memories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>
            <FaSearch />
            Search
          </button>
        </SearchBar>

        <FilterGrid>
          <FilterSelect
            value={selectedEmotion}
            onChange={(e) => setSelectedEmotion(e.target.value)}
          >
            {emotions.map(emotion => (
              <option key={emotion.value} value={emotion.value}>
                {emotion.label}
              </option>
            ))}
          </FilterSelect>

          <FilterSelect
            value={selectedDateRange}
            onChange={(e) => setSelectedDateRange(e.target.value)}
          >
            {dateRanges.map(range => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </FilterSelect>

          <FilterSelect
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            {sortOptions.map(option => (
              <option key={option.value} value={option.value}>
                Sort by: {option.label}
              </option>
            ))}
          </FilterSelect>
        </FilterGrid>
      </SearchAndFilters>

      <StatsSection
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <h3 style={{ marginBottom: '1.5rem', color: '#E91E63' }}>Memory Statistics</h3>
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
            <div className="stat-value">{memorySummary?.love_memories || 0}</div>
            <div className="stat-label">Love Memories</div>
          </StatCard>
          <StatCard>
            <div className="stat-value">{memorySummary?.recent_memories || 0}</div>
            <div className="stat-label">Recent Memories</div>
          </StatCard>
        </StatsGrid>
      </StatsSection>

      <MemoryGrid>
        {memories?.memories?.map((memory, index) => (
          <MemoryCard
            key={memory.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
          >
            <div className="memory-header">
              <div>
                <div className="memory-title">{memory.title || 'Untitled Memory'}</div>
                <div className="memory-date">
                  <FaCalendar />
                  {formatDate(memory.timestamp)}
                </div>
              </div>
            </div>
            
            <div className="memory-content">
              {memory.content || 'No content available'}
            </div>
            
            {memory.emotion && (
              <div className="memory-tags">
                <span className="tag">{memory.emotion}</span>
                {memory.intensity && (
                  <span className="tag">Intensity: {Math.round(memory.intensity * 100)}%</span>
                )}
              </div>
            )}
            
            <div className="memory-actions">
              <button title="Edit">
                <FaEdit />
              </button>
              <button title="Share">
                <FaShare />
              </button>
              <button title="Bookmark">
                <FaBookmark />
              </button>
              <button 
                title="Delete"
                onClick={() => handleDeleteMemory(memory.id)}
              >
                <FaTrash />
              </button>
            </div>
          </MemoryCard>
        ))}
      </MemoryGrid>

      {(!memories?.memories || memories.memories.length === 0) && (
        <div style={{ textAlign: 'center', padding: '4rem', color: '#757575' }}>
          <FaHeart style={{ fontSize: '4rem', marginBottom: '1rem', opacity: 0.3 }} />
          <h3>No memories found</h3>
          <p>Start creating romantic memories with Mia and Solene!</p>
        </div>
      )}

      <InsightsSection
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        <h3 style={{ marginBottom: '1.5rem', color: '#E91E63' }}>
          <FaLightbulb style={{ marginRight: '0.5rem' }} />
          Relationship Insights
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
            <FaChartLine style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.3 }} />
            <p>Relationship insights will appear here as you create more memories</p>
          </div>
        )}
      </InsightsSection>
    </MemoryContainer>
  );
};

export default MemoryInterface; 