Feature: 伐木工
  基本盒職業 A116。使用木頭累積格時額外拿 1 木。

  Scenario: 已打出伐木工後使用森林多拿 1 木
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 已打出職業 A116
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    Then 上次放置應成功
    And 玩家 1 應有 4 木
