import SwiftUI

struct ContentView: View {
    @State private var inputText: String = ""
    @State private var messages: [String] = ["Mia: I'm listening, love."]

    var body: some View {
        VStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 8) {
                    ForEach(messages, id: \.self) { msg in
                        Text(msg)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(8)
                            .background(Color.gray.opacity(0.2))
                            .cornerRadius(10)
                    }
                }.padding()
            }
            HStack {
                TextField("Speak or type...", text: $inputText)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: 44)
                Button("Send") {
                    sendMessage()
                }.padding(.horizontal)
            }.padding()
        }
    }

    func sendMessage() {
        guard !inputText.isEmpty else { return }
        let userMessage = inputText
        messages.append("You: \(userMessage)")
        inputText = ""

        APIService.shared.sendMessage(userMessage) { reply in
            DispatchQueue.main.async {
                messages.append("Mia: \(reply)")
                VoiceEngine.shared.speak(reply)
            }
        }
    }
}
