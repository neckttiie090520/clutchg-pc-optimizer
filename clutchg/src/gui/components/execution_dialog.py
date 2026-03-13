"""
Execution Output Dialog
Modal dialog for showing real-time execution progress
"""

import customtkinter as ctk
from typing import TYPE_CHECKING
import threading

from gui.theme import COLORS, SIZES
from gui.style import font, style_ghost_button

if TYPE_CHECKING:
    from core.profile_manager import Profile


class ExecutionDialog(ctk.CTkToplevel):
    """Modal dialog for showing execution progress and output"""

    def __init__(self, parent, job):
        super().__init__(parent)

        self.job = job
        self.job_title = self.resolve_job_title(job)
        self.output_lines = []
        self.is_complete = False
        self._executor = None  # set via set_executor() for cancel support
        self._tweak_ok = 0
        self._tweak_fail = 0

        # Setup window
        self.title(f"Running {self.job_title}...")
        self.geometry("600x500")
        self.configure(fg_color=COLORS["bg_primary"])

        # Make modal
        self.grab_set()
        self.focus_set()

        # Build UI
        self.setup_ui()

        # Center on parent
        self.center_window()

    def setup_ui(self):
        """Setup dialog UI"""
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header frame
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header,
            text=f"Running {self.job_title}",
            font=font("body_bold", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left", padx=20, pady=15)

        # Close button (disabled during execution)
        self.close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=30,
            height=30,
            font=font("body", size=14),
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_hover"],
            command=self.on_close,
            state="disabled"
        )
        style_ghost_button(self.close_btn, small=True)
        self.close_btn.pack(side="right", padx=(0, 15))

        # Cancel button (visible during execution)
        self.cancel_btn = ctk.CTkButton(
            header,
            text="Cancel",
            width=70,
            height=30,
            font=font("body", size=12),
            fg_color=COLORS.get("danger", "#EF4444"),
            text_color="#FFFFFF",
            hover_color=COLORS.get("danger_hover", "#DC2626"),
            command=self.on_cancel,
        )
        self.cancel_btn.pack(side="right", padx=(0, 5))

        # Progress bar frame
        progress_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        progress_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 0))
        progress_frame.grid_propagate(False)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            height=8,
            fg_color=COLORS["bg_card"],
            progress_color=COLORS["accent"]
        )
        self.progress_bar.place(relx=0.5, rely=0.5, anchor="center")
        self.progress_bar.set(0)

        # Progress label
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Preparing...",
            font=font("micro", size=10),
            text_color=COLORS["text_muted"]
        )
        self.progress_label.place(relx=0.5, rely=1.0, anchor="n")

        # Output scrollable frame
        output_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            label_text="Execution Output",
            label_font=font("micro", size=10),
            label_text_color=COLORS["text_muted"]
        )
        output_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        # Output text area
        self.output_text = ctk.CTkTextbox(
            output_frame,
            font=font("mono", size=10),
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"],
            wrap="word",
            height=350
        )
        self.output_text.pack(fill="both", expand=True)
        self.output_text.configure(state="disabled")

    def center_window(self):
        """Center dialog on parent window"""
        self.update_idletasks()

        try:
            parent_x = self.master.winfo_x()
            parent_y = self.master.winfo_y()
            parent_width = self.master.winfo_width()
            parent_height = self.master.winfo_height()

            x = parent_x + (parent_width - 600) // 2
            y = parent_y + (parent_height - 500) // 2

            self.geometry(f"600x500+{x}+{y}")
        except Exception:
            pass

    def add_output(self, line: str):
        """Add a line of output"""
        if threading.current_thread() is not threading.main_thread():
            self.after(0, lambda: self.add_output(line))
            return

        self.output_text.configure(state="normal")
        self.output_text.insert("end", line + "\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

        # Auto-scroll
        self.output_text.yview_moveto(1.0)

    def set_progress(self, percent: int):
        """Set progress percentage"""
        if threading.current_thread() is not threading.main_thread():
            self.after(0, lambda: self.set_progress(percent))
            return

        self.progress_bar.set(percent / 100)

        # Update label with tweak counts if available
        total_done = self._tweak_ok + self._tweak_fail
        if total_done > 0:
            self.progress_label.configure(text=f"{total_done} tweaks processed ({percent}%)")
        elif percent == 0:
            self.progress_label.configure(text="Preparing...")
        elif percent < 25:
            self.progress_label.configure(text="Creating backup...")
        elif percent < 75:
            self.progress_label.configure(text="Applying optimizations...")
        elif percent < 100:
            self.progress_label.configure(text="Finalizing...")
        else:
            self.progress_label.configure(text="Complete!")

    def add_tweak_status(self, name: str, success: bool):
        """Show per-tweak ✅/❌ status in the output"""
        if threading.current_thread() is not threading.main_thread():
            self.after(0, lambda: self.add_tweak_status(name, success))
            return

        if success:
            self._tweak_ok += 1
            self.add_output(f"  ✅ {name}")
        else:
            self._tweak_fail += 1
            self.add_output(f"  ❌ {name}")

    def show_result(self, result):
        """
        Show execution result and enable close button

        Args:
            result: ExecutionResult from profile application (can be None)
        """
        if threading.current_thread() is not threading.main_thread():
            self.after(0, lambda: self.show_result(result))
            return

        self.is_complete = True

        # Handle None result safely
        if result is None:
            self.add_output("")
            self.add_output("⚠️ Execution completed (no result data)")
            self.progress_label.configure(text="Done", text_color=COLORS["text_secondary"])
            self.set_progress(100)
        elif result.success:
            self.add_output("")
            self.add_output("✅ Profile applied successfully!")
            if self._tweak_ok > 0:
                self.add_output(f"   {self._tweak_ok} tweak(s) applied, {self._tweak_fail} failed")
            self.progress_label.configure(text="Complete!", text_color=COLORS["success"])
            self.progress_bar.configure(progress_color=COLORS["success"])
        else:
            self.add_output("")
            self.add_output("❌ Profile application failed!")
            if self._tweak_ok + self._tweak_fail > 0:
                self.add_output(f"   {self._tweak_ok} succeeded, {self._tweak_fail} failed")
            if result.errors:
                self.add_output(f"Errors: {result.errors}")
            self.progress_label.configure(text="Failed", text_color=COLORS["danger"])
            self.progress_bar.configure(progress_color=COLORS["danger"])

        # Enable close button, hide cancel
        self.close_btn.configure(state="normal")
        self.cancel_btn.pack_forget()

    def show_diff(self, diff):
        """Show before/after snapshot comparison in output"""
        if threading.current_thread() is not threading.main_thread():
            self.after(0, lambda: self.show_diff(diff))
            return
        
        self.add_output("")
        self.add_output("📊 Before/After Comparison:")
        for line in diff.summary_lines:
            self.add_output(f"   {line}")

    def set_executor(self, executor):
        """Set the BatchExecutor for cancel support"""
        self._executor = executor

    def on_cancel(self):
        """Handle cancel button click"""
        if self.is_complete:
            return
        self.add_output("")
        self.add_output("⛔ Cancelling...")
        self.cancel_btn.configure(state="disabled", text="Cancelling...")
        if self._executor:
            self._executor.cancel()

    def on_close(self):
        """Handle close button click"""
        if self.is_complete:
            self.destroy()

    @staticmethod
    def resolve_job_title(job) -> str:
        """
        Resolve a display title for profile/custom/action jobs.
        Supports:
        - object with display_name
        - object with name
        - plain string
        """
        if hasattr(job, "display_name"):
            return str(job.display_name)
        if hasattr(job, "name"):
            return str(job.name)
        if isinstance(job, str):
            return job
        return "Task"
