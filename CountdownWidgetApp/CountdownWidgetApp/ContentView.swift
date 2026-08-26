import SwiftUI
import WidgetKit

struct ContentView: View {
    @State private var event = CountdownStore.load()
    @State private var saved = false

    var body: some View {
        NavigationStack {
            Form {
                Section("Event") {
                    TextField("Event name", text: $event.name)
                    DatePicker("Target date", selection: $event.targetDate)
                }

                Section {
                    Button(saved ? "Saved" : "Save") {
                        CountdownStore.save(event)
                        WidgetCenter.shared.reloadAllTimelines()
                        saved = true
                    }
                    .disabled(event.name.trimmingCharacters(in: .whitespaces).isEmpty)
                }

                Section("Add to Lock Screen") {
                    Text("Long-press your Lock Screen, tap Customize, choose the Lock Screen, tap a widget slot, then find “Countdown” in the widget gallery. Pick the circle, the rectangle, or the single-line style depending on how much room you want it to take.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                Section("Add to Home Screen") {
                    Text("Long-press an empty area of your Home Screen, tap the + button, search for “Countdown”, and choose the small, medium, or large size.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Countdown")
            .onChange(of: event) { saved = false }
        }
    }
}

#Preview {
    ContentView()
}
