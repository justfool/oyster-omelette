# oyster-omelette

農家樂（修訂版）的終端機版本。

代號取自台灣小吃**蚵仔煎**的英文 *oyster omelette*，不是拼音。

## 怎麼跑

需要 [uv](https://docs.astral.sh/uv/) 與 Python 3.12。

```powershell
cd D:\work\toybox\oyster-omelette
uv sync --group dev
uv run oyster-omelette
uv run pytest
```

終端機建議用 Windows Terminal。按 `Q` 離開。

## 開發方式：BDD + TDD

新功能都走同一圈，不先寫一大坨實作。

1. **BDD**：在 `features/` 用 Gherkin 寫玩家看得到的行為（中文句子、英文關鍵字）。
2. **步驟會紅**：在 `tests/steps/` 對上 Given / When / Then。
3. **TDD**：在 `tests/unit/` 補最小單元測試（例如某一格、某一張計分表）。
4. **最少實作**：只寫剛好讓測試變綠的程式。
5. **重整**：命名與重複整理一下，不預先做下一張卡。
6. **TUI 最後動**：畫面只呼叫領域函式，規則不寫進 Textual。

關鍵字用英文 `Feature` / `Given` / `When` / `Then`，是為了讓 pytest-bdd 穩定解析；句子本身用台灣繁體中文。

```
features/                 給人讀的規格
tests/steps/              規格對應的步驟
tests/unit/               格子、計分、圍籬這類小測試
src/oyster_omelette/      遊戲規則（純 Python）
src/oyster_omelette/tui/  只有畫面
```

## 現在做到哪

- 開局、2 人版行動板、累積格、工人擺放、回家
- 耕田、播種、收成餵食、討飯卡、基本計分
- 蓋木屋、生小孩、最便宜的壁爐與烤麵包
- 圍籬、牧場、動物容量、畜舍、繁殖、翻修成黏土屋
- 10 張主要改良、石頭屋、緊急生育
- TUI 2 人熱座：P 準備、數字／字母放工人、選格（列 1-3 行 1-5）、R 回家並自動收成、S 計分、? 說明
- 官方單人（Game.setup(solo=True)）、3／4 人加格

還沒做：更複雜的「每當」卡效（林務員已做）、旅行卡轉手、次要的費用／前提。
