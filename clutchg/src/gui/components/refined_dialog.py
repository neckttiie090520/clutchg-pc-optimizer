"""
RefinedDialog Component - Enhanced Confirmation Dialogs (Advanced Filters Style)
Purpose: Replace tkinter.messagebox with modern, glassmorphism dialogs
"""

import customtkinter as ctk
from gui.theme import theme_manager, SPACING, RADIUS, COLORS
from typing import Optional, Union


class RefinedDialog(ctk.CTkToplevel):
    """
    Enhanced confirmation dialog with glassmorphism and drop shadows
    - Drop shadows (simulated with border frames)
    - Rounded corners
    - Glassmorphism background
    """

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        risk_level: str = "LOW",
        **kwargs
    ):
        """
        Create a refined confirmation dialog

        Args:
            parent: Parent window
            title: Dialog title
            message: Dialog message/content
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            risk_level: Risk level for visual indicator (LOW/MEDIUM/HIGH)
        """
        super().__init__(parent, **kwargs)

        self.parent = parent
        self.result = False  # User's choice (False=cancel, True=confirm)

        colors = theme_manager.get_colors()

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Remove window decorations (optional, for cleaner look)
        # self.overrideredirect(True)  # Uncomment for borderless window

        # Set background color for shadow effect
        self.configure(fg_color=colors["bg_primary"])

        # Shadow frame (simulates drop shadow with offset border)
        shadow_offset = 4
        shadow_frame = ctk.CTkFrame(
            self,
            corner_radius=RADIUS["xl"],
            border_width=0,
            fg_color=colors["bg_tertiary"]  # Darker shadow color
        )
        shadow_frame.place(
            x=shadow_offset,
            y=shadow_offset,
            relwidth=1.0,
            relheight=1.0
        )

        # Main dialog frame (glassmorphism)
        self.dialog_frame = ctk.CTkFrame(
            self,
            corner_radius=RADIUS["xl"],
            border_width=1,
            border_color=colors.get("border_subtle", colors["border"]),
            fg_color=colors.get("bg_card", colors["bg_secondary"])
        )
        self.dialog_frame.place(relwidth=1.0, relheight=1.0)

        # Configure grid
        self.dialog_frame.grid_columnconfigure(0, weight=1)
        self.dialog_frame.grid_rowconfigure(1, weight=1)  # Message section expands

        # Title bar
        self._create_title_bar(title, risk_level)

        # Message content
        self._create_message(message)

        # Button row
        self._create_buttons(confirm_text, cancel_text, risk_level)

        # Set dialog size and center
        self.update_idletasks()
        width = 450
        height = 200 + self._get_message_lines(message) * 20  # Dynamic height based on message
        self.geometry(f"{width}x{height}")
        self._center_dialog()

        # Bind escape key to cancel
        self.bind("<Escape>", lambda e: self._on_cancel())

        # Take focus
        self.focus_set()

    def _create_title_bar(self, title: str, risk_level: str):
        """Create title bar with risk indicator"""
        colors = theme_manager.get_colors()

        title_frame = ctk.CTkFrame(self.dialog_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["md"]))
        title_frame.grid_columnconfigure(1, weight=1)

        # Risk indicator dot
        risk_colors = {
            "LOW": colors["success"],
            "MEDIUM": colors["warning"],
            "HIGH": colors["danger"]
        }
        risk_color = risk_colors.get(risk_level.upper(), colors["success"])

        risk_dot = ctk.CTkLabel(
            title_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=risk_color
        )
        risk_dot.grid(row=0, column=0, padx=(0, SPACING["sm"]))

        # Title
        title_label = ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(family="Figtree", size=16, weight="bold"),
            text_color=colors["text_primary"]
        )
        title_label.grid(row=0, column=1, sticky="w")

    def _create_message(self, message: str):
        """Create message content area"""
        colors = theme_manager.get_colors()

        message_frame = ctk.CTkFrame(self.dialog_frame, fg_color="transparent")
        message_frame.grid(row=1, column=0, sticky="nsew", padx=SPACING["lg"], pady=SPACING["md"])

        message_label = ctk.CTkLabel(
            message_frame,
            text=message,
            font=ctk.CTkFont(family="Figtree", size=13),
            text_color=colors["text_secondary"],
            wraplength=400,
            justify="left",
            anchor="nw"
        )
        message_label.pack(expand=True, fill="both")

    def _create_buttons(self, confirm_text: str, cancel_text: str, risk_level: str = "LOW"):
        """Create button row — confirm button color reflects risk_level"""
        colors = theme_manager.get_colors()

        button_frame = ctk.CTkFrame(self.dialog_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=SPACING["lg"], pady=(SPACING["md"], SPACING["lg"]))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Cancel button (only show if cancel_text is non-empty)
        if cancel_text:
            cancel_btn = ctk.CTkButton(
                button_frame,
                text=cancel_text,
                font=ctk.CTkFont(family="Figtree", size=13, weight="bold"),
                fg_color=colors.get("bg_tertiary", colors.get("bg_active", colors["bg_secondary"])),
                hover_color=colors.get("bg_hover", colors.get("bg_active", colors["bg_secondary"])),
                text_color=colors["text_secondary"],
                corner_radius=RADIUS["md"],
                height=36,
                command=self._on_cancel,
                width=150
            )
            cancel_btn.grid(row=0, column=0, padx=(0, SPACING["sm"]))

        # Confirm button color depends on risk level
        # HIGH → danger (red), MEDIUM → warning (amber), LOW → accent (teal)
        level = risk_level.upper()
        if level == "HIGH":
            btn_color = colors.get("danger", "#EF4444")
            btn_hover = colors.get("danger_hover", "#DC2626")
        elif level == "MEDIUM":
            btn_color = colors.get("warning", "#F59E0B")
            btn_hover = colors.get("warning_hover", "#D97706")
        else:
            btn_color = colors.get("accent", colors.get("success", "#10B981"))
            btn_hover = colors.get("accent_hover", colors.get("success", "#10B981"))

        confirm_btn = ctk.CTkButton(
            button_frame,
            text=confirm_text,
            font=ctk.CTkFont(family="Figtree", size=13, weight="bold"),
            fg_color=btn_color,
            hover_color=btn_hover,
            text_color=colors.get("text_on_accent", "#ffffff"),
            corner_radius=RADIUS["md"],
            height=36,
            command=self._on_confirm,
            width=150
        )
        confirm_btn.grid(row=0, column=1, padx=(SPACING["sm"], 0))

    def _get_message_lines(self, message: str) -> int:
        """Estimate number of lines in message for height calculation"""
        # Rough estimate: ~60 characters per line at wraplength 400
        return max(1, (len(message) // 60) + 1)

    def _center_dialog(self):
        """Center dialog on parent window"""
        self.update_idletasks()

        # Get parent dimensions
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()

        # Get dialog dimensions
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        # Position dialog
        self.geometry(f"+{x}+{y}")

    def _on_confirm(self):
        """Handle confirm button click"""
        self.result = True
        self.destroy()

    def _on_cancel(self):
        """Handle cancel button click"""
        self.result = False
        self.destroy()

    def show(self) -> bool:
        """
        Show dialog and wait for user response

        Returns:
            True if user confirmed, False if cancelled
        """
        self.wait_window()
        return self.result


class InputDialog(RefinedDialog):
    """
    Dialog with text input field
    """
    def __init__(self, parent, title: str, message: str, placeholder: str = "", **kwargs):
        self.input_value = None
        self.placeholder = placeholder
        super().__init__(parent, title, message, **kwargs)

    def _create_message(self, message: str):
        """Create message and input field"""
        colors = theme_manager.get_colors()

        content_frame = ctk.CTkFrame(self.dialog_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=SPACING["lg"], pady=SPACING["md"])

        # Message
        ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(family="Figtree", size=13),
            text_color=colors["text_secondary"],
            wraplength=400,
            justify="left",
            anchor="nw"
        ).pack(fill="x", pady=(0, SPACING["md"]))

        # Input field
        self.entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="",
            height=36,
            font=ctk.CTkFont(family="Figtree", size=13),
            fg_color=colors["bg_tertiary"],
            border_color=colors["border"],
            text_color=colors["text_primary"]
        )
        self.entry.pack(fill="x")
        if self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.select_range(0, "end")
        self.entry.bind("<Return>", lambda e: self._on_confirm())
        self.entry.focus_set()

    def _on_confirm(self):
        self.input_value = self.entry.get()
        self.result = True
        self.destroy()

    def show(self) -> Optional[str]:
        self.wait_window()
        return self.input_value if self.result else None


def show_confirmation(
    parent,
    title: str,
    message: str,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    risk_level: str = "LOW"
) -> bool:
    """
    Convenience function to show a confirmation dialog

    Args:
        parent: Parent window
        title: Dialog title
        message: Dialog message
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button
        risk_level: Risk level (LOW/MEDIUM/HIGH)

    Returns:
        True if user confirmed, False if cancelled
    """
    dialog = RefinedDialog(
        parent,
        title=title,
        message=message,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
        risk_level=risk_level
    )
    return dialog.show()


def show_info(
    parent,
    title: str,
    message: str
) -> bool:
    """
    Convenience function to show an info dialog (OK button only)

    Args:
        parent: Parent window
        title: Dialog title
        message: Dialog message

    Returns:
        True (always, since only OK option)
    """
    dialog = RefinedDialog(
        parent,
        title=title,
        message=message,
        confirm_text="OK",
        cancel_text="",  # Empty = no cancel button
        risk_level="LOW"
    )
    return dialog.show()


def show_input(
    parent,
    title: str,
    message: str,
    placeholder: str = ""
) -> Optional[str]:
    """
    Show an input dialog

    Args:
        parent: Parent window
        title: Dialog title
        message: Query message
        placeholder: Placeholder text

    Returns:
        Entered string or None if cancelled
    """
    dialog = InputDialog(
        parent,
        title=title,
        message=message,
        placeholder=placeholder
    )
    return dialog.show()
