# Pass 1 Quantization Loop Orchestrator

## Overview

The **Pass 1 Quantization Loop Orchestrator** (`pass1_quantization_loop.py`) is a comprehensive automation tool that manages the complete emotional quantization process for large language models. It integrates evaluation datasets, training tracking, and quantization workflows into a single, intelligent loop that optimizes model size while preserving emotional intelligence.

## Key Features

### 🔄 **Automated Quantization Loop**
- **Progressive Quantization**: Tests multiple quantization levels (q8_0 → q6_K → q5_K_M → q4_K_M → q3_K_L → q2_K)
- **Target-Driven Optimization**: Automatically stops when size and quality targets are met
- **Configurable Parameters**: Customizable size limits, degradation thresholds, and iteration counts

### 📊 **Integrated Evaluation System**
- **Emotional Dataset Integration**: Uses `emotional_dataset_builder.py` for comprehensive evaluation scenarios
- **Multi-Metric Assessment**: Evaluates fluency, emotional intensity, match accuracy, empathy, metaphor usage, and sentiment
- **Baseline Comparison**: Establishes baseline metrics for degradation tracking

### 📈 **Progress Tracking & Analytics**
- **Training Tracker Integration**: Automatically logs all results to `emotion_training_tracker.py`
- **Comprehensive Metrics**: Tracks model size, evaluation scores, and processing times
- **Historical Analysis**: Compare performance across iterations and quantization levels

### 🎯 **Intelligent Target Criteria**
- **Size Optimization**: Default target ≤24GB with configurable limits
- **Quality Preservation**: <7% emotional degradation threshold
- **Efficiency Metrics**: Tracks score-per-GB for optimization efficiency

### 🛠️ **Flexible Execution Modes**
- **Single Iteration**: Test specific quantization level (`--run-once`)
- **Full Loop**: Complete automated optimization (`--loop`)
- **Results Analysis**: Review previous runs (`--print-last-results`)
- **Mock Testing**: Development and testing mode (`--mock`)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Pass 1 Quantization Loop                     │
├─────────────────────────────────────────────────────────────┤
│  Configuration & Initialization                            │
│  ├─ QuantizationConfig: Target size, degradation limits    │
│  ├─ EmotionalDatasetBuilder: Load evaluation scenarios     │
│  └─ EmotionTrainingTracker: Initialize progress tracking   │
├─────────────────────────────────────────────────────────────┤
│  Quantization Iteration Loop                               │
│  ├─ Idle Condition Check (optional)                        │
│  ├─ Model Quantization (Ollama/Custom Tool)               │
│  ├─ Response Generation (25 emotional scenarios)           │
│  ├─ Emotional Evaluation (6 metrics)                      │
│  ├─ Progress Tracking (SQLite + JSON backup)              │
│  └─ Target Criteria Assessment                             │
├─────────────────────────────────────────────────────────────┤
│  Results & Analytics                                       │
│  ├─ Best Result Selection                                  │
│  ├─ Summary Generation (JSON export)                      │
│  ├─ Training Tracker Integration                           │
│  └─ Historical Comparison                                  │
└─────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Basic Usage

```bash
# Run complete quantization loop
python pass1_quantization_loop.py --loop --force

# Test single quantization level
python pass1_quantization_loop.py --run-once q4_K_M --force

# Review last run results
python pass1_quantization_loop.py --print-last-results
```

### Advanced Configuration

```bash
# Custom targets and limits
python pass1_quantization_loop.py --loop \
  --target-size 20.0 \
  --max-degradation 0.05 \
  --max-iterations 8 \
  --evaluation-prompts 50

# Alternative quantization tool
python pass1_quantization_loop.py --loop \
  --quant-tool "llama.cpp" \
  --base-model "/path/to/model"

# Development testing
python pass1_quantization_loop.py --loop --mock --force
```

### Integration with Idle Management

```bash
# Run when system is idle (requires idle_watchdog.py)
python pass1_quantization_loop.py --loop

# Force execution regardless of system state
python pass1_quantization_loop.py --loop --force
```

## Configuration Options

### Core Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--base-model` | `meta-llama/Llama-2-13b-chat-hf` | Base model path for quantization |
| `--target-size` | `24.0` | Target model size in GB |
| `--max-degradation` | `0.07` | Maximum emotional degradation (7%) |
| `--max-iterations` | `10` | Maximum quantization iterations |
| `--evaluation-prompts` | `25` | Number of evaluation prompts to use |

### Execution Modes

| Mode | Description |
|------|-------------|
| `--run-once LEVEL` | Single iteration with specified quantization level |
| `--loop` | Full automated quantization loop |
| `--print-last-results` | Display results from previous run |

### Additional Options

| Option | Description |
|--------|-------------|
| `--force` | Skip idle condition checks |
| `--mock` | Enable mock mode for testing |
| `--quant-tool CMD` | Specify quantization tool command |
| `--output-dir PATH` | Set output directory for results |

## Evaluation Metrics

### Emotional Intelligence Assessment

1. **Response Fluency** (0.0-1.0)
   - Sentence structure and coherence
   - Appropriate length and complexity
   - Grammar and punctuation quality

2. **Emotional Intensity** (0.0-1.0)
   - Presence of emotional keywords
   - Appropriate emotional expression
   - Contextual intensity matching

3. **Emotional Match** (0.0-1.0)
   - Alignment with expected emotion
   - Contextual appropriateness
   - Emotional vocabulary usage

4. **Empathy Score** (0.0-1.0)
   - Understanding demonstration
   - Supportive language patterns
   - Perspective-taking indicators

5. **Metaphor Usage** (0.0-1.0)
   - Appropriate figurative language
   - Creative expression balance
   - Contextual relevance

6. **Sentiment Accuracy** (0.0-1.0)
   - Positive/negative sentiment alignment
   - Emotional tone consistency
   - Contextual sentiment matching

### Overall Score Calculation

```python
overall_score = (
    response_fluency + 
    emotional_intensity + 
    emotional_match + 
    empathy_score + 
    metaphor_usage + 
    sentiment_accuracy
) / 6
```

## Output Files

### Summary Reports

- **Location**: `quant_pass1/models/pass1_summary_YYYYMMDD_HHMMSS.json`
- **Contents**: Complete run statistics, best results, all iterations, target achievement status

### Training Tracker Integration

- **Database**: `emotion_training.db` (SQLite)
- **Backup**: `emotion_training_backup.json`
- **Exports**: CSV/JSON exports for external analysis

### Model Outputs

- **Quantized Models**: `{output_dir}/{model_name}_quantized_{quant_level}_iter{N}`
- **Response Logs**: Generated responses for each evaluation scenario

## Integration Points

### Emotional Dataset Builder

```python
# Automatic prompt loading
self.dataset_builder = EmotionalDatasetBuilder()
evaluation_prompts = self.dataset_builder.dataset[:25]
```

### Training Tracker

```python
# Automatic result logging
self.training_tracker = EmotionTrainingTracker()
iteration_id = self.training_tracker.add_iteration(
    model_name=f"llama2_13b_{quant_level}",
    quant_level=QuantLevel.FOUR_BIT,
    pass_type=PassType.PASS_1,
    emotional_metrics=metrics
)
```

### Idle Management (Optional)

```python
# Idle condition checking
import idle_watchdog
watchdog = idle_watchdog.IdleWatchdog()
if not watchdog.is_system_idle():
    # Wait for idle conditions
```

## Error Handling & Recovery

### Quantization Failures
- **Timeout Handling**: Configurable timeout for quantization operations
- **Error Logging**: Detailed error messages and recovery suggestions
- **Graceful Degradation**: Continue with remaining quantization levels

### Evaluation Failures
- **Response Generation**: Mock responses for failed model inference
- **Metric Calculation**: Fallback values for incomplete evaluations
- **Progress Preservation**: Save partial results before failures

### Storage Failures
- **Database Recovery**: Automatic SQLite database repair
- **Backup Systems**: JSON backup for critical data
- **File System**: Robust directory creation and permission handling

## Performance Optimization

### Evaluation Efficiency
- **Parallel Processing**: Batch response generation where possible
- **Caching**: Reuse evaluation results for identical prompts
- **Early Termination**: Stop when target criteria are clearly met

### Resource Management
- **Memory Cleanup**: Automatic model unloading between iterations
- **Disk Space**: Monitor and clean temporary quantization files
- **System Resources**: Idle checking prevents resource conflicts

## Best Practices

### Production Usage

1. **Baseline Establishment**: Always run with least aggressive quantization first
2. **Target Configuration**: Set realistic size and quality targets
3. **Monitoring**: Regular review of training tracker statistics
4. **Backup Strategy**: Maintain copies of successful quantized models

### Development Testing

1. **Mock Mode**: Use `--mock` for rapid iteration testing
2. **Limited Iterations**: Use `--max-iterations 3` for quick tests
3. **Single Level Testing**: Use `--run-once` for specific quantization validation
4. **Result Analysis**: Regular use of `--print-last-results`

### Integration Workflow

1. **Dataset Preparation**: Ensure emotional dataset is comprehensive
2. **Tracker Initialization**: Verify training tracker database integrity
3. **Tool Configuration**: Test quantization tool connectivity
4. **Idle Management**: Configure appropriate idle checking thresholds

## Troubleshooting

### Common Issues

**Quantization Tool Not Found**
```bash
# Error: [WinError 2] The system cannot find the file specified
# Solution: Verify quantization tool installation or use --mock
ollama --version  # Check Ollama installation
```

**Database Lock Errors**
```bash
# Error: database is locked
# Solution: Close other training tracker instances
ps aux | grep emotion_training_tracker
```

**Memory Exhaustion**
```bash
# Error: Out of memory during quantization
# Solution: Reduce evaluation prompts or enable swap
python pass1_quantization_loop.py --evaluation-prompts 10
```

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python pass1_quantization_loop.py --loop --force
```

## Future Enhancements

### Planned Features

1. **Multi-Model Support**: Simultaneous quantization of multiple base models
2. **Custom Evaluation Sets**: User-defined emotional scenarios
3. **Advanced Quantization**: Support for dynamic and mixed-precision quantization
4. **Cloud Integration**: Remote model storage and evaluation
5. **Visualization Dashboard**: Real-time progress monitoring
6. **Automated Hyperparameter Tuning**: Optimal quantization parameter discovery

### Integration Opportunities

1. **CI/CD Pipelines**: Automated quantization in model deployment workflows
2. **Model Registry**: Integration with model versioning and deployment systems
3. **Monitoring Dashboards**: Real-time visualization of quantization progress
4. **Alert Systems**: Notifications for successful optimizations or failures

---

**Created for the Dolphin AI Orchestrator v2.1 Emotional Quantization System**

*Automated emotional intelligence preservation in quantized language models*
