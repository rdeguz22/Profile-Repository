import SwiftUI
import WidgetKit

// Lock Screen, small circle — e.g. above the flashlight/camera row.
struct CircularCountdownView: View {
    var entry: CountdownProvider.Entry

    var body: some View {
        VStack(spacing: 2) {
            Image(systemName: "hourglass")
                .font(.system(size: 11))
            Text(entry.event.targetDate, style: .timer)
                .font(.system(size: 11, weight: .semibold, design: .rounded))
                .minimumScaleFactor(0.5)
                .lineLimit(1)
                .monospacedDigit()
        }
        .containerBackground(.clear, for: .widget)
    }
}

// Lock Screen, medium rectangle — name + live countdown + date.
struct RectangularCountdownView: View {
    var entry: CountdownProvider.Entry

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(entry.event.name)
                .font(.headline)
                .lineLimit(1)
            Text(entry.event.targetDate, style: .timer)
                .font(.system(size: 18, weight: .bold, design: .rounded))
                .monospacedDigit()
                .minimumScaleFactor(0.7)
                .lineLimit(1)
            Text(entry.event.targetDate, style: .date)
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
        .containerBackground(.clear, for: .widget)
    }
}

// Lock Screen, single line above the clock.
struct InlineCountdownView: View {
    var entry: CountdownProvider.Entry

    var body: some View {
        Text("\(entry.event.name): ") + Text(entry.event.targetDate, style: .relative)
    }
}

// Home Screen — small, medium, and large.
struct HomeScreenCountdownView: View {
    var entry: CountdownProvider.Entry
    var compact: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(entry.event.name)
                .font(compact ? .headline : .title2.bold())
                .lineLimit(2)
            Text(entry.event.targetDate, style: .timer)
                .font(.system(size: compact ? 20 : 34, weight: .bold, design: .rounded))
                .monospacedDigit()
                .minimumScaleFactor(0.5)
                .lineLimit(1)
            Text(entry.event.targetDate, style: .date)
                .font(.caption)
                .foregroundStyle(.secondary)
            Spacer(minLength: 0)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .containerBackground(for: .widget) {
            Color(red: 15.0 / 255.0, green: 23.0 / 255.0, blue: 42.0 / 255.0)
        }
        .foregroundStyle(.white)
    }
}
