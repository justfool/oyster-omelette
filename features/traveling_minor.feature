Feature: 旅行次要
  旅行卡打出後立刻結算，然後交給左手玩家的手牌，自己面前不留。
  單人打出後移出遊戲。

  Scenario: 兩人局打出旅行卡交給下一位
    Given 2 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 的次要手牌改為 traveling_ale
    And 玩家 1 打出次要 traveling_ale
    Then 玩家 1 面前不應有次要 traveling_ale
    And 玩家 2 的次要手牌應包含 traveling_ale
    And 玩家 1 應有 3 食物

  Scenario: 單人打出旅行卡後移出遊戲
    Given 1 位單人農家樂
    When 完成開局設置
    And 玩家 1 的次要手牌改為 traveling_ale
    And 玩家 1 打出次要 traveling_ale
    Then 玩家 1 面前不應有次要 traveling_ale
    And 玩家 1 的次要手牌不應包含 traveling_ale
