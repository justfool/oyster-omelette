# 修訂後 review：昨天的修改 + 策略模式設計

- 日期：2026-08-20
- 審核者：Claude Code（`claude-opus[1m]`，Opus 5 1M context）—— 與昨天同一個模型
- 範圍：昨天 review（`2026-08-19-rules-and-bdd.md`）之後的三個修改 commit（`0ef0fd3`／`e3bac08`／`ef72fe2`）與策略模式設計文件（`52262b8`／`2476b51`）
- 對照檔案：`src/oyster_omelette/actions.py`、`pastures.py`、`board.py`、`cards.py`、`harvest.py`、`majors.py`、`AGENTS.md`、`TODO.txt`

分級沿用昨天：
- 🔴 規則錯／實測踩到 bug
- 🟠 語義／設計沒對齊
- 🟡 邊角、YAGNI 內可以延後
- 🔵 想確認

---

## 昨天三個 🔴 修改：都對

- **畜舍累乘**（`pastures.py:158-176`）：從 `any(...)` 三元改成逐間 `cap *= 2`。實測 2 格 + 2 畜舍 = 17（含房子寵物 1）。對。
- **`target_error` 圍籬折扣**（`actions.py:200,213`）：改 `fence_currency < max(0, cost - fence_discount)`，與 `_do_fence`／`_fence_block_reason` 對齊。對。
- **加格 ③／④ 互斥、`lessons_4p_cost`**（`board.py:26-34`、`cards.py:108-110`）：`EXTRA_3P` 與 `EXTRA_4P` 完全不重疊；主格 `lessons` 維持 0／1；`lessons_4p_cost(len(occupations_played))` 用全局計數（1／1／2）。對。

多格圍籬（`e3bac08`）延伸做的部分：`shape_cost`／`shape_block_reason`／`enclose_shape` 乾淨、共用邊只算一次、`_connected`＋`_is_enclosed` 檢查完整。沒 regression。

---

## A1（🔴 已實測確認）圍籬 15 段上限會蒸發木頭

### 現象

`actions.py:170-184` 的 `_do_fence` 迴圈：`next_pasture_cost` 沒查 `MAX_FENCES`，`pay_fence_cost` 先扣木，`enclose_one_pasture` 內部因 `used+cost > 15` 回 0，狀態沒動 → 迴圈條件不變 → 繼續扣木 → 直到 `fence_currency < pay` 才 break。

### 主對話實測

（`_do_fence` 直接呼叫，farm 手動撒 13 段外緣旗標）

```
used before action: 13
next pasture cost: 3
wood before: 6
wood after: 0
used after: 13
pastures found: []
```

**6 木蒸發、0 塊牧場、狀態原封不動**。行動格白花一個工人。

### 規則書依據（修訂版 2016）

- 農場最多 15 段籬笆。
- Fences 行動**必須**至少圍出一塊新牧場（不能只放籬笆不圍）。
- 從上兩條直接推論：若 15 段上限使得**任何**合法起始格都圍不出新牧場，這格行動應該不合法（`cannot_use` → `cannot_fence`）。

### 沒把握、建議合併前查

- Uwe 的官方 Q&A、BGG Agricola 論壇有沒有針對「farm 剩空間但 15 段耗盡」的特殊裁定。主對話沒法連外查。**合併前建議 Grok 或使用者到 BGG 搜 `"15 fences" limit` 對一遍。**
- 卡片交互：A088（樹籬看守）折扣、B089（馬夫）畜舍免費——折扣只影響**成本**（每段少幾木）不影響**段數**（一段還是一段的物件），所以 15 上限不受折扣影響。此判斷仍請驗證。

### 修法方向（給 Grok，不由主對話落地）

`next_pasture_cost` 讓 `MAX_FENCES` 也是回 `None` 的原因，`_fence_block_reason`／`_do_fence`／`fence_cost_at`／`target_error` 會自然對齊。

### 建議加進 `features/fences.feature` 的紅線 spec

前置條件必須可達（domain 函式一路走到，不碰 fence 旗標）：

```gherkin
Scenario: 圍籬 15 段上限使下一塊圍不成時 fences 不能用
  Given 1 位玩家的農家樂修訂版
  And 回合卡先翻 fences
  When 完成開局設置
  And 玩家 1 依序圍出 (2,0)、(2,1)、(1,1)、(0,1) 四塊 1 格牧場
  And 玩家 1 的籬笆段數應為 13
  And 準備下一回合
  And 玩家 1 身上有 6 木
  And 玩家 1 放置工人到 fences
  Then 上次放置應失敗且原因包含 cannot_fence
  And 玩家 1 應有 6 木
  And 玩家 1 的籬笆段數應為 13
  And 玩家 1 的牧場數應為 4
```

需要新增的 step：`玩家 {n} 依序圍出 (r,c)、(r,c)、...`——只是連呼幾次現成 `enclose_pasture_at`，不動旗標。

**同時鎖第二條，避免修過頭一刀切**：

```gherkin
Scenario: 只差 1 段就能圍成時仍可用
  # 段數與座標 Grok 對 domain 實算，主對話沒重算
  ...
```

第二條的路徑我沒算完段數，由實作者算實際能走到的狀態填。

---

## A9（🟡）`"resource_market"` 是 dead id

`card_effects.py:293`：

```python
if space_id not in {"resource_market", "resource_market_3p", "resource_market_4p"}:
```

`"resource_market"`（無後綴）沒有任何地方會產生——`EXTRA_3P`／`EXTRA_4P` 都是 `_3p`／`_4p`。刪掉，或註解說明保留原因。

---

## 策略模式設計（AGENTS.md:67-90）

**落地第一個實作前，先想清楚 `Picks` 的粒度**（每個入口自己 dataclass vs 一個大 Picks）。這是實作時要決定的，不是現在 doc 要寫的。留給 Grok 選第一個 tracer 時判斷。

---

## 給 Grok 的一句話

三個 🔴 修得乾淨、多格圍籬加碼漂亮、策略模式先 doc 後落地的節奏正確。

**新增一條要處理**：A1（MAX_FENCES 洩木）是主對話實測確認的 game-breaking bug。建議先寫 feature 紅線（見上）、再改 `next_pasture_cost` 讓 MAX_FENCES 也是回 None 的原因。合併 spec 前建議查一下 BGG 有沒有特殊裁定。

**順手清一行**：A9 `card_effects.py:293` 的 `"resource_market"` 字串是 dead id。

其他撤回。
