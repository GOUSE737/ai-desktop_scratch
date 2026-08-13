import threading
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from core.assistant import AssistantCore
from storage.history import HistoryManager
from utils.logger import get_logger

logger = get_logger("GUIDashboard")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AssistantDashboard(ctk.CTk):
    """
    Modern desktop GUI dashboard for AI-Based Offline Desktop Assistant.
    Displays real-time assistant state machine, recognized commands, execution log, and manual controls.
    """
    def __init__(self):
        super().__init__()

        self.title("AI-Based Offline Desktop Assistant")
        self.geometry("900x650")
        self.minsize(800, 550)

        self.assistant = AssistantCore(status_callback=self.update_status_ui)
        self.history_mgr = HistoryManager()

        self._build_ui()
        self.refresh_history_log()

    def _build_ui(self):
        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=10)
        self.header_frame.pack(fill="x", padx=15, pady=10)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="JARVIS :: AI Desktop Assistant",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(side="left", padx=15, pady=10)

        # Status Badge Pill
        self.status_badge = ctk.CTkLabel(
            self.header_frame,
            text="IDLE",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#333333",
            text_color="#00FFCD",
            corner_radius=8,
            padx=12,
            pady=5
        )
        self.status_badge.pack(side="right", padx=15, pady=10)

        # 2. Main Content Frame (Split view: Left Controls, Right Log)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=5)

        # Left Column (Controls & Voice Trigger)
        self.left_frame = ctk.CTkFrame(self.main_container, width=380, corner_radius=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.input_label = ctk.CTkLabel(
            self.left_frame,
            text="Voice or Text Command:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.input_label.pack(anchor="w", padx=15, pady=(15, 5))

        self.cmd_entry = ctk.CTkEntry(
            self.left_frame,
            placeholder_text="Type command here (e.g. 'Open Chrome and search Python')...",
            font=ctk.CTkFont(size=13)
        )
        self.cmd_entry.pack(fill="x", padx=15, pady=5)
        self.cmd_entry.bind("<Return>", lambda e: self.on_execute_text_command())

        self.btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=15, pady=10)

        self.listen_btn = ctk.CTkButton(
            self.btn_frame,
            text="🎤 Listen (Voice)",
            command=self.on_trigger_voice,
            fg_color="#1f538d",
            hover_color="#14375e",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.listen_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.run_btn = ctk.CTkButton(
            self.btn_frame,
            text="Execute Text",
            command=self.on_execute_text_command,
            font=ctk.CTkFont(size=14)
        )
        self.run_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Status Detail Info Box
        self.detail_box = ctk.CTkTextbox(
            self.left_frame,
            height=120,
            font=ctk.CTkFont(size=12)
        )
        self.detail_box.pack(fill="x", padx=15, pady=10)
        self.detail_box.insert("1.0", "Assistant Ready. Click 'Listen' or type a command to start.")
        self.detail_box.configure(state="disabled")

        # Quick Action Macros
        self.quick_label = ctk.CTkLabel(self.left_frame, text="Quick Shortcuts:", font=ctk.CTkFont(size=13, weight="bold"))
        self.quick_label.pack(anchor="w", padx=15, pady=(5, 2))

        self.quick_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.quick_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(self.quick_frame, text="Open Chrome", width=100, command=lambda: self.run_quick("Open Chrome")).grid(row=0, column=0, padx=2, pady=2)
        ctk.CTkButton(self.quick_frame, text="Screenshot", width=100, command=lambda: self.run_quick("Take a screenshot")).grid(row=0, column=1, padx=2, pady=2)
        ctk.CTkButton(self.quick_frame, text="Search YouTube", width=100, command=lambda: self.run_quick("Search YouTube for Python")).grid(row=1, column=0, padx=2, pady=2)
        ctk.CTkButton(self.quick_frame, text="Lock Workstation", width=100, command=lambda: self.run_quick("Lock my computer")).grid(row=1, column=1, padx=2, pady=2)

        # Right Column (Command Execution History Log)
        self.right_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.history_title = ctk.CTkLabel(
            self.right_frame,
            text="Execution History Log",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.history_title.pack(anchor="w", padx=15, pady=(15, 5))

        self.log_textbox = ctk.CTkTextbox(
            self.right_frame,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(5, 10))

    def update_status_ui(self, state: str, detail_message: str):
        """Thread-safe UI status machine badge & detail box updater."""
        state_colors = {
            "IDLE": ("#333333", "#00FFCD"),
            "LISTENING": ("#9c6200", "#FFB703"),
            "PROCESSING": ("#1f538d", "#00B4D8"),
            "PLANNING": ("#5f27cd", "#A55EEA"),
            "EXECUTING": ("#008080", "#00FFCD"),
            "VERIFYING": ("#d35400", "#E67E22"),
            "SUCCESS": ("#1b4332", "#52B788"),
            "ERROR": ("#721c24", "#FF4D4D"),
            "CONFIRMATION_REQUIRED": ("#856404", "#FFC107")
        }
        bg_col, fg_col = state_colors.get(state, ("#333333", "#FFFFFF"))

        def _gui_update():
            self.status_badge.configure(text=state, fg_color=bg_col, text_color=fg_col)
            self.detail_box.configure(state="normal")
            self.detail_box.delete("1.0", "end")
            self.detail_box.insert("1.0", f"[{state}]\n{detail_message}")
            self.detail_box.configure(state="disabled")

        self.after(0, _gui_update)

    def on_trigger_voice(self):
        """Runs speech recognition in background thread to keep UI responsive."""
        def _bg_listen():
            res = self.assistant.listen_and_process_voice()
            self.after(0, self.refresh_history_log)

        threading.Thread(target=_bg_listen, daemon=True).start()

    def on_execute_text_command(self):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        self.cmd_entry.delete(0, "end")

        def _bg_exec():
            res = self.assistant.process_command_text(cmd)
            self.after(0, self.refresh_history_log)

        threading.Thread(target=_bg_exec, daemon=True).start()

    def run_quick(self, cmd_text: str):
        self.cmd_entry.delete(0, "end")
        self.cmd_entry.insert(0, cmd_text)
        self.on_execute_text_command()

    def refresh_history_log(self):
        records = self.history_mgr.get_recent_history(25)
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        for r in records:
            status_icon = "✓" if r["status"] == "SUCCESS" else "✗"
            line = f"[{r['timestamp']}] {status_icon} {r['raw_command']} -> [{r['intent']}] ({r['status']})\n"
            self.log_textbox.insert("end", line)
        self.log_textbox.configure(state="disabled")

if __name__ == "__main__":
    app = AssistantDashboard()
    app.mainloop()
