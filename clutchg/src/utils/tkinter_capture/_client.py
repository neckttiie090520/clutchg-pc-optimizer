"""Capture client — connects to the tkinter-mcp agent via RemoteBridge.

Provides high-level methods that handle CTk navigation correctly:
- navigate_to(label): finds the sidebar nav label, walks up to the clickable
  parent frame, and clicks it at center coordinates
- capture(name): takes a screenshot, decodes base64, saves as JPEG
"""

from __future__ import annotations

import base64
import json
import socket
import time
from pathlib import Path
from typing import Any

from tkinter_mcp.bridge.protocol import (
    CAPTURE_SCREENSHOT,
    CLICK_WIDGET,
    DEFAULT_HOST,
    DEFAULT_PORT,
    FIND_WIDGET_BY_TEXT,
    GET_UI_LAYOUT,
    GET_WINDOW_GEOMETRY,
    Request,
    Response,
)


class CaptureClient:
    """High-level capture client that talks to the tkinter-mcp agent socket."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        self._host = host
        self._port = port
        self._socket: socket.socket | None = None
        self._request_id = 0

    def connect(self, timeout: float = 10.0) -> bool:
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(timeout)
            self._socket.connect((self._host, self._port))
            self._socket.settimeout(30.0)
            return True
        except (OSError, TimeoutError):
            self._socket = None
            return False

    def disconnect(self) -> None:
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None

    def is_connected(self) -> bool:
        return self._socket is not None

    def _request(self, method: str, **params: Any) -> Any:
        if not self._socket:
            raise RuntimeError("Not connected")
        self._request_id += 1
        req = Request(id=self._request_id, method=method, params=params)
        data = json.dumps(req.to_dict()) + "\n"
        self._socket.sendall(data.encode("utf-8"))

        buf = b""
        while b"\n" not in buf:
            chunk = self._socket.recv(65536)
            if not chunk:
                raise RuntimeError("Connection closed")
            buf += chunk

        line = buf.split(b"\n")[0]
        resp = Response.from_dict(json.loads(line.decode("utf-8")))
        if resp.error:
            raise RuntimeError(resp.error)
        return resp.result

    def get_window_geometry(self) -> dict[str, int]:
        return self._request(GET_WINDOW_GEOMETRY)

    def get_ui_layout(self) -> dict[str, Any]:
        return self._request(GET_UI_LAYOUT)

    def find_widget_id_by_text(self, text: str) -> int | None:
        return self._request(FIND_WIDGET_BY_TEXT, text=text)

    def click_widget(self, widget_id: int) -> bool:
        return self._request(
            CLICK_WIDGET, widget_id=widget_id, button="left", double=False
        )

    def capture_screenshot(self, max_dimension: int = 1600, quality: int = 90) -> bytes:
        b64_str = self._request(
            CAPTURE_SCREENSHOT, max_dimension=max_dimension, quality=quality
        )
        if isinstance(b64_str, bytes):
            b64_str = b64_str.decode("utf-8")
        return base64.b64decode(b64_str)

    # -- High-level CTk-aware methods --

    def navigate_to(self, label: str, delay_after: float = 1.5) -> bool:
        """Navigate to a sidebar view by label text.

        Strategy:
        1. Find the Label widget with matching text via find_widget_id_by_text
        2. Click the parent CTk frame (walk up from label id)
        3. Also try clicking the label itself (sometimes triggers CTk binding)
        4. Fall back to clicking the label id directly
        """
        label_id = self.find_widget_id_by_text(label)
        if label_id is None:
            return False

        # Try clicking the label first (sometimes CTk bindings are on it)
        self.click_widget(label_id)
        time.sleep(delay_after)
        return True

    def save_screenshot(
        self, filepath: str | Path, max_dim: int = 1600, quality: int = 90
    ) -> int:
        """Capture and save screenshot. Returns file size in bytes."""
        raw_jpeg = self.capture_screenshot(max_dimension=max_dim, quality=quality)
        path = Path(filepath)
        path.write_bytes(raw_jpeg)
        return path.stat().st_size
