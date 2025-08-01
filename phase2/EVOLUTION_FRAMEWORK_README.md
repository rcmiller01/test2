# Evolution Framework - Phase 2 Implementation

## Overview
This directory contains the complete evolutionary framework for self-improving AI agents, supporting multiple agent types with specialized scoring and mutation algorithms.

## Core Components

### 1. evolve_core.py
The foundation evolutionary framework supporting all agent types:

**Supported Agents:**
- **Mirror**: Self-reflection and contradiction detection
- **Dreamer**: Narrative generation and creative synthesis  
- **Analyst**: Data processing and pattern recognition
- **Painter**: Visual synthesis and artistic generation
- **Eyla**: Legacy emotional core agent (deprecated)
- **EmotionalCore**: General emotional core agent (user-facing anchor identity)

**Key Features:**
- EvolveCandidate dataclass for variant management
- EvolutionManager with intelligent mutation algorithms
- Archive system with JSON persistence
- Agent-specific scoring heuristics
- Baseline comparison and assessment rules

### 2. evolve_emotional_core.py
Specialized evolution script for emotional core agents with detailed reflection analysis:

**Capabilities:**
- Comprehensive parameter interpretation
- Emotional trajectory assessment
- Detailed reflection summaries
- Archive management integration

### 3. evolution_archive/
Persistent storage for evolved variants:
```
evolution_archive/
├── EmotionalCore/
│   ├── variant_20250801_142515.json  # core_emotional_v001 (score: 1.000)
│   └── variant_20250801_142604.json  # EmotionalCore_v002 (score: 1.000)
└── [other_agents]/
```

## Usage Examples

### Basic Evolution Test
```bash
python evolve_core.py
```
Runs evolution test with EmotionalCore agent as default.

### Emotional Core Focused Evolution
```bash
python evolve_emotional_core.py
```
Runs specialized emotional core evolution with detailed analysis.

### Custom Agent Evolution
```python
from evolve_core import EvolutionManager

manager = EvolutionManager()
candidate = manager.propose_variant("Mirror")
score = manager.score_candidate(candidate)
manager.commit_candidate(candidate)
```

## Parameter Baselines

### EmotionalCore Agent
- **emotional_resonance**: 0.85 - Core emotional processing capability
- **reflection_depth**: 0.78 - Self-analysis and introspection level
- **presence_stability**: 0.82 - Consistency of personality expression
- **memory_gracefulness**: 0.76 - Integration of past interactions
- **seed_alignment_sensitivity**: 0.88 - Adherence to initial persona
- **drift_tolerance**: 0.12 - Acceptance of personality evolution
- **soft_response_richness**: 0.81 - Emotional depth in responses

### Other Agents
Each agent type has specialized parameter sets optimized for their role.

## Scoring System

### Performance Calculation
- Base score of 0.8
- Parameter coherence bonuses
- Range validation penalties
- Agent-specific heuristics

### Assessment Rules
- **emotional_enhancement_high_potential**: Strong emotional improvements
- **balanced_refinement**: Moderate improvements across parameters
- **experimental_shift**: Significant parameter changes
- **minor_adjustment**: Small incremental changes

## Evolution Results

### Recent Achievements
- **core_emotional_v001**: Perfect 1.000 score with balanced improvements
- **EmotionalCore_v002**: High emotional resonance enhancement (7.3% increase)

### Success Patterns
- Emotional resonance improvements consistently yield high scores
- Balanced parameter adjustments maintain stability
- Archive system successfully preserves evolutionary history

## Integration with Council System

The evolution framework integrates with the AI Council system in `/config/council_manifest.json`:

1. **Council Members** can evolve their specialized parameters
2. **Background Tasks** benefit from optimized agent performance
3. **Task Routing** improves with evolved agent capabilities

## Future Enhancements

1. **Multi-Objective Optimization**: Balance multiple performance metrics
2. **Cross-Agent Learning**: Share successful mutations between agent types
3. **Automatic Evolution**: Scheduled background evolution cycles
4. **Performance Metrics**: Real-world usage-based scoring
5. **Rollback System**: Revert to previous variants if performance degrades

## Technical Notes

- All variants are timestamped and archived for complete evolutionary history
- Mutation strength is configurable (default: 12% for emotional agents)
- JSON serialization ensures cross-platform compatibility
- Type hints and dataclasses provide robust code structure
