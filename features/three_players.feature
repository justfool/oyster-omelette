Feature: 3 人局加格
  標 ③ 的加格只出現在 3 人局，4 人局不會放這組。
  3 人：樹叢 +2 木、凹地 +1 黏、資源市場（1 蘆或 1 石以及 1 食）、上課固定 2 食。
  主格上課仍是第一張免費、之後 1 食。開局每人 7 職業 + 7 次要。

  Scenario: 3 人開局有 ③ 加格、沒有 ④ 加格
    Given 3 位玩家的農家樂修訂版
    When 完成開局設置
    Then 遊戲應有行動格 grove_3p
    And 遊戲應有行動格 hollow_3p
    And 遊戲應有行動格 resource_market_3p
    And 遊戲應有行動格 lessons_3p
    And 遊戲不應有行動格 copse_4p
    And 遊戲不應有行動格 grove_4p
    And 遊戲不應有行動格 hollow_4p
    And 遊戲不應有行動格 traveling_players
    And 玩家 1 手牌應有 7 張職業
    And 玩家 1 手牌應有 7 張次要

  Scenario: 3 人累積格補上標示數量
    Given 3 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    Then 行動格 grove_3p 應有 2 木
    And 行動格 hollow_3p 應有 1 黏土

  Scenario: 3 人加格上課固定 2 食
    Given 3 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 食物
    And 玩家 1 放置工人到 lessons_3p
    Then 上次放置應成功
    And 玩家 1 應有 0 食物
    And 玩家 1 已打出 1 張職業

  Scenario: 3 人資源市場沒指定時拿蘆葦與 1 食
    Given 3 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 resource_market_3p
    Then 上次放置應成功
    And 玩家 1 應有 1 蘆葦
    And 玩家 1 應有 3 食物
