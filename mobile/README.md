# Mobile App Development - Mia & Solene

## 📱 Overview

This directory contains the mobile app implementation for the Mia & Solene romantic AI companion system. The mobile app provides a native interface for all the advanced features including emotional TTS, mood-driven avatar, romantic memory engine, and Phase 3 features.

## 🏗️ Project Structure

```
mobile/
├── android/                 # Android app implementation
│   └── app/
│       └── src/main/
│           ├── java/com/miasolene/app/
│           │   ├── MainActivity.kt          # Main activity
│           │   ├── api/
│           │   │   └── APIClient.kt         # API client
│           │   └── viewmodel/
│           │       └── MainViewModel.kt     # ViewModel
│           └── res/
│               ├── layout/
│               │   └── activity_main.xml    # Main layout
│               ├── values/
│               │   └── colors.xml           # Color resources
│               └── drawable/
│                   └── romantic_button_background.xml
├── ios/                    # iOS app implementation
│   ├── MiaSoleneApp.swift  # App entry point
│   ├── ContentView.swift   # Main view
│   ├── APIService.swift    # API service
│   ├── VoiceEngine.swift   # Voice processing
│   └── SpeechRecognizer.swift
├── shared/                 # Shared components
│   ├── api_client.py       # Python API client
│   └── config.py           # Configuration management
└── docs/                   # Mobile-specific documentation
```

## 🚀 Features

### ✅ Implemented Features
- **API Integration**: Complete API client for all backend features
- **Connection Testing**: Health check and system status monitoring
- **Emotional TTS**: Text-to-speech with emotion and persona selection
- **Avatar Management**: Mood updates and gesture triggering
- **Memory System**: Store and recall romantic memories
- **Haptic Feedback**: Trigger haptic patterns (Android)
- **Biometric Monitoring**: Heart rate and HRV integration
- **Romantic Theme**: Beautiful romantic UI design

### 🔄 In Progress
- **Real-time Updates**: WebSocket integration for live updates
- **Voice Recognition**: Speech-to-text for natural conversation
- **Advanced UI**: More sophisticated avatar display and animations
- **Offline Mode**: Local caching and offline functionality

### 📋 Planned Features
- **Push Notifications**: Romantic reminders and notifications
- **Background Processing**: Continuous memory analysis
- **Advanced Customization**: Avatar and voice personalization
- **Social Features**: Relationship sharing and community features

## 🛠️ Development Setup

### Android Development

#### Prerequisites
- Android Studio 4.0+
- Kotlin 1.5+
- Android SDK API 21+
- OkHttp 4.x
- Coroutines

#### Setup Instructions
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mobile/android
   ```

2. **Open in Android Studio**
   - Open Android Studio
   - Select "Open an existing Android Studio project"
   - Navigate to `mobile/android` and select it

3. **Configure API endpoint**
   - Edit `MainActivity.kt`
   - Update the `baseUrl` in `APIConfig` to point to your backend server
   - For emulator: `http://10.0.2.2:8000`
   - For device: `http://<your-server-ip>:8000`

4. **Build and run**
   ```bash
   ./gradlew build
   ./gradlew installDebug
   ```

#### Dependencies
```gradle
dependencies {
    implementation 'androidx.core:core-ktx:1.7.0'
    implementation 'androidx.appcompat:appcompat:1.4.1'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.4.1'
    implementation 'androidx.lifecycle:lifecycle-livedata-ktx:2.4.1'
    implementation 'androidx.cardview:cardview:1.0.0'
    implementation 'com.squareup.okhttp3:okhttp:4.9.3'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.0'
}
```

### iOS Development

#### Prerequisites
- Xcode 13.0+
- iOS 14.0+
- Swift 5.5+

#### Setup Instructions
1. **Open in Xcode**
   ```bash
   cd mobile/ios
   open MiaSoleneApp.xcodeproj
   ```

2. **Configure API endpoint**
   - Edit `APIService.swift`
   - Update the `baseURL` to point to your backend server

3. **Build and run**
   - Select your target device/simulator
   - Press Cmd+R to build and run

## 🔧 Configuration

### API Configuration
The mobile app uses a shared configuration system that supports multiple environments:

```python
# mobile/shared/config.py
configs = {
    'development': MobileConfig(
        api_base_url="http://localhost:8000",
        enable_analytics=True
    ),
    'staging': MobileConfig(
        api_base_url="https://staging.miasolene.com",
        enable_analytics=True
    ),
    'production': MobileConfig(
        api_base_url="https://api.miasolene.com",
        enable_analytics=False
    )
}
```

### Feature Flags
Control which features are enabled:

```python
feature_flags = {
    'haptic_feedback': True,
    'biometric_monitoring': True,
    'vr_features': True,
    'voice_synthesis': True,
    'avatar_animations': True
}
```

## 📱 UI/UX Design

### Romantic Theme
The mobile app uses a romantic color palette and design language:

- **Primary Color**: Pink (#E91E63)
- **Secondary Color**: Purple (#9C27B0)
- **Background**: Very Light Pink (#FFF5F7)
- **Text**: Dark Gray (#424242)

### Design Principles
1. **Intimacy**: Warm, inviting interface that feels personal
2. **Simplicity**: Clean, uncluttered design that focuses on the companion
3. **Responsiveness**: Smooth animations and immediate feedback
4. **Accessibility**: Support for different abilities and preferences

## 🔌 API Integration

### Core API Methods
The mobile app integrates with all backend API endpoints:

```kotlin
// Android example
apiClient.synthesizeSpeech("I love you", "mia", "love", 0.8f)
apiClient.updateAvatarMood("love", 0.8f)
apiClient.storeMemory("emotional_moment", "First I love you", "...")
apiClient.triggerHapticFeedback("heartbeat", "moderate")
```

### Error Handling
- Automatic retry logic for failed requests
- User-friendly error messages
- Graceful degradation when features are unavailable
- Offline mode support (planned)

## 🧪 Testing

### Unit Tests
```bash
# Android
./gradlew test

# iOS
xcodebuild test -scheme MiaSoleneApp -destination 'platform=iOS Simulator,name=iPhone 14'
```

### Integration Tests
```bash
# Test API integration
python mobile/shared/test_api_integration.py
```

### Manual Testing
1. **Connection Test**: Verify API connectivity
2. **TTS Test**: Test speech synthesis with different emotions
3. **Avatar Test**: Test mood updates and gestures
4. **Memory Test**: Test memory storage and recall
5. **Haptic Test**: Test haptic feedback patterns

## 📊 Performance

### Optimization Strategies
- **Image Caching**: Efficient avatar and media caching
- **API Caching**: Smart caching of API responses
- **Background Processing**: Efficient memory and analysis processing
- **Memory Management**: Proper cleanup of resources

### Monitoring
- **Performance Metrics**: Response times and error rates
- **User Analytics**: Feature usage and engagement
- **Crash Reporting**: Automatic crash detection and reporting

## 🔒 Security & Privacy

### Data Protection
- **Local Storage**: Sensitive data stored locally when possible
- **Encryption**: All API communications encrypted
- **User Consent**: Clear consent for data collection
- **Data Minimization**: Only collect necessary data

### Privacy Features
- **Offline Mode**: Function without internet connection
- **Data Deletion**: Easy data removal options
- **Anonymous Mode**: Use without personal data
- **Privacy Controls**: Granular privacy settings

## 🚀 Deployment

### Android Deployment
1. **Build Release APK**
   ```bash
   ./gradlew assembleRelease
   ```

2. **Sign APK**
   ```bash
   jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore app-release-unsigned.apk alias_name
   ```

3. **Upload to Google Play Store**

### iOS Deployment
1. **Archive App**
   - Product → Archive in Xcode

2. **Upload to App Store Connect**
   - Use Xcode Organizer to upload

## 📈 Roadmap

### Phase 1: Core Features (Complete)
- ✅ Basic API integration
- ✅ Connection testing
- ✅ Feature testing UI

### Phase 2: Enhanced UI (In Progress)
- 🔄 Beautiful avatar display
- 🔄 Advanced animations
- 🔄 Customizable themes

### Phase 3: Advanced Features (Planned)
- 📋 Real-time updates
- 📋 Voice recognition
- 📋 Advanced haptics
- 📋 Biometric integration

### Phase 4: Polish & Optimization (Planned)
- 📋 Performance optimization
- 📋 Advanced analytics
- 📋 Social features
- 📋 Offline capabilities

## 🤝 Contributing

### Development Guidelines
1. **Code Style**: Follow platform-specific conventions
2. **Testing**: Write tests for new features
3. **Documentation**: Update documentation for changes
4. **Performance**: Consider performance impact of changes

### Pull Request Process
1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit pull request
5. Code review and approval

## 📞 Support

### Getting Help
- **Documentation**: Check this README and API docs
- **Issues**: Report bugs on GitHub
- **Discussions**: Join community discussions
- **Email**: Contact development team

### Common Issues
1. **Connection Failed**: Check API server is running
2. **Build Errors**: Verify dependencies and SDK versions
3. **Performance Issues**: Check device compatibility
4. **Feature Not Working**: Verify feature flags and permissions

## 📄 License

This mobile app is part of the Mia & Solene project and follows the same license terms as the main project.

---

**Note**: This mobile app is designed to work with the Mia & Solene backend API. Make sure the backend server is running and accessible before testing the mobile app. 