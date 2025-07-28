"""
True Recall - Memory Graph System

Advanced relationship mapping and connection discovery for memory events
using semantic similarity, temporal clustering, and contextual associations.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
import re
import json

# Note: In production, you'd use sentence-transformers and faiss
# For now, we'll use simpler similarity calculations
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available, using fallback similarity")

logger = logging.getLogger(__name__)

class MemoryGraph:
    """
    Graph-based memory relationship system for True Recall.
    
    Creates and maintains a network of connections between memory events
    based on semantic content, temporal proximity, emotional similarity,
    and actor relationships.
    """
    
    def __init__(self, max_connections_per_node: int = 50):
        """Initialize the memory graph."""
        self.max_connections = max_connections_per_node
        
        # Graph storage
        self.nodes = {}  # event_id -> event_data
        self.edges = defaultdict(list)  # event_id -> list of (connected_id, weight, type)
        self.reverse_edges = defaultdict(list)  # For bidirectional lookup
        
        # Similarity thresholds
        self.similarity_thresholds = {
            'semantic': 0.3,
            'temporal': 0.2,
            'emotional': 0.25,
            'actor': 0.4,
            'topic': 0.35
        }
        
        # Connection weights
        self.connection_weights = {
            'semantic': 1.0,
            'temporal': 0.7,
            'emotional': 0.8,
            'actor': 0.6,
            'topic': 0.9,
            'causal': 1.2,  # Cause-effect relationships
            'response': 0.9  # Question-answer pairs
        }
        
        # Temporal clustering parameters
        self.temporal_window_hours = 24
        self.conversation_window_minutes = 30
        
        # Initialize vectorizer for semantic similarity
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1
            )
            self.document_vectors = None
            self.document_ids = []
        
        logger.info("🕸️ MemoryGraph initialized with relationship mapping")
    
    def add_event(self, event: Dict[str, Any]) -> bool:
        """
        Add a new event to the memory graph and create connections.
        
        Args:
            event: Memory event to add
            
        Returns:
            bool: True if successfully added
        """
        try:
            event_id = event.get('id')
            if not event_id:
                logger.error("❌ Event missing ID")
                return False
            
            # Add to nodes
            self.nodes[event_id] = event.copy()
            
            # Find and create connections
            connections = self._find_connections(event)
            
            # Add edges
            for connected_id, weight, connection_type in connections:
                self._add_edge(event_id, connected_id, weight, connection_type)
            
            # Update document vectors for semantic similarity
            if SKLEARN_AVAILABLE:
                self._update_vectors()
            
            logger.debug(f"📌 Added event {event_id} with {len(connections)} connections")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding event to graph: {e}")
            return False
    
    def get_related_events(
        self, 
        event_id: str, 
        max_depth: int = 2, 
        min_weight: float = 0.2,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get events related to a specific event using graph traversal.
        
        Args:
            event_id: Starting event ID
            max_depth: Maximum traversal depth
            min_weight: Minimum connection weight
            max_results: Maximum number of results
            
        Returns:
            List of related events with relationship metadata
        """
        if event_id not in self.nodes:
            return []
        
        try:
            visited = set()
            related = []
            
            # BFS traversal with weight tracking
            queue = deque([(event_id, 0, 1.0, [])])  # (id, depth, weight, path)
            
            while queue and len(related) < max_results:
                current_id, depth, current_weight, path = queue.popleft()
                
                if current_id in visited or depth > max_depth:
                    continue
                
                visited.add(current_id)
                
                # Add to results (skip the starting event)
                if current_id != event_id and current_weight >= min_weight:
                    related_event = self.nodes[current_id].copy()
                    related_event['relationship_weight'] = round(current_weight, 3)
                    related_event['relationship_depth'] = depth
                    related_event['relationship_path'] = path.copy()
                    related.append(related_event)
                
                # Add connected events to queue
                if depth < max_depth:
                    for connected_id, weight, conn_type in self.edges[current_id]:
                        if connected_id not in visited:
                            new_weight = current_weight * weight
                            new_path = path + [conn_type]
                            queue.append((connected_id, depth + 1, new_weight, new_path))
            
            # Sort by relationship weight
            related.sort(key=lambda x: x['relationship_weight'], reverse=True)
            
            return related[:max_results]
            
        except Exception as e:
            logger.error(f"❌ Error finding related events: {e}")
            return []
    
    def find_conversation_threads(self, max_gap_minutes: int = 30) -> List[List[str]]:
        """Find conversation threads based on temporal clustering."""
        try:
            # Group events by temporal proximity
            events_with_timestamps = []
            for event_id, event in self.nodes.items():
                timestamp = self._parse_timestamp(event.get('timestamp', event.get('created_at', '')))
                if timestamp:
                    events_with_timestamps.append((event_id, timestamp))
            
            sorted_events = sorted(events_with_timestamps, key=lambda x: x[1])
            
            threads = []
            current_thread = []
            last_timestamp = None
            
            for event_id, timestamp in sorted_events:
                if (last_timestamp is None or 
                    (timestamp - last_timestamp).total_seconds() <= max_gap_minutes * 60):
                    current_thread.append(event_id)
                else:
                    if len(current_thread) > 1:
                        threads.append(current_thread)
                    current_thread = [event_id]
                
                last_timestamp = timestamp
            
            # Add the last thread
            if len(current_thread) > 1:
                threads.append(current_thread)
            
            return threads
            
        except Exception as e:
            logger.error(f"❌ Error finding conversation threads: {e}")
            return []
    
    def get_central_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find the most connected (central) events in the graph."""
        try:
            # Calculate node centrality (number and weight of connections)
            centrality_scores = {}
            
            for event_id in self.nodes:
                # Sum of connection weights (outgoing)
                outgoing_weight = sum(weight for _, weight, _ in self.edges[event_id])
                
                # Sum of connection weights (incoming)
                incoming_weight = sum(weight for _, weight, _ in self.reverse_edges[event_id])
                
                # Total connections
                total_connections = len(self.edges[event_id]) + len(self.reverse_edges[event_id])
                
                # Combined centrality score
                centrality_scores[event_id] = (outgoing_weight + incoming_weight) * (1 + math.log(1 + total_connections))
            
            # Sort by centrality
            central_events = sorted(centrality_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Prepare results
            results = []
            for event_id, centrality in central_events[:limit]:
                event = self.nodes[event_id].copy()
                event['centrality_score'] = round(centrality, 3)
                event['connection_count'] = len(self.edges[event_id]) + len(self.reverse_edges[event_id])
                results.append(event)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error calculating central events: {e}")
            return []
    
    def find_semantic_clusters(self, min_cluster_size: int = 3) -> List[List[str]]:
        """Find clusters of semantically similar events."""
        if not SKLEARN_AVAILABLE or not self.document_vectors:
            return self._fallback_clustering()
        
        try:
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(self.document_vectors)
            
            # Find clusters using simple thresholding
            clusters = []
            visited = set()
            
            for i, event_id in enumerate(self.document_ids):
                if event_id in visited:
                    continue
                
                # Find similar events
                cluster = [event_id]
                visited.add(event_id)
                
                for j, other_id in enumerate(self.document_ids):
                    if i != j and other_id not in visited:
                        if similarity_matrix[i][j] > self.similarity_thresholds['semantic']:
                            cluster.append(other_id)
                            visited.add(other_id)
                
                if len(cluster) >= min_cluster_size:
                    clusters.append(cluster)
            
            return clusters
            
        except Exception as e:
            logger.error(f"❌ Error finding semantic clusters: {e}")
            return []
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics."""
        try:
            total_nodes = len(self.nodes)
            total_edges = sum(len(connections) for connections in self.edges.values())
            
            # Connection type distribution
            connection_types = defaultdict(int)
            for connections in self.edges.values():
                for _, _, conn_type in connections:
                    connection_types[conn_type] += 1
            
            # Density calculation
            max_possible_edges = total_nodes * (total_nodes - 1)
            density = (total_edges / max_possible_edges) if max_possible_edges > 0 else 0
            
            # Average connections per node
            avg_connections = total_edges / total_nodes if total_nodes > 0 else 0
            
            # Find isolated nodes
            isolated_nodes = [event_id for event_id in self.nodes 
                            if not self.edges[event_id] and not self.reverse_edges[event_id]]
            
            return {
                'total_nodes': total_nodes,
                'total_edges': total_edges,
                'graph_density': round(density, 4),
                'average_connections': round(avg_connections, 2),
                'connection_types': dict(connection_types),
                'isolated_nodes': len(isolated_nodes),
                'largest_component_size': self._get_largest_component_size(),
                'clustering_coefficient': self._calculate_clustering_coefficient()
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating graph statistics: {e}")
            return {}
    
    def _find_connections(self, event: Dict[str, Any]) -> List[Tuple[str, float, str]]:
        """Find connections between the event and existing events."""
        connections = []
        event_id = event['id']
        
        for existing_id, existing_event in self.nodes.items():
            if existing_id == event_id:
                continue
            
            # Calculate different types of connections
            semantic_sim = self._calculate_semantic_similarity(event, existing_event)
            temporal_sim = self._calculate_temporal_similarity(event, existing_event)
            emotional_sim = self._calculate_emotional_similarity(event, existing_event)
            actor_sim = self._calculate_actor_similarity(event, existing_event)
            
            # Check for special relationship types
            causal_weight = self._detect_causal_relationship(event, existing_event)
            response_weight = self._detect_response_relationship(event, existing_event)
            
            # Determine strongest connection type and weight
            similarities = {
                'semantic': semantic_sim,
                'temporal': temporal_sim,
                'emotional': emotional_sim,
                'actor': actor_sim
            }
            
            # Add special relationships
            if causal_weight > 0:
                similarities['causal'] = causal_weight
            if response_weight > 0:
                similarities['response'] = response_weight
            
            # Find the strongest valid connection
            for conn_type, similarity in similarities.items():
                threshold = self.similarity_thresholds.get(conn_type, 0.3)
                if similarity >= threshold:
                    weight = similarity * self.connection_weights.get(conn_type, 1.0)
                    connections.append((existing_id, weight, conn_type))
        
        # Sort by weight and limit connections
        connections.sort(key=lambda x: x[1], reverse=True)
        return connections[:self.max_connections]
    
    def _calculate_semantic_similarity(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """Calculate semantic similarity between two events."""
        content1 = event1.get('content', '').lower()
        content2 = event2.get('content', '').lower()
        
        if not content1 or not content2:
            return 0.0
        
        if SKLEARN_AVAILABLE:
            # Use TF-IDF vectorization for better similarity
            try:
                vectors = self.vectorizer.fit_transform([content1, content2])
                similarity_matrix = cosine_similarity(vectors)
                # Handle both sparse and dense matrices
                if hasattr(similarity_matrix, 'toarray'):
                    similarity_matrix = similarity_matrix.toarray()
                similarity = float(similarity_matrix[0][1])
                return max(0.0, similarity)
            except:
                pass
        
        # Fallback to simple word overlap
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_temporal_similarity(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """Calculate temporal proximity similarity."""
        time1 = self._parse_timestamp(event1.get('timestamp', event1.get('created_at', '')))
        time2 = self._parse_timestamp(event2.get('timestamp', event2.get('created_at', '')))
        
        if not time1 or not time2:
            return 0.0
        
        # Calculate time difference in hours
        time_diff_hours = abs((time1 - time2).total_seconds()) / 3600
        
        # Exponential decay based on time difference
        if time_diff_hours <= 1:
            return 1.0
        elif time_diff_hours <= self.temporal_window_hours:
            return math.exp(-time_diff_hours / self.temporal_window_hours)
        else:
            return 0.0
    
    def _calculate_emotional_similarity(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """Calculate emotional similarity between events."""
        emotion1 = event1.get('emotion_analysis', {})
        emotion2 = event2.get('emotion_analysis', {})
        
        if not emotion1 or not emotion2:
            return 0.0
        
        # Compare primary emotions
        primary1 = emotion1.get('primary_emotion')
        primary2 = emotion2.get('primary_emotion')
        
        primary_match = 1.0 if primary1 and primary1 == primary2 else 0.0
        
        # Compare emotional fingerprints
        fingerprint1 = emotion1.get('emotional_fingerprint', '')
        fingerprint2 = emotion2.get('emotional_fingerprint', '')
        
        fingerprint_similarity = 0.0
        if fingerprint1 and fingerprint2:
            # Simple string similarity for fingerprints
            words1 = set(fingerprint1.split('+'))
            words2 = set(fingerprint2.split('+'))
            if words1 or words2:
                fingerprint_similarity = len(words1.intersection(words2)) / len(words1.union(words2))
        
        # Compare valence and arousal
        valence1 = emotion1.get('valence', 0)
        valence2 = emotion2.get('valence', 0)
        arousal1 = emotion1.get('arousal', 0)
        arousal2 = emotion2.get('arousal', 0)
        
        valence_similarity = 1.0 - abs(valence1 - valence2) / 2.0
        arousal_similarity = 1.0 - abs(arousal1 - arousal2) / 2.0
        
        # Combine emotional factors
        emotional_similarity = (
            primary_match * 0.4 +
            fingerprint_similarity * 0.3 +
            valence_similarity * 0.15 +
            arousal_similarity * 0.15
        )
        
        return max(0.0, emotional_similarity)
    
    def _calculate_actor_similarity(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """Calculate actor-based similarity."""
        actor1 = event1.get('actor', '').lower()
        actor2 = event2.get('actor', '').lower()
        
        if not actor1 or not actor2:
            return 0.0
        
        # Exact match gets full score
        if actor1 == actor2:
            return 1.0
        
        # Partial match for similar actor types
        actor_groups = {
            'user': ['user', 'human', 'person'],
            'system': ['system', 'bot', 'ai', 'assistant'],
            'dolphin': ['dolphin', 'ai_companion']
        }
        
        for group, actors in actor_groups.items():
            if actor1 in actors and actor2 in actors:
                return 0.7
        
        return 0.0
    
    def _detect_causal_relationship(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """Detect cause-effect relationships between events."""
        content1 = event1.get('content', '').lower()
        content2 = event2.get('content', '').lower()
        
        # Look for causal indicators
        causal_phrases = [
            'because of', 'due to', 'caused by', 'as a result', 'therefore',
            'consequently', 'leads to', 'results in', 'triggers', 'influences'
        ]
        
        causal_score = 0.0
        for phrase in causal_phrases:
            if phrase in content1 or phrase in content2:
                causal_score += 0.3
        
        # Check temporal ordering (cause before effect)
        time1 = self._parse_timestamp(event1.get('timestamp', event1.get('created_at', '')))
        time2 = self._parse_timestamp(event2.get('timestamp', event2.get('created_at', '')))
        
        if time1 and time2:
            time_diff_minutes = (time2 - time1).total_seconds() / 60
            if 0 < time_diff_minutes <= 60:  # Effect within 1 hour
                causal_score += 0.2
        
        return min(1.0, causal_score)
    
    def _detect_response_relationship(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """Detect question-answer or response relationships."""
        content1 = event1.get('content', '').lower()
        content2 = event2.get('content', '').lower()
        
        # Check for question-answer patterns
        has_question = '?' in content1
        has_answer_indicators = any(phrase in content2 for phrase in [
            'answer', 'response', 'reply', 'yes', 'no', 'because', 'it is', 'that is'
        ])
        
        response_score = 0.0
        if has_question and has_answer_indicators:
            response_score += 0.6
        
        # Check actor alternation (dialogue pattern)
        actor1 = event1.get('actor', '').lower()
        actor2 = event2.get('actor', '').lower()
        
        if actor1 != actor2 and actor1 and actor2:
            response_score += 0.3
        
        return min(1.0, response_score)
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        if not timestamp_str:
            return None
        
        try:
            # Handle different timestamp formats
            if 'T' in timestamp_str:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                return datetime.fromisoformat(timestamp_str)
        except:
            return None
    
    def _add_edge(self, from_id: str, to_id: str, weight: float, connection_type: str):
        """Add a directed edge to the graph."""
        self.edges[from_id].append((to_id, weight, connection_type))
        self.reverse_edges[to_id].append((from_id, weight, connection_type))
    
    def _update_vectors(self):
        """Update document vectors for semantic similarity."""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            documents = []
            ids = []
            
            for event_id, event in self.nodes.items():
                content = event.get('content', '')
                if content.strip():
                    documents.append(content)
                    ids.append(event_id)
            
            if documents:
                self.document_vectors = self.vectorizer.fit_transform(documents)
                self.document_ids = ids
                
        except Exception as e:
            logger.error(f"❌ Error updating vectors: {e}")
    
    def _fallback_clustering(self) -> List[List[str]]:
        """Fallback clustering method when sklearn is not available."""
        # Simple clustering based on shared keywords
        clusters = []
        visited = set()
        
        for event_id, event in self.nodes.items():
            if event_id in visited:
                continue
            
            content = event.get('content', '').lower()
            words = set(content.split())
            
            cluster = [event_id]
            visited.add(event_id)
            
            # Find events with significant word overlap
            for other_id, other_event in self.nodes.items():
                if other_id in visited:
                    continue
                
                other_content = other_event.get('content', '').lower()
                other_words = set(other_content.split())
                
                if words and other_words:
                    overlap = len(words.intersection(other_words))
                    union = len(words.union(other_words))
                    similarity = overlap / union if union > 0 else 0
                    
                    if similarity > 0.3:
                        cluster.append(other_id)
                        visited.add(other_id)
            
            if len(cluster) >= 3:
                clusters.append(cluster)
        
        return clusters
    
    def _get_largest_component_size(self) -> int:
        """Get the size of the largest connected component."""
        visited = set()
        largest_size = 0
        
        for start_node in self.nodes:
            if start_node in visited:
                continue
            
            # BFS to find component size
            component_size = 0
            queue = deque([start_node])
            component_visited = set()
            
            while queue:
                node = queue.popleft()
                if node in component_visited:
                    continue
                
                component_visited.add(node)
                visited.add(node)
                component_size += 1
                
                # Add connected nodes
                for connected_id, _, _ in self.edges[node]:
                    if connected_id not in component_visited:
                        queue.append(connected_id)
                
                for connected_id, _, _ in self.reverse_edges[node]:
                    if connected_id not in component_visited:
                        queue.append(connected_id)
            
            largest_size = max(largest_size, component_size)
        
        return largest_size
    
    def _calculate_clustering_coefficient(self) -> float:
        """Calculate the average clustering coefficient."""
        if len(self.nodes) < 3:
            return 0.0
        
        total_coefficient = 0.0
        node_count = 0
        
        for node in self.nodes:
            neighbors = set()
            
            # Get all neighbors
            for connected_id, _, _ in self.edges[node]:
                neighbors.add(connected_id)
            for connected_id, _, _ in self.reverse_edges[node]:
                neighbors.add(connected_id)
            
            neighbor_list = list(neighbors)
            neighbor_count = len(neighbor_list)
            
            if neighbor_count < 2:
                continue
            
            # Count connections between neighbors
            connections_between_neighbors = 0
            max_possible_connections = neighbor_count * (neighbor_count - 1)
            
            for i, neighbor1 in enumerate(neighbor_list):
                for neighbor2 in neighbor_list[i+1:]:
                    # Check if neighbor1 and neighbor2 are connected
                    connected = any(conn_id == neighbor2 for conn_id, _, _ in self.edges[neighbor1])
                    connected = connected or any(conn_id == neighbor2 for conn_id, _, _ in self.reverse_edges[neighbor1])
                    
                    if connected:
                        connections_between_neighbors += 2  # Bidirectional
            
            if max_possible_connections > 0:
                coefficient = connections_between_neighbors / max_possible_connections
                total_coefficient += coefficient
                node_count += 1
        
        return total_coefficient / node_count if node_count > 0 else 0.0

# Convenience function
def create_memory_graph() -> MemoryGraph:
    """Create and return a memory graph instance."""
    return MemoryGraph()
