// VoiceIntegration.swift
// Swift STT + TTS Integration for iOS

import Foundation
import Speech
import AVFoundation
import Combine

// MARK: - Voice Integration Manager
class VoiceIntegration: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    @Published var isListening = false
    @Published var isSpeaking = false
    @Published var recognizedText = ""
    @Published var currentPersona = "mia"
    @Published var voiceError: String?
    @Published var voiceStatus = VoiceStatus.idle
    
    // MARK: - Private Properties
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()
    private let synthesizer = AVSpeechSynthesizer()
    
    private var cancellables = Set<AnyCancellable>()
    private let apiClient = APIClient.shared
    
    // MARK: - Voice Configuration
    private var voiceConfigs: [String: VoiceConfig] = [
        "mia": VoiceConfig(
            voice: "com.apple.ttsbundle.siri_female_en-US_compact",
            pitch: 1.1,
            rate: 0.5,
            volume: 0.8,
            personality: "warm_affectionate"
        ),
        "solene": VoiceConfig(
            voice: "com.apple.ttsbundle.siri_female_en-US_compact",
            pitch: 0.9,
            rate: 0.6,
            volume: 0.9,
            personality: "sophisticated_passionate"
        ),
        "lyra": VoiceConfig(
            voice: "com.apple.ttsbundle.siri_female_en-US_compact",
            pitch: 1.2,
            rate: 0.4,
            volume: 0.7,
            personality: "mystical_ethereal"
        ),
        "doc": VoiceConfig(
            voice: "com.apple.ttsbundle.siri_male_en-US_compact",
            pitch: 1.0,
            rate: 0.7,
            volume: 0.8,
            personality: "professional_analytical"
        )
    ]
    
    // MARK: - Initialization
    override init() {
        super.init()
        setupVoiceIntegration()
        setupBindings()
    }
    
    // MARK: - Setup Methods
    private func setupVoiceIntegration() {
        // Request speech recognition authorization
        SFSpeechRecognizer.requestAuthorization { [weak self] status in
            DispatchQueue.main.async {
                switch status {
                case .authorized:
                    self?.voiceStatus = .ready
                case .denied, .restricted, .notDetermined:
                    self?.voiceStatus = .unauthorized
                    self?.voiceError = "Speech recognition not authorized"
                @unknown default:
                    self?.voiceStatus = .error
                    self?.voiceError = "Unknown authorization status"
                }
            }
        }
        
        // Request microphone authorization
        AVAudioSession.sharedInstance().requestRecordPermission { [weak self] granted in
            DispatchQueue.main.async {
                if granted {
                    self?.setupAudioSession()
                } else {
                    self?.voiceStatus = .unauthorized
                    self?.voiceError = "Microphone access not granted"
                }
            }
        }
    }
    
    private func setupAudioSession() {
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetooth])
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            voiceStatus = .error
            voiceError = "Failed to setup audio session: \(error.localizedDescription)"
        }
    }
    
    private func setupBindings() {
        // Monitor persona changes
        $currentPersona
            .sink { [weak self] persona in
                self?.updateVoiceConfiguration(for: persona)
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Voice Configuration
    private func updateVoiceConfiguration(for persona: String) {
        guard let config = voiceConfigs[persona] else { return }
        
        // Update synthesizer voice
        if let voice = AVSpeechSynthesisVoice(identifier: config.voice) {
            synthesizer.voice = voice
        }
        
        print("[Voice Integration] Updated voice config for \(persona)")
    }
    
    // MARK: - Speech Recognition (STT)
    func startListening() {
        guard voiceStatus == .ready else {
            voiceError = "Voice system not ready"
            return
        }
        
        guard !isListening else { return }
        
        do {
            // Cancel any ongoing recognition
            recognitionTask?.cancel()
            recognitionTask = nil
            
            // Setup audio session
            try setupAudioSession()
            
            // Create recognition request
            recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
            guard let recognitionRequest = recognitionRequest else {
                voiceError = "Failed to create recognition request"
                return
            }
            
            recognitionRequest.shouldReportPartialResults = true
            
            // Start recognition task
            recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { [weak self] result, error in
                DispatchQueue.main.async {
                    if let error = error {
                        self?.handleRecognitionError(error)
                        return
                    }
                    
                    if let result = result {
                        self?.recognizedText = result.bestTranscription.formattedString
                        
                        if result.isFinal {
                            self?.handleFinalRecognition()
                        }
                    }
                }
            }
            
            // Setup audio input
            let inputNode = audioEngine.inputNode
            let recordingFormat = inputNode.outputFormat(forBus: 0)
            
            inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
                recognitionRequest.append(buffer)
            }
            
            // Start audio engine
            audioEngine.prepare()
            try audioEngine.start()
            
            isListening = true
            voiceStatus = .listening
            voiceError = nil
            
            print("[Voice Integration] Started listening")
            
        } catch {
            voiceError = "Failed to start listening: \(error.localizedDescription)"
            voiceStatus = .error
        }
    }
    
    func stopListening() {
        guard isListening else { return }
        
        // Stop audio engine
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        
        // End recognition request
        recognitionRequest?.endAudio()
        recognitionRequest = nil
        
        // Cancel recognition task
        recognitionTask?.cancel()
        recognitionTask = nil
        
        isListening = false
        voiceStatus = .ready
        
        print("[Voice Integration] Stopped listening")
    }
    
    private func handleRecognitionError(_ error: Error) {
        isListening = false
        voiceStatus = .error
        voiceError = "Recognition error: \(error.localizedDescription)"
        
        print("[Voice Integration] Recognition error: \(error)")
    }
    
    private func handleFinalRecognition() {
        guard !recognizedText.isEmpty else { return }
        
        // Send recognized text to backend
        sendRecognizedText(recognizedText)
        
        // Clear recognized text
        recognizedText = ""
    }
    
    // MARK: - Text-to-Speech (TTS)
    func speak(_ text: String, persona: String? = nil) {
        guard !text.isEmpty else { return }
        
        let targetPersona = persona ?? currentPersona
        guard let config = voiceConfigs[targetPersona] else {
            voiceError = "Unknown persona: \(targetPersona)"
            return
        }
        
        // Stop any ongoing speech
        if synthesizer.isSpeaking {
            synthesizer.stopSpeaking(at: .immediate)
        }
        
        // Create speech utterance
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(identifier: config.voice)
        utterance.pitchMultiplier = config.pitch
        utterance.rate = config.rate
        utterance.volume = config.volume
        
        // Add persona-specific speech patterns
        applyPersonaSpeechPatterns(utterance, for: targetPersona)
        
        // Start speaking
        synthesizer.delegate = self
        synthesizer.speak(utterance)
        
        isSpeaking = true
        voiceStatus = .speaking
        voiceError = nil
        
        print("[Voice Integration] Speaking: \(text)")
    }
    
    func stopSpeaking() {
        if synthesizer.isSpeaking {
            synthesizer.stopSpeaking(at: .immediate)
        }
        
        isSpeaking = false
        voiceStatus = .ready
    }
    
    private func applyPersonaSpeechPatterns(_ utterance: AVSpeechUtterance, for persona: String) {
        switch persona {
        case "mia":
            // Warm, affectionate patterns
            utterance.pitchMultiplier *= 1.1
            utterance.rate *= 0.9
            
        case "solene":
            // Sophisticated, passionate patterns
            utterance.pitchMultiplier *= 0.95
            utterance.rate *= 1.1
            
        case "lyra":
            // Mystical, ethereal patterns
            utterance.pitchMultiplier *= 1.2
            utterance.rate *= 0.8
            
        case "doc":
            // Professional, analytical patterns
            utterance.pitchMultiplier *= 1.0
            utterance.rate *= 1.2
            
        default:
            break
        }
    }
    
    // MARK: - API Integration
    private func sendRecognizedText(_ text: String) {
        let request = VoiceInputRequest(
            text: text,
            persona: currentPersona,
            timestamp: Date().timeIntervalSince1970
        )
        
        apiClient.sendVoiceInput(request) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    self?.handleVoiceResponse(response)
                case .failure(let error):
                    self?.voiceError = "API error: \(error.localizedDescription)"
                }
            }
        }
    }
    
    private func handleVoiceResponse(_ response: VoiceResponse) {
        // Speak the response if provided
        if let speechText = response.speech_text {
            speak(speechText, persona: response.persona)
        }
        
        // Update persona if changed
        if let newPersona = response.persona, newPersona != currentPersona {
            currentPersona = newPersona
        }
        
        // Handle any additional actions
        if let actions = response.actions {
            handleVoiceActions(actions)
        }
    }
    
    private func handleVoiceActions(_ actions: [VoiceAction]) {
        for action in actions {
            switch action.type {
            case "mood_change":
                // Handle mood change
                print("[Voice Integration] Mood change: \(action.parameters)")
                
            case "scene_trigger":
                // Handle scene trigger
                print("[Voice Integration] Scene trigger: \(action.parameters)")
                
            case "memory_store":
                // Handle memory storage
                print("[Voice Integration] Memory store: \(action.parameters)")
                
            default:
                print("[Voice Integration] Unknown action: \(action.type)")
            }
        }
    }
    
    // MARK: - Voice Status Management
    func checkVoiceStatus() -> VoiceStatus {
        return voiceStatus
    }
    
    func resetVoiceError() {
        voiceError = nil
        if !isListening && !isSpeaking {
            voiceStatus = .ready
        }
    }
}

// MARK: - AVSpeechSynthesizerDelegate
extension VoiceIntegration: AVSpeechSynthesizerDelegate {
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            self.isSpeaking = false
            self.voiceStatus = .ready
        }
    }
    
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            self.isSpeaking = false
            self.voiceStatus = .ready
        }
    }
    
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, willSpeakRangeOfSpeechString characterRange: NSRange, utterance: AVSpeechUtterance) {
        // Optional: Handle speech progress
    }
}

// MARK: - Supporting Types
enum VoiceStatus {
    case idle
    case ready
    case listening
    case speaking
    case unauthorized
    case error
}

struct VoiceConfig {
    let voice: String
    let pitch: Float
    let rate: Float
    let volume: Float
    let personality: String
}

struct VoiceInputRequest: Codable {
    let text: String
    let persona: String
    let timestamp: TimeInterval
}

struct VoiceResponse: Codable {
    let speech_text: String?
    let persona: String?
    let actions: [VoiceAction]?
}

struct VoiceAction: Codable {
    let type: String
    let parameters: [String: Any]
    
    enum CodingKeys: String, CodingKey {
        case type
        case parameters
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        type = try container.decode(String.self, forKey: .type)
        parameters = try container.decode([String: Any].self, forKey: .parameters)
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(type, forKey: .type)
        try container.encode(parameters, forKey: .parameters)
    }
}

// MARK: - API Client Extension
extension APIClient {
    func sendVoiceInput(_ request: VoiceInputRequest, completion: @escaping (Result<VoiceResponse, Error>) -> Void) {
        let url = baseURL.appendingPathComponent("api/voice/input")
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            completion(.failure(error))
            return
        }
        
        URLSession.shared.dataTask(with: urlRequest) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "VoiceIntegration", code: -1, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                return
            }
            
            do {
                let response = try JSONDecoder().decode(VoiceResponse.self, from: data)
                completion(.success(response))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
} 