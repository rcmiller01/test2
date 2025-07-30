# Autopilot Bootloader System Documentation

## Overview

The Autopilot Bootloader is an autonomous launch system that monitors system usage and schedules background quantization and judging sessions during idle or scheduled times. It provides intelligent resource management and seamless integration with the emotional quantization autopilot.

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Bootloader Config  │    │  Autopilot          │    │  Dolphin Backend    │
│  bootloader_config  │────│  Bootloader         │────│  API Integration    │
│  .json              │    │  autopilot_         │    │  /api/autopilot/*   │
└─────────────────────┘    │  bootloader.py      │    └─────────────────────┘
                           └─────────────────────┘              │
                                      │                         │
                                      ▼                         ▼
                           ┌─────────────────────┐    ┌─────────────────────┐
                           │  Quantization       │    │  Frontend UI        │
                           │  Autopilot          │    │  Controls           │
                           │  quant_autopilot.py │    │  (Future)           │
                           └─────────────────────┘    └─────────────────────┘
```

## Files and Components

### 1. `autopilot_bootloader.py`
**Main bootloader application**

**Responsibilities:**
- Monitor CPU/memory usage using `psutil`
- Load schedule or trigger mode from configuration
- Launch `quant_autopilot.py` when conditions are met
- Log all decisions and actions
- Restart autopilot automatically if interrupted
- Provide comprehensive status reporting

**Key Classes:**
- `AutopilotBootloader`: Main controller class
- `SystemMetrics`: System performance data structure
- `BootloaderStatus`: Current operational status

### 2. `bootloader_config.json`
**Configuration file for bootloader behavior**

**Configuration Options:**
```json
{
  "mode": "idle",                    // "idle", "cron", "manual"
  "idle_threshold": 20.0,            // Max CPU % to qualify as idle
  "check_interval": 300,             // Seconds between checks
  "cron_schedule": "02:00",          // Schedule for cron mode
  "max_memory_percent": 70.0,        // Max memory % threshold
  "min_idle_duration_minutes": 15,   // Minimum idle time before launch
  "safety_checks": {
    "min_free_disk_gb": 20,          // Minimum disk space required
    "max_cpu_temp_celsius": 80,      // Maximum CPU temperature
    "check_ollama_available": true,   // Verify Ollama is running
    "prevent_during_work_hours": false,
    "work_hours_start": "09:00",
    "work_hours_end": "17:00"
  }
}
```

### 3. `bootloader.log`
**Append-only log file tracking all bootloader activity**

**Log Contents:**
- Timestamps for all events
- System state detection (idle/active)
- Launch decisions and rationale
- Safety check results
- Error conditions and recovery attempts

### 4. `autopilot_service.bat`
**Windows service management script**

**Available Commands:**
- `start`: Start bootloader service
- `stop`: Stop bootloader service  
- `restart`: Restart bootloader service
- `status`: Check current status
- `install`: Install as Windows scheduled task
- `uninstall`: Remove Windows scheduled task

## Usage

### Command Line Interface

**Basic Operations:**
```bash
# Check current status
python autopilot_bootloader.py --status

# Launch autopilot immediately (bypass conditions)
python autopilot_bootloader.py --launch-now

# Stop any running autopilot processes
python autopilot_bootloader.py --stop

# Run continuous monitoring (main mode)
python autopilot_bootloader.py
```

**Configuration:**
```bash
# Use custom config file
python autopilot_bootloader.py --config my_bootloader_config.json
```

### Operating Modes

#### 1. Idle Mode (Default)
- Monitors CPU and memory usage continuously
- Launches autopilot when system is idle for specified duration
- Ideal for background optimization during low activity

**Conditions:**
- CPU usage < `idle_threshold` %
- Memory usage < `max_memory_percent` %  
- Idle duration >= `min_idle_duration_minutes`
- All safety checks pass

#### 2. Cron Mode
- Launches autopilot at specific scheduled times
- Useful for predictable optimization windows
- Respects safety conditions even during scheduled time

**Configuration:**
```json
{
  "mode": "cron",
  "cron_schedule": "02:00"  // 2:00 AM daily
}
```

#### 3. Manual Mode
- No automatic launching
- Responds only to manual triggers via API or `--launch-now`
- Provides full control over when optimization runs

### Safety System

The bootloader includes comprehensive safety checks:

**Resource Checks:**
- Minimum free disk space
- CPU temperature monitoring (if available)
- Memory usage thresholds

**Service Dependencies:**
- Ollama availability verification
- Required model presence
- Configuration file validation

**Time-based Restrictions:**
- Work hours prevention (optional)
- Maximum daily launch limits
- Retry backoff for failed launches

## API Integration

### Dolphin Backend Endpoints

**Status and Control:**
```http
GET /api/autopilot/bootloader/status
POST /api/autopilot/bootloader/start
POST /api/autopilot/bootloader/stop
POST /api/autopilot/bootloader/launch-now
GET /api/autopilot/integration/status
```

**Example Status Response:**
```json
{
  "bootloader": {
    "running": true,
    "mode": "idle",
    "check_interval": 300,
    "launch_count": 2,
    "error_count": 0
  },
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 62.1,
    "disk_free_gb": 654.5,
    "idle_duration_minutes": 25.3
  },
  "autopilot": {
    "running": false,
    "process_id": null
  },
  "conditions": {
    "is_idle": true,
    "safety_ok": true,
    "cron_ready": false
  }
}
```

### Future Frontend Integration

**Planned UI Components:**
- Real-time bootloader status display
- Manual launch/stop controls
- Configuration editor
- Resource usage graphs
- Launch history and logs

## Windows Service Installation

### Method 1: Task Scheduler (Recommended)
```batch
# Run as Administrator
autopilot_service.bat install

# Start the service
schtasks /run /tn "AutopilotBootloader"

# Check service status
autopilot_service.bat status
```

### Method 2: Manual Background Process
```batch
# Start in background
autopilot_service.bat start

# Check status
autopilot_service.bat status

# Stop service
autopilot_service.bat stop
```

## Monitoring and Troubleshooting

### Log Files

**bootloader.log:**
- All bootloader decisions and actions
- System metrics at each check
- Error conditions and recovery attempts

**emotion_quant_autopilot/logs/:**
- Autopilot execution logs
- Quantization results
- Emotional evaluation data

### Common Issues

**Bootloader won't start:**
```bash
# Check configuration
python -c "import json; print(json.load(open('bootloader_config.json')))"

# Verify Python dependencies
pip install psutil requests

# Check file permissions
ls -la bootloader_config.json autopilot_bootloader.py
```

**Autopilot launch failures:**
```bash
# Test autopilot directly
python emotion_quant_autopilot/quant_autopilot.py --config emotion_quant_autopilot/autopilot_config.json integration

# Check Ollama availability
curl http://localhost:11434/api/tags

# Verify disk space
df -h
```

**High resource usage:**
```bash
# Check if multiple instances running
ps aux | grep autopilot

# Monitor system resources
python autopilot_bootloader.py --status
```

### Performance Tuning

**Optimize for Different Scenarios:**

**Development Environment:**
```json
{
  "mode": "manual",
  "safety_checks": {
    "prevent_during_work_hours": true,
    "work_hours_start": "08:00",
    "work_hours_end": "18:00"
  }
}
```

**Production Server:**
```json
{
  "mode": "idle", 
  "idle_threshold": 10.0,
  "min_idle_duration_minutes": 30,
  "check_interval": 600,
  "safety_checks": {
    "min_free_disk_gb": 100,
    "max_cpu_temp_celsius": 70
  }
}
```

**Scheduled Optimization:**
```json
{
  "mode": "cron",
  "cron_schedule": "03:00",
  "safety_checks": {
    "prevent_during_work_hours": false
  }
}
```

## Integration Testing

### Test Full Workflow
```bash
# 1. Test bootloader status
python autopilot_bootloader.py --status

# 2. Test immediate launch
python autopilot_bootloader.py --launch-now

# 3. Test API integration
curl http://localhost:8000/api/autopilot/bootloader/status

# 4. Test service management
autopilot_service.bat status
```

### Verify Integration
```bash
# Run comprehensive integration test
python simple_integration_test.py

# Check bootloader + autopilot connectivity
python autopilot_bootloader.py --status | grep "autopilot.*running.*true"
```

## Security Considerations

**File Permissions:**
- Restrict write access to config files
- Secure log file locations
- Limit service account privileges

**Network Security:**
- API authentication (future enhancement)
- Local-only Ollama access
- Secure credential storage

**Resource Protection:**
- Disk space monitoring
- Memory usage limits
- CPU temperature safeguards

## Future Enhancements

**Planned Features:**
1. **Advanced Scheduling**: Multiple cron expressions, day-of-week rules
2. **Resource Prediction**: ML-based usage pattern analysis  
3. **Distributed Operation**: Multi-node coordination
4. **Enhanced Safety**: GPU monitoring, process priority management
5. **Cloud Integration**: Remote monitoring and control
6. **Performance Analytics**: Historical optimization tracking

**API Expansions:**
1. **Real-time Metrics**: WebSocket status updates
2. **Configuration API**: Dynamic config changes
3. **Log Streaming**: Live log tail via API
4. **Health Monitoring**: Comprehensive system health checks

This bootloader system provides a robust foundation for autonomous emotional quantization with intelligent resource management and comprehensive monitoring capabilities.
