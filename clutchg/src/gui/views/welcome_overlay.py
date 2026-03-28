"""
Welcome/Tutorial Overlay
First-time user walkthrough — Phase 3 redesign
"""

import customtkinter as ctk
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from gui.theme import COLORS, SIZES, ICON
from gui.style import font, style_primary_button, style_outline_button

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


class WelcomeOverlay(ctk.CTkToplevel):
    """Welcome overlay for first-time users"""

    # Localization strings (EN/TH)
    UI_STRINGS = {
        "en": {
            "window_title": "Welcome to ClutchG",
            # Step 1
            "step1_title": "Welcome to ClutchG!",
            "step1_content": "ClutchG optimizes your Windows PC for gaming and performance.\n\nBased on research from 28 different optimization tools, ClutchG focuses on safe, evidence-based tweaks that actually work.",
            "step1_highlight": "You're in control. All changes are reversible.",
            # Step 2
            "step2_title": "Dashboard Overview",
            "step2_content": "The dashboard shows your system's hardware and a performance score.\n\nYour score is based on real benchmark data, not marketing claims.",
            "step2_highlight": "Higher score = Better performance potential",
            # Step 3
            "step3_title": "Choose Your Profile",
            "step3_content": "ClutchG offers three optimization profiles:\n\n{safe} SAFE - For beginners, minimal risk\n{comp} COMPETITIVE - For gamers, balanced\n{ext} EXTREME - Maximum performance, advanced users only",
            "step3_highlight": "Start with SAFE if you're unsure",
            # Step 4
            "step4_title": "Automatic Backups",
            "step4_content": "Before applying any optimizations, ClutchG automatically creates:\n\n• Windows System Restore point\n• Registry backups\n• Configuration snapshots\n\nYou can always revert if something goes wrong.",
            "step4_highlight": "Safety first - never optimize without a backup",
            # Step 5
            "step5_title": "Ready to Optimize!",
            "step5_content": "You're all set!\n\n1. Go to Profiles\n2. Choose a profile\n3. Click Apply\n4. Wait for completion\n5. Restart if prompted\n\nNeed help? Click Docs in the sidebar.",
            "step5_highlight": "Enjoy your optimized PC!",
            # Buttons
            "back_btn": "Back",
            "next_btn": "Next",
            "skip_btn": "Skip",
            "get_started": "Get Started",
            # Progress
            "progress": "Step {current} of {total}",
        },
        "th": {
            "window_title": "ยินดีต้อนรับสู่ ClutchG",
            # Step 1
            "step1_title": "ยินดีต้อนรับสู่ ClutchG!",
            "step1_content": "ClutchG ช่วย Optimize  Windows PC ของคุณสำหรับเกมและประสิทธิภาพสูงสุด\n\nอิงจากการวิจัยจากเครื่องมือ Optimize 28 ตัว ClutchG ใช้การปรับแต่งที่ปลอดภัยและได้ผลจริง",
            "step1_highlight": "คุณคุมอะไรได้บ้าง การเปลี่ยนแปลงทั้งหมดสามารถย้อนกลับได้",
            # Step 2
            "step2_title": "ภาพรวม Dashboard",
            "step2_content": "Dashboard แสดงฮาร์ดแวร์และคะแนนประสิทธิภาพของระบบ\n\nคะแนนของคุณอิงจาก Benchmark จริง ไม่ใช่คำโฆษณา",
            "step2_highlight": "คะแนนสูงกว่า = ประสิทธิภาพดีกว่า",
            # Step 3
            "step3_title": "เลือก Profile ของคุณ",
            "step3_content": "ClutchG มี 3 Profile สำหรับ Optimize:\n\n{safe} SAFE - สำหรับมือใหม่ ความเสี่ยงต่ำ\n{comp} COMPETITIVE - สำหรับเกมเมอร์ สมดุล\n{ext} EXTREME - ประสิทธิภาพสูงสุด สำหรับผู้ใช้ขั้นสูง",
            "step3_highlight": "แนะนำให้เริ่มจาก SAFE หากไม่แน่ใจ",
            # Step 4
            "step4_title": "สร้าง Backup อัตโนมัติ",
            "step4_content": "ก่อน Optimize ใดๆ ClutchG จะสร้าง:\n\n• System Restore point\n• Registry backups\n• Configuration snapshots\n\nคุณสามารถย้อนกลับได้เสมอหากมีปัญหา",
            "step4_highlight": "ความปลอดภัยเป็นหลัก - อย่า Optimize โดยไม่มี Backup",
            # Step 5
            "step5_title": "พร้อม Optimize แล้ว!",
            "step5_content": "พร้อมแล้ว!\n\n1. ไปที่ Profiles\n2. เลือก Profile\n3. กด Apply\n4. รอให้เสร็จ\n5. Restart ถ้าถูกถาม\n\nต้องการความช่วยเหลือ? กด Docs ในแถบด้านข้าง",
            "step5_highlight": "เพลิดเพลินกับ PC ที่ Optimize แล้ว!",
            # Buttons
            "back_btn": "ย้อนกลับ",
            "next_btn": "ถัดไป",
            "skip_btn": "ข้าม",
            "get_started": "เริ่มใช้งาน",
            # Progress
            "progress": "ขั้นตอน {current} จาก {total}",
        },
    }

    def __init__(self, parent, app: Optional["ClutchGApp"] = None, on_close=None):
        super().__init__(parent)

        self.app = app
        self.on_close = on_close
        self.step = 0
        self.total_steps = 5

        # Get language from app or default to English
        self.language = "en"
        if app and hasattr(app, "config"):
            self.language = app.config.get("language", "en")

        # Configure window
        self.title(self._ui("window_title"))
        self.geometry("700x500")
        self.configure(fg_color=COLORS["bg_primary"])

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Build steps with localized content
        self._build_steps()

        self.setup_ui()
        self.show_step(0)

    def _ui(self, key: str, **kwargs) -> str:
        """Get UI string in current language"""
        return (
            self.UI_STRINGS.get(self.language, self.UI_STRINGS["en"])
            .get(key, key)
            .format(**kwargs)
        )

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed"""
        w = weight if weight in ("normal", "bold") else "normal"  # type: ignore[arg-type]
        if self.language == "th":
            return ctk.CTkFont(family="Figtree", size=size, weight=w)  # type: ignore[arg-type]
        return font("body", size=size, weight=w)  # type: ignore[arg-type]

    def _build_steps(self):
        """Build steps content with localized strings"""
        # Get icons for step 3
        safe_icon = ICON("safe")
        comp_icon = ICON("competitive")
        ext_icon = ICON("extreme")

        self.steps = [
            {
                "title": self._ui("step1_title"),
                "content": self._ui("step1_content"),
                "highlight": self._ui("step1_highlight"),
            },
            {
                "title": self._ui("step2_title"),
                "content": self._ui("step2_content"),
                "highlight": self._ui("step2_highlight"),
            },
            {
                "title": self._ui("step3_title"),
                "content": self._ui(
                    "step3_content", safe=safe_icon, comp=comp_icon, ext=ext_icon
                ),
                "highlight": self._ui("step3_highlight"),
            },
            {
                "title": self._ui("step4_title"),
                "content": self._ui("step4_content"),
                "highlight": self._ui("step4_highlight"),
            },
            {
                "title": self._ui("step5_title"),
                "content": self._ui("step5_content"),
                "highlight": self._ui("step5_highlight"),
            },
        ]

    def setup_ui(self):
        """Setup UI with grid layout:
        Row 0: Logo (step 0 only)
        Row 1: Header (title)
        Row 2: Content text (weight=1)
        Row 3: Highlight box
        Row 4: Dots + progress text
        Row 5: Navigation buttons (Back/Next)
        """
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Row 0: App logo (step 0 only) ---
        self._logo_image = None  # prevent GC
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "icon.png"
        if icon_path.is_file():
            try:
                from PIL import Image

                pil_img = Image.open(icon_path)
                self._logo_image = ctk.CTkImage(
                    light_image=pil_img, dark_image=pil_img, size=(64, 64)
                )
                self.logo_label = ctk.CTkLabel(self, image=self._logo_image, text="")
                self.logo_label.grid(
                    row=0, column=0, padx=40, pady=(30, 10), sticky="w"
                )
            except Exception:
                pass

        # --- Skip button (top-right, absolute position) ---
        self.skip_btn = ctk.CTkButton(
            self,
            text=self._ui("skip_btn"),
            width=100,
            fg_color="transparent",
            text_color=COLORS["text_muted"],
            hover_color=COLORS.get("bg_hover", "#333333"),
            font=self._font(11),
            command=self.close,
        )
        self.skip_btn.place(relx=1.0, x=-20, y=15, anchor="ne")

        # --- Row 1: Header ---
        self.header_label = ctk.CTkLabel(
            self,
            text="",
            font=self._font(20, "bold"),
            text_color=COLORS["text_primary"],
        )
        self.header_label.grid(row=1, column=0, sticky="w", padx=40, pady=(10, 20))

        # --- Row 2: Content ---
        self.content_label = ctk.CTkLabel(
            self,
            text="",
            font=self._font(13),
            text_color=COLORS["text_secondary"],
            wraplength=620,
            justify="left",
        )
        self.content_label.grid(row=2, column=0, sticky="nsew", padx=40)

        # --- Row 3: Highlight box ---
        self.highlight_box = ctk.CTkFrame(
            self, fg_color=COLORS["accent_dim"], corner_radius=SIZES["card_radius"]
        )
        self.highlight_box.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 20))

        self.highlight_label = ctk.CTkLabel(
            self.highlight_box,
            text="",
            font=self._font(12, "bold"),
            text_color=COLORS["accent"],
            wraplength=580,
        )
        self.highlight_label.pack(padx=20, pady=15)

        # --- Row 4: Dot indicators only (no progress text) ---
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.grid(row=4, column=0, pady=(5, 0))

        # Dots
        self.dots_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        self.dots_frame.pack(pady=(0, 4))

        self.dots = []
        for _ in range(self.total_steps):
            dot = ctk.CTkFrame(
                self.dots_frame,
                width=8,
                height=8,
                corner_radius=4,
                fg_color=COLORS["bg_tertiary"],
            )
            dot.pack(side="left", padx=3)
            dot.pack_propagate(False)
            self.dots.append(dot)

        # --- Row 5: Navigation buttons (Back / Next) ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=5, column=0, pady=(10, 30))

        self.back_btn = ctk.CTkButton(
            btn_frame,
            text=self._ui("back_btn"),
            width=100,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            command=self.prev_step,
            state="disabled",
        )
        style_outline_button(self.back_btn, small=True, color=COLORS["border"])
        self.back_btn.pack(side="left", padx=10)

        self.next_btn = ctk.CTkButton(
            btn_frame,
            text=self._ui("next_btn"),
            width=100,
            fg_color=COLORS["accent"],
            text_color="white",
            command=self.next_step,
        )
        style_primary_button(self.next_btn, small=True)
        self.next_btn.pack(side="left", padx=10)

    def show_step(self, step: int):
        """Show a specific step"""
        self.step = step
        step_data = self.steps[step]

        # Update content
        self.header_label.configure(text=step_data["title"])
        self.content_label.configure(text=step_data["content"])
        self.highlight_label.configure(text=step_data["highlight"])

        # Logo visibility — only on step 0
        if hasattr(self, "logo_label"):
            if step == 0:
                self.logo_label.grid()
            else:
                self.logo_label.grid_remove()

        # Step 5 highlight uses success (green), others use accent (sky blue)
        if step == self.total_steps - 1:
            self.highlight_box.configure(fg_color=COLORS["success_dim"])
            self.highlight_label.configure(text_color=COLORS["success"])
        else:
            self.highlight_box.configure(fg_color=COLORS["accent_dim"])
            self.highlight_label.configure(text_color=COLORS["accent"])

        # Dot indicators
        for i, dot in enumerate(self.dots):
            if i == step:
                dot.configure(fg_color=COLORS["accent"])
            elif i < step:
                dot.configure(fg_color=COLORS["text_muted"])
            else:
                dot.configure(fg_color=COLORS["bg_tertiary"])

        # Update buttons
        self.back_btn.configure(state="normal" if step > 0 else "disabled")

        if step == self.total_steps - 1:
            self.next_btn.configure(text=self._ui("get_started"))
        else:
            self.next_btn.configure(text=self._ui("next_btn"))

    def next_step(self):
        """Go to next step"""
        if self.step < self.total_steps - 1:
            self.show_step(self.step + 1)
        else:
            self.close()

    def prev_step(self):
        """Go to previous step"""
        if self.step > 0:
            self.show_step(self.step - 1)

    def close(self):
        """Close overlay"""
        self.destroy()
        if self.on_close:
            self.on_close()
