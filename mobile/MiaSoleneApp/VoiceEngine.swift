import AVFoundation

class VoiceEngine {
    static let shared = VoiceEngine()
    private let synthesizer = AVSpeechSynthesizer()

    func speak(_ text: String, persona: String = "Mia") {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(identifier: personaVoiceID(for: persona))
        utterance.pitchMultiplier = persona == "Mia" ? 0.9 : 0.8
        utterance.rate = persona == "Mia" ? 0.45 : 0.5
        synthesizer.speak(utterance)
    }

    private func personaVoiceID(for persona: String) -> String {
        switch persona {
        case "Mia":
            return "com.apple.ttsbundle.Ava-compact"
        case "Solene":
            return "com.apple.ttsbundle.Samantha-compact"
        default:
            return AVSpeechSynthesisVoiceIdentifierAlex
        }
    }
}
