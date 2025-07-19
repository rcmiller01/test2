# Scripts Directory

This directory contains organized scripts for different aspects of the Mia & Solene project.

## 📁 Directory Structure

```
scripts/
├── llm_engines/          # LLM engine startup scripts
│   ├── run_mythomax.sh   # MythoMax LLM engine
│   ├── run_openchat.sh   # OpenChat LLM engine
│   ├── run_qwen2_chat.sh # Qwen2 Chat LLM engine
│   └── run_kimik2.sh     # KimiK2 LLM engine
├── deployment/           # Deployment and infrastructure scripts
├── testing/              # Test scripts and test runners
│   ├── test_phase1.py    # Phase 1 feature tests
│   ├── test_phase2.py    # Phase 2 feature tests
│   └── test_phase3.py    # Phase 3 feature tests
└── development/          # Development and setup scripts
    └── start_phase1.py   # Phase 1 development startup
```

## 🚀 Usage

### LLM Engines
Start different LLM engines for the system:

```bash
# Start MythoMax (Mia persona)
cd scripts/llm_engines
./run_mythomax.sh

# Start OpenChat (Solene persona)
./run_openchat.sh

# Start Qwen2 Chat (Lyra persona)
./run_qwen2_chat.sh

# Start KimiK2 (Doc persona)
./run_kimik2.sh
```

### Testing
Run tests for different phases:

```bash
# Test Phase 1 features
cd scripts/testing
python test_phase1.py

# Test Phase 2 features
python test_phase2.py

# Test Phase 3 features
python test_phase3.py
```

### Development
Start development environment:

```bash
# Start Phase 1 development
cd scripts/development
python start_phase1.py
```

## 🔧 Script Details

### LLM Engine Scripts
- **run_mythomax.sh**: Starts MythoMax model for Mia's empathetic responses
- **run_openchat.sh**: Starts OpenChat model for Solene's assertive personality
- **run_qwen2_chat.sh**: Starts Qwen2 Chat for Lyra's poetic responses
- **run_kimik2.sh**: Starts KimiK2 for Doc's factual and reflective responses

### Test Scripts
- **test_phase1.py**: Tests core romantic features and emotion recognition
- **test_phase2.py**: Tests intimacy features, NSFW generation, and activities
- **test_phase3.py**: Tests advanced companionship features (haptic, biometric, VR, AI)

### Development Scripts
- **start_phase1.py**: Initializes Phase 1 development environment and dependencies

## 📋 Adding New Scripts

When adding new scripts, place them in the appropriate directory:

1. **LLM Engines**: New model startup scripts
2. **Deployment**: Infrastructure, Docker, and deployment scripts
3. **Testing**: Test runners and validation scripts
4. **Development**: Setup, configuration, and development tools

## 🎯 Next Steps

### Planned Scripts
- **deployment/docker_build.sh**: Automated Docker image building
- **deployment/deploy_production.sh**: Production deployment automation
- **testing/integration_tests.py**: Full system integration tests
- **development/setup_environment.sh**: Complete environment setup

### Script Improvements
- Add error handling and logging
- Implement configuration management
- Add script documentation
- Create script testing framework 