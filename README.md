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
uv run ruff check
uv run ruff format --check
```

終端機建議用 Windows Terminal。按 `Q` 離開。

畫面做成**桌遊板**，不是純文字清單：

- **行動板**在正中，每一格是獨立可選的 widget（有邊框）。上面是**固定區**（2 人 10 格；3／4 人加格也在這），下面是**回合卡區**（翻開的卡一張張出現，沒翻的只顯示背面，不洩漏卡名）。
- **方向鍵**在格子之間移動；選中格會粗框／反白。
- **Enter** 或 **空白鍵**放工人；佔用格會站上該玩家的工人圖示（預設 👷／👨‍🌾／👩‍🍳／👨‍🔧，主題鍵 `worker_1`…`worker_4`）。
- 滑鼠停在上方玩家區（建材／作物／動物／家人／卡片）會顯示細節。家人區的 🙋 是「還能派工」。
- **I** 或 **D** 看目前選取格的細部說明（效果、累積量、誰佔用、要不要選農場格）。
- **資源列**分成建材、作物、動物、家人、卡片；滑鼠移上去看數量說明與面前的牌。
- 農場平常在右側迷你圖；按 `M` 或需要選格的行動會展開 **3×5 大圖**，方向鍵選格、Enter 確認。
- 下方狀態列是「目前選取」＋「剛才動作」，不是一長串 log。

數字／字母快捷鍵仍可當備援。上帝模式（`G`）才看得到未翻開回合卡名稱。

沒指定時使用內建 **`default`** 主題（資源與行動格用接近的 emoji，中文名稱寫在旁邊）。完整圖示表在 `src/oyster_omelette/themes/default.json`，複製後改圖示即可。

```powershell
uv run oyster-omelette
uv run oyster-omelette --theme text
uv run oyster-omelette --theme default
$env:OYSTER_THEME = "text"
```

自訂主題可傳一份 JSON（會疊在 `default` 或指定的 `base` 上）：

```json
{ "name": "mine", "base": "default", "icons": { "wood": "W", "forest": "F" } }
```

```powershell
uv run oyster-omelette --theme D:\path\mine.json
```

遊戲內按 `T` 可在 default／文字主題之間切換。主題可改工人圖示（`worker_1`…`worker_4`）與未翻開卡（`face_down`）。

### 快捷鍵

| 按鍵 | 作用 |
| --- | --- |
| ↑↓←→ | 選行動格；選農場格時改選 3×5 大圖 |
| Enter／空白 | 放工人；選農場格時確認該格 |
| I／D | 目前選取格的細部說明 |
| P | 準備回合（翻開下一張回合卡） |
| R | 回家（收成回合會自動收成） |
| H | 收成 |
| S | 計分 |
| M | 展開／收合農場大圖 |
| G | 上帝模式 |
| Tab | 上帝模式換操作者 |
| T | 切換 default／文字主題 |
| ? | 按鍵說明 |
| Q | 離開 |
| Esc／0 | 取消選農場格 |
| 1–9、a–c… | 備援：直接對應行動格 |

耕田、圍籬、農場擴建、耕且／或播：先選行動格再自動展開農場大圖，方向鍵選格後 Enter。仍可用列 1–3、行 1–5。

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
- TUI 2 人熱座：中央行動板是可 focus 的格子（固定區＋回合卡區）、方向鍵選格、Enter 放工人、I 看說明、佔用格顯示工人圖示、資源列分組、右側農場迷你圖、M／選格展開 3×5 大圖、T 切換主題、P 準備、數字／字母備援、R 回家並自動收成、S 計分、G 上帝模式、? 按鍵
- 官方單人（Game.setup(solo=True)）、3／4 人加格

還沒做：更複雜的「每當」卡效（林務員已做）、旅行卡轉手、次要的費用／前提。
