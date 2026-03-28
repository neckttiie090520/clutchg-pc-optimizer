"""
Timeline Component - Visual timeline for backups and changes
Horizontal timeline with interactive nodes
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional, Callable
from dataclasses import dataclass

from gui.theme import COLORS, SIZES, RADIUS
from gui.style import font

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


@dataclass
class TimelineNode:
    """Represents a single point on the timeline"""

    id: str
    timestamp: datetime
    title: str
    description: str
    node_type: str  # "manual", "auto", "profile_applied", "restore"
    status: str  # "success", "warning", "error"
    metadata: dict = None  # Additional data (profile name, tweaks count, etc.)


class Timeline(ctk.CTkFrame):
    """
    Horizontal timeline visualization with interactive nodes.

    Shows:
    - Backup history over time
    - Profile applications
    - Restore operations
    - Manual vs automatic backups
    """

    def __init__(
        self,
        parent,
        app: "ClutchGApp",
        on_node_click: Optional[Callable[[TimelineNode], None]] = None,
    ):
        """
        Initialize timeline.

        Args:
            parent: Parent widget
            app: ClutchGApp instance
            on_node_click: Callback when node is clicked
        """
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.on_node_click = on_node_click

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header with legend
        self.create_header()

        # Scrollable timeline area
        self.timeline_scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", orientation="horizontal"
        )
        self.timeline_scroll.grid(row=1, column=0, sticky="nsew", pady=(20, 0))

        # Container for nodes
        self.nodes_container = ctk.CTkFrame(
            self.timeline_scroll, fg_color="transparent"
        )
        self.nodes_container.pack(fill="both", expand=True)

        # Store node widgets and data
        self.node_widgets: List[tuple[ctk.CTkFrame, TimelineNode]] = []

    def create_header(self):
        """Create timeline header with legend"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(
            header,
            text="Backup Timeline",
            font=font("section", size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        # Legend
        legend_frame = ctk.CTkFrame(header, fg_color="transparent")
        legend_frame.grid(row=0, column=1, sticky="e")

        legend_items = [
            ("Manual", COLORS["accent"]),
            ("Auto", COLORS["success"]),
            ("Profile", COLORS["warning"]),
            ("Restore", COLORS["danger"]),
        ]

        for i, (label, color) in enumerate(legend_items):
            # Color dot
            dot = ctk.CTkLabel(
                legend_frame, text="●", font=font("micro", size=10), text_color=color
            )
            dot.pack(side="left", padx=(10 if i > 0 else 0, 3))

            # Label
            ctk.CTkLabel(
                legend_frame,
                text=label,
                font=font("micro", size=9),
                text_color=COLORS["text_secondary"],
            ).pack(side="left")

    def set_nodes(self, nodes: List[TimelineNode]):
        """
        Set timeline nodes and render them.

        Args:
            nodes: List of TimelineNode objects (should be sorted by timestamp)
        """
        # Clear existing nodes
        self.clear_nodes()

        # Render new nodes
        for i, node in enumerate(nodes):
            node_widget = self.create_node_widget(node, i, len(nodes))
            node_widget.pack(side="left", padx=15)
            self.node_widgets.append((node_widget, node))

    def clear_nodes(self):
        """Clear all nodes from timeline"""
        for widget, _ in self.node_widgets:
            widget.destroy()
        self.node_widgets.clear()

    def create_node_widget(
        self, node: TimelineNode, index: int, total: int
    ) -> ctk.CTkFrame:
        """
        Create a single timeline node widget.

        Args:
            node: TimelineNode data
            index: Position in sequence
            total: Total number of nodes

        Returns:
            Node widget frame
        """
        # Get node color
        node_color = self._get_node_color(node)

        # Node container
        node_frame = ctk.CTkFrame(
            self.nodes_container, fg_color="transparent", width=120
        )
        node_frame.pack_propagate(False)

        # Timeline line connector
        if index < total - 1:
            connector = ctk.CTkFrame(node_frame, height=2, fg_color=COLORS["border"])
            connector.place(x=60, y=40, relwidth=0.5, anchor="w")

        # Node circle
        circle_frame = ctk.CTkFrame(
            node_frame,
            width=32,
            height=32,
            fg_color=COLORS["bg_card"],
            corner_radius=16,
            border_width=2,
            border_color=node_color,
        )
        circle_frame.place(x=60, y=40, anchor="center")
        circle_frame.grid_propagate(False)

        # Bind click event
        if self.on_node_click:
            circle_frame.bind("<Button-1>", lambda e: self.on_node_click(node))

        # Hover effect
        def on_enter(event):
            circle_frame.configure(fg_color=COLORS["bg_hover"])

        def on_leave(event):
            circle_frame.configure(fg_color=COLORS["bg_card"])

        circle_frame.bind("<Enter>", on_enter)
        circle_frame.bind("<Leave>", on_leave)

        # Node icon
        icon = self._get_node_icon(node)
        ctk.CTkLabel(
            circle_frame, text=icon, font=font("body", size=14), text_color=node_color
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Date label
        date_str = self._format_date(node.timestamp)
        date_label = ctk.CTkLabel(
            node_frame,
            text=date_str,
            font=font("micro", size=9),
            text_color=COLORS["text_secondary"],
        )
        date_label.place(x=60, y=70, anchor="n")

        # Time label
        time_str = node.timestamp.strftime("%H:%M")
        time_label = ctk.CTkLabel(
            node_frame,
            text=time_str,
            font=font("micro", size=8),
            text_color=COLORS["text_muted"],
        )
        time_label.place(x=60, y=85, anchor="n")

        # Title (truncated)
        title_text = node.title[:15] + "..." if len(node.title) > 15 else node.title
        title_label = ctk.CTkLabel(
            node_frame,
            text=title_text,
            font=font("micro", size=9, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        title_label.place(x=60, y=5, anchor="s")

        return node_frame

    def _get_node_color(self, node: TimelineNode) -> str:
        """Get color for node based on type and status"""
        if node.status == "error":
            return COLORS["danger"]
        elif node.status == "warning":
            return COLORS["warning"]

        # Color by type
        type_colors = {
            "manual": COLORS["accent"],
            "auto": COLORS["success"],
            "profile_applied": COLORS["warning"],
            "restore": COLORS["danger"],
        }
        return type_colors.get(node.node_type, COLORS["text_muted"])

    def _get_node_icon(self, node: TimelineNode) -> str:
        """Get icon for node based on type"""
        type_icons = {
            "manual": "💾",
            "auto": "🔄",
            "profile_applied": "⚡",
            "restore": "↩️",
        }
        return type_icons.get(node.node_type, "●")

    def _format_date(self, timestamp: datetime) -> str:
        """Format date for display"""
        today = datetime.now().date()
        node_date = timestamp.date()

        if node_date == today:
            return "Today"
        elif node_date == today - timedelta(days=1):
            return "Yesterday"
        else:
            return timestamp.strftime("%b %d")

    def get_selected_node(self) -> Optional[TimelineNode]:
        """Get currently selected node (if any)"""
        # For now, return None. Could be implemented to track selection state.
        return None


class CompactTimeline(ctk.CTkFrame):
    """
    Compact vertical timeline for smaller spaces.

    Shows timeline nodes in a vertical list format.
    """

    def __init__(self, parent, app: "ClutchGApp", max_nodes: int = 5):
        """
        Initialize compact timeline.

        Args:
            parent: Parent widget
            app: ClutchGApp instance
            max_nodes: Maximum number of nodes to display
        """
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.max_nodes = max_nodes

        self.grid_columnconfigure(0, weight=1)

        # Container for nodes
        self.nodes_container = ctk.CTkFrame(self, fg_color="transparent")
        self.nodes_container.grid(row=0, column=0, sticky="nsew")

        # Store node data
        self.node_widgets: List[tuple[ctk.CTkFrame, TimelineNode]] = []

    def set_nodes(self, nodes: List[TimelineNode]):
        """
        Set timeline nodes (limited to max_nodes).

        Args:
            nodes: List of TimelineNode objects (should be sorted by timestamp, newest first)
        """
        # Clear existing
        self.clear_nodes()

        # Limit to max_nodes
        display_nodes = nodes[: self.max_nodes]

        # Create node rows
        for i, node in enumerate(display_nodes):
            row = self.create_node_row(node)
            row.pack(fill="x", pady=(0 if i == 0 else 8, 0))
            self.node_widgets.append((row, node))

    def clear_nodes(self):
        """Clear all nodes"""
        for widget, _ in self.node_widgets:
            widget.destroy()
        self.node_widgets.clear()

    def create_node_row(self, node: TimelineNode) -> ctk.CTkFrame:
        """Create a compact node row"""
        node_color = self._get_node_color(node)

        # Row frame
        row = ctk.CTkFrame(
            self.nodes_container,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["card_radius"],
            height=50,
        )
        row.pack_propagate(False)
        row.grid_columnconfigure(1, weight=1)

        # Left color strip
        strip = ctk.CTkFrame(
            row, width=4, fg_color=node_color, corner_radius=RADIUS["sm"]
        )
        strip.grid(row=0, column=0, rowspan=2, sticky="ns")

        # Icon
        icon = self._get_node_icon(node)
        ctk.CTkLabel(row, text=icon, font=font("body", size=16)).grid(
            row=0, column=1, rowspan=2, padx=(12, 8), pady=12
        )

        # Title
        ctk.CTkLabel(
            row,
            text=node.title,
            font=font("body_bold", size=11, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).grid(row=0, column=2, sticky="ew", padx=(0, 10), pady=(8, 0))

        # Timestamp
        time_str = node.timestamp.strftime("%Y-%m-%d %H:%M")
        ctk.CTkLabel(
            row,
            text=time_str,
            font=font("micro", size=9),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).grid(row=1, column=2, sticky="ew", padx=(0, 10), pady=(0, 8))

        return row

    def _get_node_color(self, node: TimelineNode) -> str:
        """Get color for node"""
        if node.status == "error":
            return COLORS["danger"]
        elif node.status == "warning":
            return COLORS["warning"]

        type_colors = {
            "manual": COLORS["accent"],
            "auto": COLORS["success"],
            "profile_applied": COLORS["warning"],
            "restore": COLORS["danger"],
        }
        return type_colors.get(node.node_type, COLORS["text_muted"])

    def _get_node_icon(self, node: TimelineNode) -> str:
        """Get icon for node"""
        type_icons = {
            "manual": "💾",
            "auto": "🔄",
            "profile_applied": "⚡",
            "restore": "↩️",
        }
        return type_icons.get(node.node_type, "●")


def create_sample_nodes() -> List[TimelineNode]:
    """Create sample timeline nodes for testing"""
    from datetime import timedelta

    now = datetime.now()

    nodes = [
        TimelineNode(
            id="1",
            timestamp=now - timedelta(days=7),
            title="Full Backup",
            description="Automatic weekly backup",
            node_type="auto",
            status="success",
            metadata={"size": "245 MB"},
        ),
        TimelineNode(
            id="2",
            timestamp=now - timedelta(days=5),
            title="SAFE Profile Applied",
            description="Applied SAFE optimization profile",
            node_type="profile_applied",
            status="success",
            metadata={"profile": "SAFE", "tweaks": 12},
        ),
        TimelineNode(
            id="3",
            timestamp=now - timedelta(days=3),
            title="Manual Backup",
            description="Created before trying EXTREME",
            node_type="manual",
            status="success",
            metadata={"size": "250 MB"},
        ),
        TimelineNode(
            id="4",
            timestamp=now - timedelta(days=2),
            title="COMPETITIVE Profile",
            description="Applied COMPETITIVE profile",
            node_type="profile_applied",
            status="success",
            metadata={"profile": "COMPETITIVE", "tweaks": 18},
        ),
        TimelineNode(
            id="5",
            timestamp=now - timedelta(hours=6),
            title="Restore to Backup",
            description="Restored to manual backup",
            node_type="restore",
            status="success",
            metadata={"restore_target": "3"},
        ),
        TimelineNode(
            id="6",
            timestamp=now - timedelta(hours=2),
            title="Auto Backup",
            description="Automatic backup before profile change",
            node_type="auto",
            status="success",
            metadata={"size": "255 MB"},
        ),
        TimelineNode(
            id="7",
            timestamp=now,
            title="SAFE Profile Applied",
            description="Applied SAFE profile again",
            node_type="profile_applied",
            status="success",
            metadata={"profile": "SAFE", "tweaks": 12},
        ),
    ]

    return nodes
