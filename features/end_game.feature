Feature: 遊戲結束
  第 14 回合回家並完成最後一次收成後，遊戲結束並可計分。

  Scenario: 第 14 回合收成後結束
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 連續準備到第 14 回合，收成回合都收成
    Then 目前回合應為 14
    And 遊戲應已結束

  Scenario: 第 1 回合還沒結束
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    Then 遊戲應尚未結束
