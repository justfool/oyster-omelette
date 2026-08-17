Feature: 職業卡
  開局每人 7 張職業。上課格打出手牌第一張。
  2 人規則：第一張免費，之後要 1 食。

  Scenario: 第一張職業免費，樵夫拿到 2 木
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 lessons
    Then 上次放置應成功
    And 玩家 1 應有 2 木
    And 玩家 1 已打出 1 張職業

  Scenario: 第二張職業要付 1 食
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 lessons
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 1 食物
    And 玩家 1 放置工人到 lessons
    Then 上次放置應成功
    And 玩家 1 應有 0 食物
    And 玩家 1 已打出 2 張職業
    And 玩家 1 應有 2 黏土
