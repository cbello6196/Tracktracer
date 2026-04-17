import re
import webbrowser
import tkinter as tk
from tkinter import messagebox

# Estilos
ENTRY_STYLE = {
    "bg": "#3c4043",
    "fg": "#D3D3D3",
    "insertbackground": "#ECF0F1",
    "font": ("Helvetica", 12)
}

BUTTON_STYLE = {
    "bg": "#1B4F72",
    "fg": "#ECF0F1",
    "activebackground": "#ECF0F1",
    "font": ("Helvetica", 12),
    "relief": "flat",
    "highlightthickness": 0
}


class TrackTracerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrackTracer")
        self.root.geometry("825x685")
        self.root.configure(bg="#23272a")

        self.create_widgets()
        self.create_carriers_menu()

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="TrackTracer",
            fg="white",
            bg="#23272a",
            font=("Helvetica", 20)
        )
        title_label.pack(pady=(10, 0))

        subtitle_label = tk.Label(
            self.root,
            text="Bulk Tracking Validation Tool",
            fg="white",
            bg="#23272a",
            font=("Helvetica", 10)
        )
        subtitle_label.pack(pady=(0, 20))

        self.input_text = tk.Text(self.root, height=10, **ENTRY_STYLE)
        self.input_text.pack(padx=20, pady=10, fill="x")
        self.input_text.bind("<<Paste>>", self.filter_on_paste)

        self.output_text = tk.Text(self.root, height=10, **ENTRY_STYLE)
        self.output_text.pack(padx=20, pady=10, fill="x")

        buttons_frame = tk.Frame(self.root, bg="#23272a")
        buttons_frame.pack(fill="x", padx=20, pady=10)

        filter_button = tk.Button(
            buttons_frame,
            text="Filter",
            command=self.filter_tracking_numbers,
            **BUTTON_STYLE
        )
        filter_button.pack(side="left", padx=5)

        clean_button = tk.Button(
            buttons_frame,
            text="Clean",
            command=self.clear_fields,
            **BUTTON_STYLE
        )
        clean_button.pack(side="left", padx=5)

        copy_button = tk.Button(
            buttons_frame,
            text="Copy",
            command=self.copy_output,
            **BUTTON_STYLE
        )
        copy_button.pack(side="right", padx=5)

        carriers_button = tk.Button(
            buttons_frame,
            text="Carriers",
            **BUTTON_STYLE
        )
        carriers_button.pack(side="right", padx=5)
        carriers_button.bind("<Button-1>", self.show_carriers_menu)

    def create_carriers_menu(self):
        self.carriers_menu = tk.Menu(self.root, tearoff=0)

        carriers = ["17Track", "AfterShip", "DHL", "USPS"]
        for carrier in carriers:
            self.carriers_menu.add_command(
                label=carrier,
                command=lambda c=carrier: self.open_carrier(c)
            )

    def extract_tracking_numbers(self, text):
        matches = re.findall(
            r"(?<=Tracking Number: )[\w\s-]+(?=\s*Carrier)",
            text
        )
        cleaned = [re.sub(r"[-\s]", "", match) for match in matches]
        return [tracking for tracking in cleaned if tracking.strip()]

    def filter_tracking_numbers(self):
        input_value = self.input_text.get("1.0", tk.END)
        tracking_numbers = self.extract_tracking_numbers(input_value)

        self.output_text.delete("1.0", tk.END)

        duplicates = {x for x in tracking_numbers if tracking_numbers.count(x) > 1}
        duplicate_count = 0

        for tracking in tracking_numbers:
            if tracking in duplicates:
                self.output_text.insert(tk.END, tracking + "\n", "duplicate")
                duplicate_count += 1
            else:
                self.output_text.insert(tk.END, tracking + "\n")

        self.output_text.tag_configure("duplicate", foreground="red")

        if duplicate_count > 0:
            messagebox.showwarning(
                "Duplicate Trackings Detected",
                f"There are {duplicate_count} duplicated tracking entries."
            )

    def filter_on_paste(self, event):
        self.root.after(100, self.filter_tracking_numbers)

    def clear_fields(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)

    def copy_output(self):
        output_value = self.output_text.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(output_value)

    def open_carrier(self, carrier):
        output_value = self.output_text.get("1.0", tk.END).strip()
        tracking_numbers = output_value.split()

        if not tracking_numbers:
            messagebox.showinfo("No Trackings", "There are no tracking numbers to open.")
            return

        trackings = ",".join(tracking_numbers)

        urls = {
            "17Track": "https://t.17track.net/en#nums=",
            "AfterShip": "https://www.aftership.com/track?t=",
            "DHL": "https://www.dhl.com/us-en/home/tracking.html?tracking-id=",
            "USPS": "https://tools.usps.com/go/TrackConfirmAction?tRef=fullpage&tLc=11&text28777=&tLabels="
        }

        webbrowser.open(urls[carrier] + trackings)

    def show_carriers_menu(self, event):
        self.carriers_menu.post(event.x_root, event.y_root)


if __name__ == "__main__":
    root = tk.Tk()
    app = TrackTracerApp(root)
    root.mainloop()