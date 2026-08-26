import Foundation

struct CountdownEvent: Codable, Equatable {
    var name: String
    var targetDate: Date

    static let `default` = CountdownEvent(
        name: "HYROX Boston",
        targetDate: Calendar.current.date(from: DateComponents(year: 2026, month: 11, day: 8, hour: 8))
            ?? Date().addingTimeInterval(60 * 60 * 24 * 30)
    )
}

enum CountdownStore {
    static let appGroupID = "group.com.rdeguzman.countdownwidget"
    private static let key = "countdownEvent"

    private static var defaults: UserDefaults? {
        UserDefaults(suiteName: appGroupID)
    }

    static func load() -> CountdownEvent {
        guard let defaults, let data = defaults.data(forKey: key) else {
            return .default
        }
        return (try? JSONDecoder().decode(CountdownEvent.self, from: data)) ?? .default
    }

    static func save(_ event: CountdownEvent) {
        guard let data = try? JSONEncoder().encode(event) else { return }
        defaults?.set(data, forKey: key)
    }
}
