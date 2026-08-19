Feature: 上帝模式略過規則檢查
  上帝模式可以在尚未準備回合、格子已被佔時仍放工人。

  Scenario: 尚未準備也能放
    Given 2 位玩家的農家樂修訂版
    When 完成開局設置
    And 規則檢查改為上帝模式
    And 玩家 1 放置工人到 forest
    Then 上次放置應成功
    And forest 應被玩家 1 佔領

  Scenario: 已被佔的格子上帝模式仍可放
    Given 2 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 規則檢查改為上帝模式
    And 玩家 2 放置工人到 forest
    Then 上次放置應成功
