"""失敗原因：領域層用英文代碼，規格句子可用中文。"""

ALIASES = {
    "不是工作階段": "not_work_phase",
    "不是這位玩家的回合": "not_your_turn",
    "已經有人": "space_occupied",
    "沒有可放置的家人": "no_available_family",
    "沒有這個行動格": "unknown_space",
}


def matches(error: str, expected: str) -> bool:
    if expected in error:
        return True
    code = ALIASES.get(expected)
    return code is not None and code in error
