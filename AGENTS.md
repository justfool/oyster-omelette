# oyster-omelette 開發規則

從長 session（2026-08-13～17）整理。之後開新對話也照這份做。
產品說明與操作見 `README.md`；規則完成度見 `TODO.txt`。
牌庫：`TODO-deck-x.txt` 是索引。基本盒 96 張在 `TODO-deck-base.txt`；Artifex 120 在 `TODO-deck-a.txt`；Bubulcus 120 在 `TODO-deck-b.txt`。卡表以 `Agricola Database - Database.csv` 為準。

## 專案是什麼

- 農家樂 **2016 修訂版** 的終端機版，不是 2007 原版、不是家庭版。
- 代號 **oyster-omelette**（蚵仔煎的英文）。專案名、套件名、資料夾名**絕對不用拼音**。
- 目標：完整規則引擎；卡片可先做精簡子集，再接 Deck A／B。

## 語言與用詞

- 對使用者、註解、feature 句子、commit 說明一律用**台灣慣用繁體中文**。
- 不用中國大陸簡體或用詞（例如用「程式」不寫「代碼」、用「資訊」不寫「信息」、用「預設」不寫「默認」）。
- 領域識別字用穩定英文 id（`forest`、`day_laborer`）。畫面上的中文名寫在 `theme.SPACE_NAMES`。

## 技術棧

- Python 3.12、uv、Textual、pytest、pytest-bdd。
- 終端機建議 Windows Terminal。
- 跑測試：`uv run pytest`。跑遊戲：`uv run oyster-omelette`。

## 程式怎麼寫

為了好讀、方便學習，禁止繞路寫法。

- 狀態用 `dataclass`，不要 class 繼承樹。
- 規則用普通函式（`place_worker`、`resolve_space`）。一個函式做一件事。
- 卡片效果用「有名字的函式」對照，登錄在 `effects.py`。引擎只呼叫這些入口，**不要**在 `actions`／`harvest`／`majors` 裡寫 `if card == ...`。
- **不要** decorator、事件匯流排、metaclass、Visitor。不要用 `on_`／`emit`／`handle_`／`notify_` 當入口名。

### 卡片對照表命名

靜態表，不是訂閱。打出只記卡號；時機到了才查表。

- **問數量**（回傳 `int`、只加總）：入口 `bonus_*`，表 `BONUS_*`
  - `bonus_on_take`／`BONUS_ON_TAKE`
  - `bonus_on_bake`／`BONUS_ON_BAKE`
  - `bonus_on_score`／`BONUS_ON_SCORE`
- **做副作用**（改狀態）：入口 `after_*`，表 `AFTER_*`
  - `after_space`／`AFTER_SPACE`
  - `after_play`／`AFTER_PLAY`
  - 以後回家／回合開始：`after_return_home`、`after_round_start`
- 單張卡函式：`{卡id}_{時機}`，例如 `forester_on_take`、`A002_after_play`
- 玩家下錯的動作回 `PlaceResult(ok, error)`，不要用例外當流程控制。程式錯誤（例如負的索引）才丟例外。
- 資源維持平面整數欄位（`wood`、`clay`…），不要做 `Goods` 大抽象。
- 註解只解釋非顯而易見的規則，用台灣繁體。

## 領域與畫面分開

```
features/                 給人讀的規格
tests/steps/              規格對應的步驟
tests/unit/               格子、計分、圍籬這類小測試
src/oyster_omelette/      遊戲規則（純 Python，完全不 import Textual）
src/oyster_omelette/tui/  只有畫面：畫狀態、收按鍵、呼叫領域函式
```

- **規則不准寫進 Textual。** 步驟定義也不准重寫規則來讓測試變綠。
- TUI 只用基本元件與少量排版 CSS；不要 reactive 監聽、decorator 框架、背景 worker。
- 圖示主題放在 `theme.py`／`themes/*.json`，**不要佔用 Textual 的 `theme` 屬性**（會害啟動炸掉；用自己的欄位，例如 `look`）。

## 每一小段怎麼做（BDD + TDD）

不先寫一大坨實作。新功能都走同一圈：

1. **BDD**：`features/` 寫玩家看得到的行為。
2. **步驟會紅**：`tests/steps/` 對上 Given / When / Then。
3. **TDD**：`tests/unit/` 補最小單元測試。
4. **最少實作**：只寫剛好讓測試變綠的程式。
5. **重整**：命名與重複整理一下，不預先做下一張卡。
6. **TUI 最後動**：該段不需要顯示就別動畫面。

Gherkin 關鍵字留英文（`Feature` / `Given` / `When` / `Then`），句子用台灣繁體。玩家編號在規格裡是 1-based，領域索引是 0-based。

## 測試約束

- 單元測試檔名**不要**跟 `tests/steps/test_*.py` 撞名。步驟叫 `test_fences.py` 時，單元測試用 `test_pasture_rules.py` 這種後綴。
- 領域失敗原因用**英文代碼**（`space_occupied`）。feature 句子可用中文，走 `tests/error_text.py` 對應。
- 步驟用「錯誤字串包含」比對，不要鎖死整句文案。
- **已綠的 feature 句子不准改。** 若再派測試者，只准新增 feature／測試。
- 既有開局、工人擺放等回歸必須維持綠色。
- 回合卡正式遊戲應在階段內洗牌；測試用 `Game.setup(..., round_cards=...)` 注入，預設清單可固定。

## Git

- **每完成一小段就 commit**，不要累積整天再一次送。
- 訊息用 conventional commits，主旨可中英混用，內文用台灣繁體說明做了什麼。
- 不要 commit `__pycache__`、`.venv`。

## 若派出子代理人

由主對話串起來；子代理人**不要自己 git commit**。

| 角色 | 做什麼 | 不准做 |
| --- | --- | --- |
| 47 規劃 | 寫下一增量的目標、鎖死規則、檔案、場景、不做清單、驗收 | 改程式、改測試、commit |
| 53 碼農 | 只改 `src/oyster_omelette/`（必要時微調 TUI 顯示） | 改 `features/`、`tests/`、commit |
| 98 刁鑽測試 | 只寫 `features/` 與 `tests/`，把陷阱寫成會紅的規格 | 改 `src/`、改 TUI、改已綠 feature、commit |

主對話負責：收齊 → `uv run pytest` 全綠 → commit。

增量要小：一次一個可交付行為（例如「新生兒收成只吃 1 食」），並寫明「這一增量不做」。

## 規則與卡片的優先順序

- 先把**沒手牌也能打完 14 回合**的官方行動做對，再補 TUI 手感，最後才擴牌庫。
- 卡文優先於規則書。實作時以實體卡文為準。
- 現有玩具卡（樵夫、大鍋菜…）先留當測試樁，正式牌庫接上後再退役。
- 牌庫分檔：基本盒 `TODO-deck-base.txt`，Artifex `TODO-deck-a.txt`，Bubulcus `TODO-deck-b.txt`。先難度 1～3，再 4～5；7～8 等容量／佔格／工人重構後再做。跨庫引擎待辦寫在 `TODO-deck-x.txt`。
- 打出職業／次要要讀卡文，不要一律「打出就拿資源」。
- 選主要改良最終要讓玩家選；在那之前自動買第一張付得起的只是權宜。

## TUI 約定（已定案）

- **行動板在正中**，是可 focus 的格子（固定區 + 回合卡區），不是右側文字清單。
- 農場平常是右側迷你圖；按 `M` 或需要選格的行動才展開 3×5 大圖。
- 資源／行動格用接近的 emoji，保留 `--theme` / `OYSTER_THEME` / JSON 覆寫。沒指定就用 `themes/default.json`。
- 方向鍵選格、Enter／空白放工人、`I`／`D` 說明。數字／字母當備援。
- 上帝模式（`G`）才看得到未翻開回合卡名稱與其他隱藏資訊。

## 開工前

1. 讀 `TODO.txt`「下一件」與對應的 feature／單元測試。
2. 先紅燈再寫實作。
3. `uv run pytest` 全綠後才 commit，並把 `TODO.txt` 對應行打勾、標日期。
