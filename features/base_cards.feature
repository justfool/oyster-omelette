Feature: 基本盒難度 1 到 4 的卡
  正式卡掛在對照表。發牌仍是玩具卡；測試把卡放到面前。

  Scenario: 伐木工使用森林多拿 1 木
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 已打出職業 A116
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    Then 上次放置應成功
    And 玩家 1 應有 4 木

  Scenario: 穀鏟使用穀種多拿 1 穀
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 已打出次要 A067
    And 準備下一回合
    And 玩家 1 放置工人到 grain_seeds
    Then 上次放置應成功
    And 玩家 1 應有 2 穀
