"""除錯軌跡：把按鍵、動作與結果記成幾行的環形清單，可開面板或寫進檔案。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

DEFAULT_LIMIT = 60


@dataclass
class TraceEntry:
    """一筆軌跡。tag 用英文識別字，text 給人讀。"""

    tag: str
    text: str
    at: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class TraceLog:
    """保留最近 N 筆，可渲染成文字，也可把每一筆同步附加到檔案。

    paused 為 True 時暫停記錄；面板開著不用怕新事件一直蓋掉舊的。
    """

    limit: int = DEFAULT_LIMIT
    entries: list[TraceEntry] = field(default_factory=list)
    sink_path: str | None = None
    paused: bool = False

    def add(self, tag: str, text: str) -> None:
        if self.paused:
            return
        entry = TraceEntry(tag=tag, text=text)
        self.entries.append(entry)
        if len(self.entries) > self.limit:
            del self.entries[: len(self.entries) - self.limit]
        if self.sink_path:
            self._write_sink(entry)

    def _write_sink(self, entry: TraceEntry) -> None:
        assert self.sink_path is not None
        with open(self.sink_path, "a", encoding="utf-8") as sink:
            sink.write(f"{entry.at} [{entry.tag}] {entry.text}\n")

    def set_sink(self, path: str) -> None:
        self.sink_path = path

    def render(self) -> str:
        lines = [f"{entry.at} [{entry.tag}] {entry.text}" for entry in self.entries]
        return "\n".join(lines) or "（尚無軌跡）"

    def has(self, text: str) -> bool:
        return any(text in entry.text for entry in self.entries)


def _who(value: object | None) -> str:
    """把「誰」表示成一行文字：已給字串就用字串，物件就取其類別名。"""
    if value is None:
        return "—"
    if isinstance(value, str):
        return value
    return type(value).__name__


def key_line(key: str, character: str | None, focus: object | None) -> str:
    """把一個按鍵事件壓成一行軌跡文字：鍵名、字元、當時誰有 focus。"""
    return f"key={key} char={character!r} focus={_who(focus)}"


def action_line(binding: str, namespace: object | None) -> str:
    """把 binding 觸發的 action 壓成一行：action 名與 namespace。"""
    return f"action={binding} namespace={_who(namespace)}"


__all__ = [
    "DEFAULT_LIMIT",
    "TraceEntry",
    "TraceLog",
    "action_line",
    "key_line",
]
