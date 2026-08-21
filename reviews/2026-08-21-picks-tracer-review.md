# Picks tracer 落地 review

- 日期：2026-08-21
- 審核者：Claude Code（`claude-opus[1m]`）
- 範圍：8/20 的 7 個 commit（`4d594bd` A1 修正 + `01264a2`／`bc96a63`／`7fedc23`／`e71cdd7`／`c1361e5` 策略模式落地；TUI 系列跳過）
- 對照檔：`pastures.py`、`harvest.py`、`picks.py`、`actions.py`、`game.py`、`tui/app.py`、`AGENTS.md`

---

## A1／A9 都修對

- **A1**（`pastures.py:next_pasture_cost` / `fence_cost_at`）：加 `if used()+cost > MAX_FENCES: return None`，三個入口（`_fence_block_reason`／`_do_fence`／`target_error`）靠同一個回 None 對齊。feature 兩條寫得比建議還乾淨：走 domain 函式到 used=13 擋、12+3=15 邊界仍可用。unit test 直接呼 `_do_fence` 驗木頭沒被扣。
- **A9**：`card_effects.py:293` 移掉死 id `"resource_market"`。

## 策略模式落地：跟 doc 對得起來

- `FeedPlan`／`Picks` 各自 dataclass、沒併一個大 class。
- `default_*_plan` + `apply_*` + 入口 `plan is None → default` 三件套齊。
- 驗證留領域（`picks_error`），TUI 只做 `space_options` + 傳資料。
- 一輪把 10+ 格全上，比原建議「先做 resource_market 一格」的保守方向更好。**撤回上輪的保守建議**。

## 建議修的（依優先度）

### S3 🟠 兩層預設不一致（`tui/app.py:602-608`）

TUI 只要 target 非 None 就覆蓋 `continue_expand=False`／`continue_fence=False`。這是 TUI 政策蓋掉領域政策——領域 `default_space_picks` 說「有 target 也繼續」。程式化 client（AI、replay）走 `place_worker(picks=None, target=...)` 會拿到跟 TUI 玩家不同的行為。

**改法**：這條 heuristic 搬進 `default_space_picks(player, space, target=...)`——target 非 None 時 `continue_*` 預設 False。TUI 就不用覆蓋。

### S1 🟠 方案傳遞方式不一致

`FeedPlan` 要塞 `game.feed_plans[i]` 才被 `harvest()` 讀；`Picks` 是 `place_worker(picks=...)` 參數。單一動作 vs 整批動作的差異 doc 沒寫，TUI 接餵食 UI 時「什麼時候彈選單、選完存哪」會再談一次。

**改法**：AGENTS.md 補一行「單一動作用參數傳、整批動作（收成、開局）用 game 欄位事先塞」。順便 feature 鎖 `game.harvest()` 用完清空 `feed_plans` 的行為。

## 小疙瘩（未來碰到再說）

- **S2** `default_space_picks` 對所有 space 都填 `market="reed"`，4 人版讀不到但雜訊。
- **S4** `_apply_space` 內部又呼一次 `resolve_picks`，defensive 但用不到——`_apply_space` 只有一個 caller。
- **S5** `_do_fence` 的 cells 分支忽略 `continue_fence`（現況正確），沒 feature 鎖。
- **S6** `add_resource` 呼 `note_gained_building` 但**不**呼 `bonus_on_take`，resource_market 語意上正確（不是累積格）但需要一行註解防誤解。

## 流程觀察

`7fedc23`（+891/-86，19 張卡 + 5 個新機制）**批次太大**，跟 AGENTS.md「一次一個可交付行為」不對齊。下輪可以拆小。

---

## 給 Grok 的一句話

A1 修得漂亮、策略模式一輪把 10+ 格全上跑得比保守建議好。真的要處理只有 **S3（把 target-stop 政策從 TUI 搬進領域）** 與 **S1（doc 補傳遞方式差異）**。其他都可以延後。批次大小下輪注意。
