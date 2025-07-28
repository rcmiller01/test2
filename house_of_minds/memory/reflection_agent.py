"""
True Recall - Reflection Agent

Automated reflection and synthesis system for generating daily summaries,
identifying patterns, and creating meaningful insights from memory events.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import json
import re

logger = logging.getLogger(__name__)

class ReflectionAgent:
    """
    Intelligent reflection system for True Recall memory analysis.
    
    Generates daily reflections, identifies patterns, creates insights,
    and synthesizes meaningful summaries from memory events.
    """
    
    def __init__(self):
        """Initialize the reflection agent."""
        
        # Reflection templates
        self.reflection_templates = {
            'daily': {
                'sections': [
                    'emotional_tone',
                    'key_events',
                    'interaction_patterns',
                    'learning_moments',
                    'memorable_quotes',
                    'reflection_summary'
                ]
            },
            'weekly': {
                'sections': [
                    'week_overview',
                    'emotional_journey',
                    'recurring_themes',
                    'relationship_dynamics',
                    'growth_insights',
                    'future_considerations'
                ]
            }
        }
        
        # Pattern detection keywords
        self.pattern_keywords = {
            'learning': ['learn', 'understand', 'realize', 'discover', 'insight', 'knowledge'],
            'emotional': ['feel', 'emotion', 'mood', 'happy', 'sad', 'angry', 'excited'],
            'social': ['friend', 'family', 'relationship', 'conversation', 'people'],
            'work': ['work', 'job', 'project', 'meeting', 'task', 'career'],
            'health': ['health', 'exercise', 'sleep', 'medical', 'wellness'],
            'creativity': ['create', 'design', 'art', 'music', 'write', 'imagine'],
            'problem_solving': ['problem', 'solution', 'fix', 'resolve', 'challenge']
        }
        
        # Sentiment indicators for reflection tone
        self.tone_indicators = {
            'positive': ['good', 'great', 'wonderful', 'amazing', 'happy', 'love', 'excited'],
            'negative': ['bad', 'terrible', 'awful', 'sad', 'angry', 'frustrated', 'disappointed'],
            'neutral': ['okay', 'fine', 'normal', 'regular', 'usual', 'typical'],
            'mixed': ['complicated', 'complex', 'bittersweet', 'conflicted', 'uncertain']
        }
        
        logger.info("🤔 ReflectionAgent initialized for memory synthesis")
    
    def generate_daily_reflection(
        self, 
        events: List[Dict[str, Any]], 
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive daily reflection from events.
        
        Args:
            events: List of memory events from the day
            target_date: Date to reflect on (defaults to today)
            
        Returns:
            Dict containing the daily reflection
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            if not events:
                return self._create_empty_reflection(target_date, 'daily')
            
            # Analyze the day's events
            analysis = self._analyze_events(events)
            
            # Generate reflection sections
            reflection = {
                'id': f"reflection_daily_{target_date.isoformat()}",
                'type': 'daily',
                'date': target_date.isoformat(),
                'event_count': len(events),
                'created_at': datetime.now().isoformat()
            }
            
            # Emotional tone analysis
            reflection['emotional_tone'] = self._analyze_emotional_tone(events, analysis)
            
            # Key events identification
            reflection['key_events'] = self._identify_key_events(events, analysis)
            
            # Interaction patterns
            reflection['interaction_patterns'] = self._analyze_interaction_patterns(events, analysis)
            
            # Learning moments
            reflection['learning_moments'] = self._extract_learning_moments(events, analysis)
            
            # Memorable quotes
            reflection['memorable_quotes'] = self._extract_memorable_quotes(events)
            
            # Overall reflection summary
            reflection['reflection_summary'] = self._generate_daily_summary(events, analysis, reflection)
            
            # Metadata
            reflection['patterns_detected'] = analysis['patterns']
            reflection['dominant_emotions'] = analysis['emotions'][:3]
            reflection['interaction_summary'] = analysis['interaction_stats']
            
            logger.info(f"📝 Generated daily reflection for {target_date}")
            return reflection
            
        except Exception as e:
            logger.error(f"❌ Error generating daily reflection: {e}")
            return self._create_empty_reflection(target_date, 'daily')
    
    def generate_weekly_reflection(
        self, 
        daily_reflections: List[Dict[str, Any]], 
        start_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Generate a weekly reflection from daily reflections.
        
        Args:
            daily_reflections: List of daily reflections for the week
            start_date: Start of the week (defaults to Monday of current week)
            
        Returns:
            Dict containing the weekly reflection
        """
        if start_date is None:
            today = date.today()
            start_date = today - timedelta(days=today.weekday())
        
        try:
            if not daily_reflections:
                return self._create_empty_reflection(start_date, 'weekly')
            
            # Analyze weekly patterns
            weekly_analysis = self._analyze_weekly_patterns(daily_reflections)
            
            end_date = start_date + timedelta(days=6)
            
            reflection = {
                'id': f"reflection_weekly_{start_date.isoformat()}",
                'type': 'weekly',
                'date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'daily_reflection_count': len(daily_reflections),
                'created_at': datetime.now().isoformat()
            }
            
            # Week overview
            reflection['week_overview'] = self._generate_week_overview(daily_reflections, weekly_analysis)
            
            # Emotional journey
            reflection['emotional_journey'] = self._trace_emotional_journey(daily_reflections)
            
            # Recurring themes
            reflection['recurring_themes'] = self._identify_recurring_themes(daily_reflections, weekly_analysis)
            
            # Relationship dynamics
            reflection['relationship_dynamics'] = self._analyze_relationship_dynamics(daily_reflections)
            
            # Growth insights
            reflection['growth_insights'] = self._extract_growth_insights(daily_reflections, weekly_analysis)
            
            # Future considerations
            reflection['future_considerations'] = self._generate_future_considerations(daily_reflections, weekly_analysis)
            
            # Weekly metadata
            reflection['week_summary'] = weekly_analysis
            
            logger.info(f"📅 Generated weekly reflection for {start_date} to {end_date}")
            return reflection
            
        except Exception as e:
            logger.error(f"❌ Error generating weekly reflection: {e}")
            return self._create_empty_reflection(start_date, 'weekly')
    
    def identify_patterns(self, events: List[Dict[str, Any]], time_window_days: int = 30) -> Dict[str, Any]:
        """
        Identify patterns across a time window of events.
        
        Args:
            events: List of memory events
            time_window_days: Days to analyze for patterns
            
        Returns:
            Dict containing identified patterns
        """
        try:
            analysis = self._analyze_events(events)
            
            patterns = {
                'temporal_patterns': self._find_temporal_patterns(events),
                'emotional_patterns': self._find_emotional_patterns(events, analysis),
                'interaction_patterns': self._find_interaction_patterns(events, analysis),
                'content_patterns': self._find_content_patterns(events, analysis),
                'behavioral_patterns': self._find_behavioral_patterns(events, analysis),
                'identified_at': datetime.now().isoformat(),
                'analysis_period_days': time_window_days,
                'total_events_analyzed': len(events)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Error identifying patterns: {e}")
            return {}
    
    def _analyze_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive analysis of a set of events."""
        analysis = {
            'total_events': len(events),
            'actors': Counter(),
            'event_types': Counter(),
            'emotions': [],
            'patterns': {},
            'interaction_stats': {},
            'content_themes': Counter(),
            'time_distribution': defaultdict(int)
        }
        
        if not events:
            return analysis
        
        # Analyze each event
        emotion_scores = defaultdict(float)
        hourly_distribution = defaultdict(int)
        content_words = []
        
        for event in events:
            # Actor analysis
            actor = event.get('actor', 'unknown')
            analysis['actors'][actor] += 1
            
            # Event type analysis
            event_type = event.get('event_type', 'unknown')
            analysis['event_types'][event_type] += 1
            
            # Emotion analysis
            emotion_data = event.get('emotion_analysis', {})
            if emotion_data:
                detected_emotions = emotion_data.get('detected_emotions', {})
                for emotion, score in detected_emotions.items():
                    emotion_scores[emotion] += score
                
                primary_emotion = emotion_data.get('primary_emotion')
                if primary_emotion:
                    analysis['emotions'].append(primary_emotion)
            
            # Time analysis
            timestamp_str = event.get('timestamp', event.get('created_at', ''))
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    hour = timestamp.hour
                    hourly_distribution[hour] += 1
                except:
                    pass
            
            # Content analysis
            content = event.get('content', '')
            if content:
                words = content.lower().split()
                content_words.extend(words)
                
                # Pattern keyword detection
                for pattern_type, keywords in self.pattern_keywords.items():
                    for keyword in keywords:
                        if keyword in content.lower():
                            if pattern_type not in analysis['patterns']:
                                analysis['patterns'][pattern_type] = 0
                            analysis['patterns'][pattern_type] += 1
        
        # Sort emotions by score
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        analysis['emotions'] = [emotion for emotion, score in sorted_emotions if score > 0]
        
        # Content themes from word frequency
        word_counter = Counter(content_words)
        # Filter out common words and short words
        meaningful_words = {word: count for word, count in word_counter.items() 
                          if len(word) > 3 and count > 1}
        analysis['content_themes'] = Counter(meaningful_words)
        
        # Time distribution
        analysis['time_distribution'] = dict(hourly_distribution)
        
        # Interaction statistics
        total_interactions = len(events)
        unique_actors = len(analysis['actors'])
        avg_events_per_actor = total_interactions / unique_actors if unique_actors > 0 else 0
        
        analysis['interaction_stats'] = {
            'total_interactions': total_interactions,
            'unique_actors': unique_actors,
            'average_events_per_actor': round(avg_events_per_actor, 2),
            'most_active_actor': analysis['actors'].most_common(1)[0] if analysis['actors'] else None
        }
        
        return analysis
    
    def _analyze_emotional_tone(self, events: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the overall emotional tone of the day."""
        if not events:
            return {'tone': 'neutral', 'description': 'No events to analyze', 'confidence': 0.0}
        
        # Collect emotional data
        emotion_intensities = []
        valence_scores = []
        dominant_emotions = analysis.get('emotions', [])
        
        for event in events:
            emotion_data = event.get('emotion_analysis', {})
            if emotion_data:
                intensity = emotion_data.get('emotional_intensity', 0)
                valence = emotion_data.get('valence', 0)
                emotion_intensities.append(intensity)
                valence_scores.append(valence)
        
        if not emotion_intensities:
            return {'tone': 'neutral', 'description': 'No emotional data available', 'confidence': 0.0}
        
        # Calculate averages
        avg_intensity = sum(emotion_intensities) / len(emotion_intensities)
        avg_valence = sum(valence_scores) / len(valence_scores)
        
        # Determine tone
        if avg_valence > 0.3:
            if avg_intensity > 0.6:
                tone = 'very_positive'
                description = 'A highly positive and energetic day'
            else:
                tone = 'positive'
                description = 'A generally positive day'
        elif avg_valence < -0.3:
            if avg_intensity > 0.6:
                tone = 'very_negative'
                description = 'A challenging and emotionally intense day'
            else:
                tone = 'negative'
                description = 'A somewhat difficult day'
        else:
            if avg_intensity > 0.5:
                tone = 'mixed_intense'
                description = 'An emotionally complex and intense day'
            else:
                tone = 'neutral'
                description = 'A relatively calm and balanced day'
        
        return {
            'tone': tone,
            'description': description,
            'average_intensity': round(avg_intensity, 2),
            'average_valence': round(avg_valence, 2),
            'dominant_emotions': dominant_emotions[:3],
            'confidence': min(1.0, len(emotion_intensities) / 10)  # More events = higher confidence
        }
    
    def _identify_key_events(self, events: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify the most significant events of the day."""
        if not events:
            return []
        
        # Score events by multiple factors
        scored_events = []
        
        for event in events:
            score = 0.0
            reasons = []
            
            # Salience score
            salience_data = event.get('salience_analysis', {})
            salience_score = salience_data.get('salience_score', 0.5)
            score += salience_score * 0.4
            if salience_score > 0.7:
                reasons.append('high salience')
            
            # Emotional intensity
            emotion_data = event.get('emotion_analysis', {})
            if emotion_data:
                intensity = emotion_data.get('emotional_intensity', 0)
                score += intensity * 0.3
                if intensity > 0.7:
                    reasons.append('emotionally intense')
            
            # Content length (longer = potentially more important)
            content_length = len(event.get('content', ''))
            length_score = min(1.0, content_length / 200)
            score += length_score * 0.2
            
            # Special keywords indicating importance
            content = event.get('content', '').lower()
            important_keywords = ['important', 'significant', 'remember', 'crucial', 'milestone']
            for keyword in important_keywords:
                if keyword in content:
                    score += 0.1
                    reasons.append(f'contains "{keyword}"')
            
            # User events often more significant than system
            if event.get('actor', '').lower() in ['user', 'human']:
                score += 0.1
                reasons.append('user interaction')
            
            scored_events.append({
                'event': event,
                'significance_score': round(score, 3),
                'reasons': reasons
            })
        
        # Sort by score and take top events
        scored_events.sort(key=lambda x: x['significance_score'], reverse=True)
        
        # Return top 5 events with scores above threshold
        key_events = []
        for item in scored_events[:5]:
            if item['significance_score'] > 0.3:
                key_events.append({
                    'id': item['event'].get('id'),
                    'content': item['event'].get('content', '')[:200] + '...' if len(item['event'].get('content', '')) > 200 else item['event'].get('content', ''),
                    'timestamp': item['event'].get('timestamp', item['event'].get('created_at')),
                    'significance_score': item['significance_score'],
                    'reasons': item['reasons']
                })
        
        return key_events
    
    def _analyze_interaction_patterns(self, events: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze interaction patterns between different actors."""
        patterns = {
            'conversation_flow': [],
            'actor_dominance': {},
            'response_patterns': {},
            'interaction_quality': 'unknown'
        }
        
        if not events or len(events) < 2:
            return patterns
        
        # Analyze conversation flow
        conversation_flow = []
        prev_actor = None
        
        for event in events:
            actor = event.get('actor', 'unknown')
            timestamp = event.get('timestamp', event.get('created_at', ''))
            
            if prev_actor and actor != prev_actor:
                conversation_flow.append({
                    'from': prev_actor,
                    'to': actor,
                    'timestamp': timestamp
                })
            
            prev_actor = actor
        
        patterns['conversation_flow'] = conversation_flow[-10:]  # Last 10 interactions
        
        # Actor dominance (who spoke most)
        actor_stats = analysis.get('interaction_stats', {})
        total_events = actor_stats.get('total_interactions', 0)
        
        for actor, count in analysis.get('actors', {}).items():
            dominance = count / total_events if total_events > 0 else 0
            patterns['actor_dominance'][actor] = round(dominance, 3)
        
        # Assess interaction quality
        if len(set(event.get('actor') for event in events)) > 1:
            # Multiple actors = interactive
            avg_emotion_intensity = self._calculate_avg_emotion_intensity(events)
            if avg_emotion_intensity > 0.6:
                patterns['interaction_quality'] = 'intense'
            elif avg_emotion_intensity > 0.3:
                patterns['interaction_quality'] = 'engaged'
            else:
                patterns['interaction_quality'] = 'calm'
        else:
            patterns['interaction_quality'] = 'solo'
        
        return patterns
    
    def _extract_learning_moments(self, events: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract moments that indicate learning or insight."""
        learning_moments = []
        
        learning_indicators = [
            'learned', 'discovered', 'realized', 'understood', 'insight',
            'aha', 'eureka', 'figured out', 'makes sense', 'now i understand',
            'i see', 'that explains', 'interesting', 'never knew', 'didnt know'
        ]
        
        for event in events:
            content = event.get('content', '').lower()
            
            # Check for learning indicators
            found_indicators = []
            for indicator in learning_indicators:
                if indicator in content:
                    found_indicators.append(indicator)
            
            if found_indicators:
                learning_moments.append({
                    'id': event.get('id'),
                    'content': event.get('content', '')[:150] + '...' if len(event.get('content', '')) > 150 else event.get('content', ''),
                    'timestamp': event.get('timestamp', event.get('created_at')),
                    'indicators': found_indicators,
                    'actor': event.get('actor')
                })
        
        return learning_moments[:5]  # Top 5 learning moments
    
    def _extract_memorable_quotes(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract memorable or significant quotes from the day."""
        quotes = []
        
        for event in events:
            content = event.get('content', '')
            
            # Look for quotable content
            is_quotable = False
            reasons = []
            
            # Longer, substantial content
            if len(content) > 50 and len(content) < 300:
                is_quotable = True
                reasons.append('substantial content')
            
            # Contains wisdom/insight keywords
            wisdom_keywords = ['wisdom', 'advice', 'lesson', 'truth', 'important', 'remember']
            for keyword in wisdom_keywords:
                if keyword in content.lower():
                    is_quotable = True
                    reasons.append(f'contains {keyword}')
            
            # Strong emotional content
            emotion_data = event.get('emotion_analysis', {})
            if emotion_data and emotion_data.get('emotional_intensity', 0) > 0.7:
                is_quotable = True
                reasons.append('emotionally intense')
            
            # Questions (often thought-provoking)
            if '?' in content and len(content) > 20:
                is_quotable = True
                reasons.append('thought-provoking question')
            
            if is_quotable:
                quotes.append({
                    'content': content,
                    'actor': event.get('actor'),
                    'timestamp': event.get('timestamp', event.get('created_at')),
                    'reasons': reasons,
                    'emotion': emotion_data.get('primary_emotion') if emotion_data else None
                })
        
        # Sort by emotional intensity and content length
        quotes.sort(key=lambda x: len(x['content']), reverse=True)
        
        return quotes[:3]  # Top 3 memorable quotes
    
    def _generate_daily_summary(
        self, 
        events: List[Dict[str, Any]], 
        analysis: Dict[str, Any], 
        reflection: Dict[str, Any]
    ) -> str:
        """Generate a narrative summary of the day."""
        if not events:
            return "Today was quiet with no recorded interactions or events."
        
        # Build summary components
        summary_parts = []
        
        # Event count and timing
        event_count = len(events)
        time_dist = analysis.get('time_distribution', {})
        peak_hours = sorted(time_dist.items(), key=lambda x: x[1], reverse=True)[:2]
        
        if event_count == 1:
            summary_parts.append("Today had a single notable interaction")
        elif event_count < 5:
            summary_parts.append(f"Today was relatively quiet with {event_count} interactions")
        elif event_count < 15:
            summary_parts.append(f"Today was moderately active with {event_count} interactions")
        else:
            summary_parts.append(f"Today was very active with {event_count} interactions")
        
        if peak_hours:
            peak_hour = peak_hours[0][0]
            if peak_hour < 12:
                time_period = "morning"
            elif peak_hour < 17:
                time_period = "afternoon"
            else:
                time_period = "evening"
            summary_parts.append(f", with most activity in the {time_period}")
        
        # Emotional tone
        emotional_tone = reflection.get('emotional_tone', {})
        tone_desc = emotional_tone.get('description', 'The emotional tone was neutral')
        summary_parts.append(f". {tone_desc}")
        
        # Key patterns
        patterns = analysis.get('patterns', {})
        if patterns:
            top_pattern = max(patterns.items(), key=lambda x: x[1])
            pattern_name = top_pattern[0].replace('_', ' ')
            summary_parts.append(f" The day featured notable {pattern_name} themes")
        
        # Interaction quality
        interaction_patterns = reflection.get('interaction_patterns', {})
        quality = interaction_patterns.get('interaction_quality', 'unknown')
        if quality != 'unknown':
            summary_parts.append(f", with {quality} interactions")
        
        # Learning moments
        learning_moments = reflection.get('learning_moments', [])
        if learning_moments:
            summary_parts.append(f". There were {len(learning_moments)} notable learning moments")
        
        summary_parts.append(".")
        
        return "".join(summary_parts)
    
    def _analyze_weekly_patterns(self, daily_reflections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns across daily reflections for weekly insights."""
        analysis = {
            'daily_summaries': [],
            'emotional_trends': {},
            'pattern_evolution': {},
            'interaction_trends': {},
            'peak_days': [],
            'quiet_days': []
        }
        
        if not daily_reflections:
            return analysis
        
        # Process each daily reflection
        for daily in daily_reflections:
            day_summary = {
                'date': daily.get('date'),
                'event_count': daily.get('event_count', 0),
                'dominant_emotion': daily.get('dominant_emotions', [None])[0],
                'tone': daily.get('emotional_tone', {}).get('tone', 'neutral'),
                'key_patterns': list(daily.get('patterns_detected', {}).keys())
            }
            analysis['daily_summaries'].append(day_summary)
        
        # Identify peak and quiet days
        event_counts = [d.get('event_count', 0) for d in daily_reflections]
        if event_counts:
            avg_events = sum(event_counts) / len(event_counts)
            
            for daily in daily_reflections:
                event_count = daily.get('event_count', 0)
                if event_count > avg_events * 1.5:
                    analysis['peak_days'].append(daily.get('date'))
                elif event_count < avg_events * 0.5:
                    analysis['quiet_days'].append(daily.get('date'))
        
        return analysis
    
    def _calculate_avg_emotion_intensity(self, events: List[Dict[str, Any]]) -> float:
        """Calculate average emotional intensity across events."""
        intensities = []
        for event in events:
            emotion_data = event.get('emotion_analysis', {})
            if emotion_data:
                intensity = emotion_data.get('emotional_intensity', 0)
                intensities.append(intensity)
        
        return sum(intensities) / len(intensities) if intensities else 0.0
    
    def _create_empty_reflection(self, target_date: date, reflection_type: str) -> Dict[str, Any]:
        """Create an empty reflection for days with no events."""
        return {
            'id': f"reflection_{reflection_type}_{target_date.isoformat()}",
            'type': reflection_type,
            'date': target_date.isoformat(),
            'event_count': 0,
            'created_at': datetime.now().isoformat(),
            'summary': f"No events recorded for {target_date.isoformat()}",
            'note': 'Empty reflection - no events to analyze'
        }
    
    # Additional helper methods for weekly reflection generation
    def _generate_week_overview(self, daily_reflections: List[Dict[str, Any]], weekly_analysis: Dict[str, Any]) -> str:
        """Generate overview text for the week."""
        if not daily_reflections:
            return "This was a quiet week with minimal recorded activity."
        
        total_events = sum(d.get('event_count', 0) for d in daily_reflections)
        avg_daily_events = total_events / len(daily_reflections) if daily_reflections else 0
        
        peak_days = weekly_analysis.get('peak_days', [])
        quiet_days = weekly_analysis.get('quiet_days', [])
        
        overview = f"This week featured {total_events} total interactions across {len(daily_reflections)} days, "
        overview += f"averaging {avg_daily_events:.1f} interactions per day. "
        
        if peak_days:
            overview += f"Peak activity occurred on {', '.join(peak_days)}. "
        
        if quiet_days:
            overview += f"Quieter periods were observed on {', '.join(quiet_days)}."
        
        return overview
    
    def _trace_emotional_journey(self, daily_reflections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trace the emotional journey through the week."""
        journey = {
            'daily_tones': [],
            'emotional_progression': 'stable',
            'peak_emotional_day': None,
            'emotional_variance': 0.0
        }
        
        for daily in daily_reflections:
            tone_data = daily.get('emotional_tone', {})
            tone = tone_data.get('tone', 'neutral')
            intensity = tone_data.get('average_intensity', 0)
            
            journey['daily_tones'].append({
                'date': daily.get('date'),
                'tone': tone,
                'intensity': intensity
            })
        
        return journey
    
    def _identify_recurring_themes(self, daily_reflections: List[Dict[str, Any]], weekly_analysis: Dict[str, Any]) -> List[str]:
        """Identify themes that appeared multiple times during the week."""
        theme_counts = Counter()
        
        for daily in daily_reflections:
            patterns = daily.get('patterns_detected', {})
            for pattern in patterns.keys():
                theme_counts[pattern] += 1
        
        # Return themes that appeared on multiple days
        recurring = [theme for theme, count in theme_counts.items() if count >= 2]
        return recurring[:5]  # Top 5 recurring themes
    
    def _analyze_relationship_dynamics(self, daily_reflections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze relationship and interaction dynamics across the week."""
        return {
            'interaction_consistency': 'varied',
            'primary_relationships': [],
            'communication_patterns': 'mixed'
        }
    
    def _extract_growth_insights(self, daily_reflections: List[Dict[str, Any]], weekly_analysis: Dict[str, Any]) -> List[str]:
        """Extract insights about growth and learning from the week."""
        insights = []
        
        # Count learning moments across the week
        total_learning_moments = sum(
            len(daily.get('learning_moments', [])) 
            for daily in daily_reflections
        )
        
        if total_learning_moments > 0:
            insights.append(f"Demonstrated active learning with {total_learning_moments} learning moments throughout the week")
        
        return insights[:3]  # Top 3 insights
    
    def _generate_future_considerations(self, daily_reflections: List[Dict[str, Any]], weekly_analysis: Dict[str, Any]) -> List[str]:
        """Generate suggestions for future focus based on weekly patterns."""
        considerations = []
        
        # Analyze patterns for suggestions
        all_patterns = []
        for daily in daily_reflections:
            all_patterns.extend(daily.get('patterns_detected', {}).keys())
        
        pattern_counts = Counter(all_patterns)
        
        if 'emotional' in pattern_counts and pattern_counts['emotional'] >= 3:
            considerations.append("Consider exploring emotional regulation techniques given the emotional intensity of the week")
        
        if 'learning' in pattern_counts:
            considerations.append("Continue pursuing learning opportunities as they appear to be a positive pattern")
        
        return considerations[:3]
    
    def _find_temporal_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find temporal patterns in the events."""
        return {'daily_rhythm': 'varied', 'peak_times': []}
    
    def _find_emotional_patterns(self, events: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Find emotional patterns in the events."""
        return {'emotional_cycles': [], 'trigger_patterns': []}
    
    def _find_interaction_patterns(self, events: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Find interaction patterns in the events."""
        return {'conversation_styles': [], 'response_patterns': []}
    
    def _find_content_patterns(self, events: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Find content patterns in the events."""
        return {'topic_clusters': [], 'language_patterns': []}
    
    def _find_behavioral_patterns(self, events: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Find behavioral patterns in the events."""
        return {'activity_patterns': [], 'engagement_patterns': []}

# Convenience function
def create_reflection_agent() -> ReflectionAgent:
    """Create and return a reflection agent instance."""
    return ReflectionAgent()
