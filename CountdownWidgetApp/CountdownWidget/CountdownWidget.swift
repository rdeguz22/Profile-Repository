import WidgetKit
import SwiftUI

struct CountdownEntry: TimelineEntry {
    let date: Date
    let event: CountdownEvent
}

struct CountdownProvider: TimelineProvider {
    func placeholder(in context: Context) -> CountdownEntry {
        CountdownEntry(date: Date(), event: .default)
    }

    func getSnapshot(in context: Context, completion: @escaping (CountdownEntry) -> Void) {
        completion(CountdownEntry(date: Date(), event: CountdownStore.load()))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<CountdownEntry>) -> Void) {
        let event = CountdownStore.load()
        let entry = CountdownEntry(date: Date(), event: event)

        // The views below use Text(_:style:) so the system animates the
        // countdown live on-device; we only need a new timeline once the
        // event has actually passed.
        let policy: TimelineReloadPolicy = event.targetDate > Date() ? .after(event.targetDate) : .never
        completion(Timeline(entries: [entry], policy: policy))
    }
}

struct CountdownWidgetEntryView: View {
    @Environment(\.widgetFamily) private var family
    var entry: CountdownProvider.Entry

    var body: some View {
        switch family {
        case .accessoryCircular:
            CircularCountdownView(entry: entry)
        case .accessoryRectangular:
            RectangularCountdownView(entry: entry)
        case .accessoryInline:
            InlineCountdownView(entry: entry)
        case .systemSmall:
            HomeScreenCountdownView(entry: entry, compact: true)
        default:
            HomeScreenCountdownView(entry: entry, compact: false)
        }
    }
}

struct CountdownWidget: Widget {
    let kind: String = "CountdownWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: CountdownProvider()) { entry in
            CountdownWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Countdown")
        .description("Shows time remaining until your event.")
        .supportedFamilies([
            .accessoryCircular,
            .accessoryRectangular,
            .accessoryInline,
            .systemSmall,
            .systemMedium,
            .systemLarge
        ])
    }
}

@main
struct CountdownWidgetBundle: WidgetBundle {
    var body: some Widget {
        CountdownWidget()
    }
}
