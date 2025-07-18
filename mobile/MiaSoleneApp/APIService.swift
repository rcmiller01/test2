import Foundation

class APIService {
    static let shared = APIService()
    let baseURL = URL(string: "https://your-backend-url.com")! // Replace with actual backend URL

    func sendMessage(_ text: String, completion: @escaping (String) -> Void) {
        let endpoint = baseURL.appendingPathComponent("/api/event/dispatch")
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ["event_type": "text", "value": text]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)

        URLSession.shared.dataTask(with: request) { data, _, _ in
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let reply = json["value"] as? String else {
                completion("...I'm here, but I couldn’t reach the backend.")
                return
            }
            completion(reply)
        }.resume()
    }
}
