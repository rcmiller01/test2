"""
True Recall - Emotion Tagging System

Advanced emotion detection and analysis using TextBlob sentiment analysis
combined with contextual emotion mapping and intensity scoring.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional, Set
from textblob import TextBlob
from datetime import datetime

logger = logging.getLogger(__name__)

class EmotionTagger:
    """
    Sophisticated emotion analysis system for memory events.
    
    Uses TextBlob for sentiment analysis, keyword detection for specific emotions,
    and contextual analysis to tag memories with rich emotional metadata.
    """
    
    def __init__(self):
        """Initialize the emotion tagger with emotion mappings and patterns."""
        
        # Core emotion categories with keywords and patterns
        self.emotion_keywords = {
            # Primary emotions
            'joy': {
                'keywords': ['happy', 'joy', 'excited', 'delighted', 'cheerful', 'elated', 
                           'thrilled', 'content', 'pleased', 'glad', 'wonderful', 'amazing',
                           'awesome', 'fantastic', 'great', 'love', 'enjoy', 'celebrate'],
                'phrases': ['feel good', 'so happy', 'love it', 'amazing time', 'best day'],
                'emoji': ['😊', '😄', '😃', '🥳', '💖', '❤️', '🎉']
            },
            'sadness': {
                'keywords': ['sad', 'depressed', 'down', 'blue', 'melancholy', 'grief',
                           'sorrow', 'heartbroken', 'disappointed', 'dejected', 'gloomy',
                           'miserable', 'tragic', 'crying', 'tears', 'upset'],
                'phrases': ['feel bad', 'so sad', 'breaks my heart', 'feeling down'],
                'emoji': ['😢', '😭', '💔', '😞', '😔', '☹️']
            },
            'anger': {
                'keywords': ['angry', 'mad', 'furious', 'rage', 'irritated', 'annoyed',
                           'frustrated', 'outraged', 'livid', 'hostile', 'bitter',
                           'resentful', 'hate', 'stupid', 'damn', 'annoying'],
                'phrases': ['so angry', 'pissed off', 'fed up', 'sick of', 'hate it'],
                'emoji': ['😠', '😡', '🤬', '💢', '👿']
            },
            'fear': {
                'keywords': ['afraid', 'scared', 'fear', 'anxious', 'worried', 'nervous',
                           'terrified', 'panic', 'frightened', 'concerned', 'stress',
                           'overwhelmed', 'insecure', 'uncertain', 'doubt'],
                'phrases': ['so scared', 'worried about', 'afraid of', 'nervous about'],
                'emoji': ['😨', '😰', '😱', '🫣', '😟', '😧']
            },
            'surprise': {
                'keywords': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned',
                           'bewildered', 'unexpected', 'sudden', 'wow', 'omg', 'whoa'],
                'phrases': ['so surprised', 'cant believe', 'never expected', 'what a surprise'],
                'emoji': ['😲', '😯', '🤯', '😮', '😧']
            },
            'disgust': {
                'keywords': ['disgusted', 'gross', 'awful', 'terrible', 'horrible',
                           'repulsive', 'sick', 'nasty', 'revolting', 'appalling'],
                'phrases': ['so gross', 'makes me sick', 'cant stand', 'disgusting'],
                'emoji': ['🤢', '🤮', '😷', '🙄']
            },
            
            # Complex emotions
            'love': {
                'keywords': ['love', 'adore', 'cherish', 'devotion', 'affection', 'romance',
                           'passion', 'caring', 'tender', 'sweet', 'darling', 'honey'],
                'phrases': ['love you', 'so much love', 'in love', 'love this'],
                'emoji': ['❤️', '💕', '💖', '💝', '😍', '🥰']
            },
            'trust': {
                'keywords': ['trust', 'reliable', 'dependable', 'faithful', 'honest',
                           'loyal', 'confidence', 'security', 'belief', 'faith'],
                'phrases': ['trust you', 'have faith', 'can count on', 'believe in'],
                'emoji': ['🤝', '💪', '👍']
            },
            'anticipation': {
                'keywords': ['excited', 'eager', 'anticipate', 'look forward', 'expect',
                           'hopeful', 'optimistic', 'enthusiastic', 'ready', 'waiting'],
                'phrases': ['cant wait', 'looking forward', 'so excited', 'hope for'],
                'emoji': ['🤗', '😍', '🥳', '🎯']
            },
            'contempt': {
                'keywords': ['contempt', 'scorn', 'disdain', 'superior', 'beneath',
                           'pathetic', 'worthless', 'inferior', 'ridiculous'],
                'phrases': ['look down on', 'better than', 'so pathetic'],
                'emoji': ['🙄', '😤', '😏']
            },
            
            # Nuanced emotions
            'pride': {
                'keywords': ['proud', 'accomplished', 'achievement', 'success', 'victory',
                           'triumph', 'excellent', 'outstanding', 'impressed'],
                'phrases': ['so proud', 'great job', 'well done', 'accomplished'],
                'emoji': ['😤', '💪', '🏆', '⭐']
            },
            'shame': {
                'keywords': ['shame', 'embarrassed', 'humiliated', 'guilty', 'regret',
                           'sorry', 'apologize', 'mistake', 'wrong', 'disappointed in myself'],
                'phrases': ['so ashamed', 'feel guilty', 'made a mistake', 'sorry for'],
                'emoji': ['😳', '😞', '🙈', '😔']
            },
            'gratitude': {
                'keywords': ['grateful', 'thankful', 'appreciate', 'blessed', 'thank you',
                           'thanks', 'kind', 'helpful', 'generous', 'acknowledge'],
                'phrases': ['thank you', 'so grateful', 'appreciate it', 'blessed to have'],
                'emoji': ['🙏', '💕', '😊', '🥹']
            },
            'curiosity': {
                'keywords': ['curious', 'wonder', 'interesting', 'fascinating', 'explore',
                           'discover', 'learn', 'question', 'investigate', 'mysterious'],
                'phrases': ['wonder about', 'curious to know', 'want to learn', 'interesting'],
                'emoji': ['🤔', '🧐', '👀', '💭']
            },
            'confusion': {
                'keywords': ['confused', 'puzzled', 'unclear', 'lost', 'bewildered',
                           'perplexed', 'understand', 'explain', 'what', 'how', 'why'],
                'phrases': ['dont understand', 'confused about', 'makes no sense', 'lost me'],
                'emoji': ['😕', '🤔', '😵‍💫', '🤷']
            },
            'nostalgia': {
                'keywords': ['nostalgic', 'remember', 'memories', 'past', 'childhood',
                           'miss', 'reminisce', 'old times', 'used to', 'back then'],
                'phrases': ['remember when', 'miss those days', 'brings back memories', 'old times'],
                'emoji': ['🥹', '💭', '📸', '⏰']
            }
        }
        
        # Emotion intensity indicators
        self.intensity_amplifiers = {
            'very': 1.3,
            'extremely': 1.5,
            'incredibly': 1.4,
            'absolutely': 1.4,
            'totally': 1.3,
            'completely': 1.3,
            'utterly': 1.4,
            'so': 1.2,
            'really': 1.2,
            'quite': 1.1,
            'rather': 1.1,
            'somewhat': 0.8,
            'slightly': 0.7,
            'a bit': 0.7,
            'a little': 0.7,
            'kind of': 0.8,
            'sort of': 0.8
        }
        
        # Negation words that flip sentiment
        self.negation_words = {
            'not', 'no', 'never', 'none', 'nobody', 'nothing', 'neither',
            'nowhere', 'hardly', 'scarcely', 'barely', 'seldom', "don't",
            "doesn't", "won't", "can't", "isn't", "aren't", "wasn't",
            "weren't", "hasn't", "haven't", "hadn't", "shouldn't", "couldn't",
            "wouldn't", "mustn't", "mightn't", "needn't", "daren't", "mayn't"
        }
        
        logger.info("🎭 EmotionTagger initialized with comprehensive emotion mapping")
    
    def analyze_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive emotion analysis on text.
        
        Args:
            text: The text to analyze
            context: Optional context information (speaker, situation, etc.)
            
        Returns:
            Dict containing emotion analysis results
        """
        if not text or not text.strip():
            return self._create_neutral_analysis()
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # TextBlob sentiment analysis
            blob = TextBlob(cleaned_text)
            sentiment = blob.sentiment
            
            # Detect emotions with confidence scores
            detected_emotions = self._detect_emotions(cleaned_text)
            
            # Calculate emotional intensity
            intensity_score = self._calculate_intensity(cleaned_text, detected_emotions)
            
            # Determine emotional valence and arousal
            valence, arousal = self._calculate_valence_arousal(sentiment, detected_emotions)
            
            # Apply context adjustments if available
            if context:
                detected_emotions = self._apply_context_adjustments(detected_emotions, context)
            
            # Generate emotional fingerprint
            emotional_fingerprint = self._generate_emotional_fingerprint(detected_emotions)
            
            analysis = {
                'detected_emotions': detected_emotions,
                'primary_emotion': self._get_primary_emotion(detected_emotions),
                'secondary_emotions': self._get_secondary_emotions(detected_emotions),
                'sentiment_polarity': round(sentiment.polarity, 3),
                'sentiment_subjectivity': round(sentiment.subjectivity, 3),
                'emotional_intensity': round(intensity_score, 3),
                'valence': round(valence, 3),  # Positive/negative dimension
                'arousal': round(arousal, 3),   # High/low energy dimension
                'emotional_fingerprint': emotional_fingerprint,
                'analysis_confidence': self._calculate_confidence(text, detected_emotions),
                'analyzed_at': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in emotion analysis: {e}")
            return self._create_neutral_analysis()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis."""
        # Convert to lowercase for keyword matching
        cleaned = text.lower()
        
        # Remove excessive punctuation but keep basic structure
        cleaned = re.sub(r'[!]{2,}', '!', cleaned)
        cleaned = re.sub(r'[?]{2,}', '?', cleaned)
        cleaned = re.sub(r'[.]{3,}', '...', cleaned)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions using keyword matching and pattern analysis."""
        detected = {}
        words = text.split()
        text_length = len(words)
        
        # Check each emotion category
        for emotion, patterns in self.emotion_keywords.items():
            score = 0.0
            matches = 0
            
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword in text:
                    base_score = 0.3
                    
                    # Apply intensity modifiers
                    for word in words:
                        if keyword in word or word in keyword:
                            # Check for intensity amplifiers nearby
                            word_index = words.index(word) if word in words else -1
                            if word_index >= 0:
                                for i in range(max(0, word_index-2), min(len(words), word_index+3)):
                                    if words[i] in self.intensity_amplifiers:
                                        base_score *= self.intensity_amplifiers[words[i]]
                                
                                # Check for negation
                                negated = False
                                for i in range(max(0, word_index-3), word_index):
                                    if words[i] in self.negation_words:
                                        negated = True
                                        break
                                
                                if negated:
                                    base_score *= 0.2  # Heavily reduce but don't eliminate
                            
                            score += base_score
                            matches += 1
            
            # Check phrases
            for phrase in patterns['phrases']:
                if phrase in text:
                    score += 0.4
                    matches += 1
            
            # Check emoji patterns
            for emoji in patterns['emoji']:
                if emoji in text:
                    score += 0.2
                    matches += 1
            
            # Normalize score based on text length and matches
            if matches > 0:
                # Account for text length (shorter texts should have higher relative scores)
                length_factor = min(1.0, 10 / text_length) if text_length > 0 else 1.0
                normalized_score = (score / max(1, matches)) * (1 + length_factor * 0.5)
                detected[emotion] = min(1.0, normalized_score)  # Cap at 1.0
        
        return detected
    
    def _calculate_intensity(self, text: str, emotions: Dict[str, float]) -> float:
        """Calculate overall emotional intensity."""
        base_intensity = sum(emotions.values())
        
        # Check for intensity indicators
        words = text.split()
        intensity_multiplier = 1.0
        
        for word in words:
            if word in self.intensity_amplifiers:
                intensity_multiplier *= self.intensity_amplifiers[word]
        
        # Punctuation intensity indicators
        exclamation_count = text.count('!')
        question_count = text.count('?')
        caps_words = len([w for w in words if w.isupper() and len(w) > 1])
        
        punctuation_intensity = 1.0 + (exclamation_count * 0.1) + (question_count * 0.05)
        caps_intensity = 1.0 + (caps_words * 0.1)
        
        total_intensity = base_intensity * intensity_multiplier * punctuation_intensity * caps_intensity
        
        return min(2.0, total_intensity)  # Cap at 2.0
    
    def _calculate_valence_arousal(self, sentiment: Any, emotions: Dict[str, float]) -> Tuple[float, float]:
        """Calculate emotional valence (positive/negative) and arousal (energy level)."""
        
        # Start with TextBlob sentiment polarity for valence
        valence = sentiment.polarity
        
        # Adjust based on detected emotions
        positive_emotions = ['joy', 'love', 'trust', 'anticipation', 'pride', 'gratitude']
        negative_emotions = ['sadness', 'anger', 'fear', 'disgust', 'shame', 'contempt']
        
        positive_boost = sum(emotions.get(e, 0) for e in positive_emotions)
        negative_boost = sum(emotions.get(e, 0) for e in negative_emotions)
        
        valence = valence + (positive_boost * 0.3) - (negative_boost * 0.3)
        valence = max(-1.0, min(1.0, valence))  # Clamp between -1 and 1
        
        # Calculate arousal based on emotion types
        high_arousal_emotions = ['anger', 'fear', 'joy', 'surprise', 'anticipation']
        low_arousal_emotions = ['sadness', 'trust', 'disgust', 'contempt']
        
        high_arousal_score = sum(emotions.get(e, 0) for e in high_arousal_emotions)
        low_arousal_score = sum(emotions.get(e, 0) for e in low_arousal_emotions)
        
        arousal = (high_arousal_score - low_arousal_score * 0.5) * 0.5
        arousal = max(-1.0, min(1.0, arousal))  # Clamp between -1 and 1
        
        return valence, arousal
    
    def _apply_context_adjustments(self, emotions: Dict[str, float], context: Dict[str, Any]) -> Dict[str, float]:
        """Apply contextual adjustments to emotion scores."""
        adjusted = emotions.copy()
        
        # Adjust based on speaker
        speaker = context.get('speaker', '').lower()
        if speaker == 'system':
            # System messages are typically neutral, reduce emotional scores
            for emotion in adjusted:
                adjusted[emotion] *= 0.7
        
        # Adjust based on conversation type
        conv_type = context.get('conversation_type', '').lower()
        if conv_type == 'support':
            # Support conversations might have heightened emotions
            for emotion in ['sadness', 'fear', 'anger']:
                if emotion in adjusted:
                    adjusted[emotion] *= 1.2
        
        # Adjust based on time of day
        hour = context.get('hour')
        if hour is not None:
            if 22 <= hour or hour <= 6:  # Late night/early morning
                # People might be more emotional when tired
                for emotion in adjusted:
                    adjusted[emotion] *= 1.1
        
        return adjusted
    
    def _generate_emotional_fingerprint(self, emotions: Dict[str, float]) -> str:
        """Generate a unique emotional fingerprint for the text."""
        # Sort emotions by strength and create a signature
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 3 emotions with scores > 0.1
        significant_emotions = [(e, s) for e, s in sorted_emotions if s > 0.1][:3]
        
        if not significant_emotions:
            return "neutral"
        
        # Create fingerprint
        fingerprint_parts = []
        for emotion, score in significant_emotions:
            intensity_level = "high" if score > 0.6 else "med" if score > 0.3 else "low"
            fingerprint_parts.append(f"{emotion}:{intensity_level}")
        
        return "+".join(fingerprint_parts)
    
    def _get_primary_emotion(self, emotions: Dict[str, float]) -> Optional[str]:
        """Get the strongest detected emotion."""
        if not emotions:
            return None
        
        max_emotion = max(emotions.items(), key=lambda x: x[1])
        return max_emotion[0] if max_emotion[1] > 0.1 else None
    
    def _get_secondary_emotions(self, emotions: Dict[str, float], limit: int = 3) -> List[str]:
        """Get secondary emotions (excluding primary)."""
        primary = self._get_primary_emotion(emotions)
        
        secondary = [(e, s) for e, s in emotions.items() 
                    if e != primary and s > 0.1]
        secondary.sort(key=lambda x: x[1], reverse=True)
        
        return [e for e, s in secondary[:limit]]
    
    def _calculate_confidence(self, text: str, emotions: Dict[str, float]) -> float:
        """Calculate confidence in the emotion analysis."""
        if not text or not emotions:
            return 0.0
        
        # Base confidence on text length
        text_length = len(text.split())
        length_confidence = min(1.0, text_length / 10)
        
        # Confidence based on number of detected emotions
        emotion_count = len([e for e in emotions.values() if e > 0.1])
        emotion_confidence = min(1.0, emotion_count / 3)
        
        # Confidence based on emotion strength
        max_emotion_score = max(emotions.values()) if emotions else 0
        strength_confidence = min(1.0, max_emotion_score * 2)
        
        # Combined confidence
        overall_confidence = (length_confidence + emotion_confidence + strength_confidence) / 3
        
        return round(overall_confidence, 3)
    
    def _create_neutral_analysis(self) -> Dict[str, Any]:
        """Create a neutral emotion analysis result."""
        return {
            'detected_emotions': {},
            'primary_emotion': None,
            'secondary_emotions': [],
            'sentiment_polarity': 0.0,
            'sentiment_subjectivity': 0.0,
            'emotional_intensity': 0.0,
            'valence': 0.0,
            'arousal': 0.0,
            'emotional_fingerprint': 'neutral',
            'analysis_confidence': 0.0,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def get_emotion_summary(self, emotions: Dict[str, float]) -> str:
        """Generate a human-readable emotion summary."""
        if not emotions:
            return "Neutral emotional tone"
        
        significant_emotions = [(e, s) for e, s in emotions.items() if s > 0.2]
        significant_emotions.sort(key=lambda x: x[1], reverse=True)
        
        if not significant_emotions:
            return "Mild emotional undertones"
        
        if len(significant_emotions) == 1:
            emotion, score = significant_emotions[0]
            intensity = "strong" if score > 0.7 else "moderate" if score > 0.4 else "mild"
            return f"{intensity.capitalize()} {emotion}"
        
        elif len(significant_emotions) == 2:
            e1, s1 = significant_emotions[0]
            e2, s2 = significant_emotions[1]
            return f"Mixed {e1} and {e2}"
        
        else:
            emotions_list = [e for e, s in significant_emotions[:3]]
            return f"Complex emotional blend: {', '.join(emotions_list)}"

# Convenience function
def create_emotion_tagger() -> EmotionTagger:
    """Create and return an emotion tagger instance."""
    return EmotionTagger()
