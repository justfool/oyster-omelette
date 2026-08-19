Feature: 次要改良
  開局每人 7 張次要改良。聚會所拿起始玩家時，會打出手牌第一張。
  第一張運木車打出拿 2 木。

  Scenario: 聚會所會打出運木車
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 meeting_place
    Then 上次放置應成功
    And 玩家 1 應有 2 木
    And 玩家 1 已打出 1 張次要改良

  Scenario: 大鍋菜沒有穀不能打
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 的次要手牌改為 hearty_stew
    And 玩家 1 身上有 0 穀
    Then 玩家 1 不能打出次要 hearty_stew

  Scenario: 獨木舟沒有職業不能打
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 的次要手牌改為 A078
    Then 玩家 1 不能打出次要 A078

