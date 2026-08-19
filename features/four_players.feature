Feature: 4 人局加格
  標 ④ 的加格只出現在 4 人局，不會再放 ③ 那組。
  4 人：小樹林 +1 木、樹叢 +2 木、凹地 +2 黏、資源市場 1 蘆 1 石 1 食、
  上課前兩張職業 1 食之後 2 食、賣藝 +1 食。

  Scenario: 4 人開局有 ④ 加格、沒有 ③ 加格
    Given 4 位玩家的農家樂修訂版
    When 完成開局設置
    Then 遊戲應有行動格 copse_4p
    And 遊戲應有行動格 grove_4p
    And 遊戲應有行動格 hollow_4p
    And 遊戲應有行動格 resource_market_4p
    And 遊戲應有行動格 lessons_4p
    And 遊戲應有行動格 traveling_players
    And 遊戲不應有行動格 grove_3p
    And 遊戲不應有行動格 hollow_3p
    And 遊戲不應有行動格 lessons_3p
    And 遊戲不應有行動格 resource_market_3p

  Scenario: 4 人累積格補上標示數量
    Given 4 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    Then 行動格 copse_4p 應有 1 木
    And 行動格 grove_4p 應有 2 木
    And 行動格 hollow_4p 應有 2 黏土
    And 行動格 traveling_players 應有 1 食物

  Scenario: 4 人加格上課前兩張各 1 食，第三張 2 食
    Given 4 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 1 食物
    And 玩家 1 放置工人到 lessons_4p
    Then 上次放置應成功
    And 玩家 1 應有 0 食物
    And 玩家 1 已打出 1 張職業
    When 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 1 食物
    And 玩家 1 放置工人到 lessons_4p
    Then 上次放置應成功
    And 玩家 1 應有 0 食物
    When 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 1 食物
    And 玩家 1 放置工人到 lessons_4p
    Then 上次放置應失敗且原因包含 cannot_play_occupation
    When 玩家 1 身上有 2 食物
    And 玩家 1 放置工人到 lessons_4p
    Then 上次放置應成功
    And 玩家 1 應有 0 食物
    And 玩家 1 已打出 3 張職業

  Scenario: 4 人資源市場一次拿蘆、石、食
    Given 4 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 resource_market_4p
    Then 上次放置應成功
    And 玩家 1 應有 1 蘆葦
    And 玩家 1 應有 1 石頭
    And 玩家 1 應有 3 食物
