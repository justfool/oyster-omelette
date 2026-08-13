Feature: 壁爐
  主要或次要改良格這一版只蓋最便宜的壁爐，要付 2 黏土。
  之後用播種且／或烤麵包時，手上的穀會烤成每顆 2 食物。

  Scenario: 付 2 黏土蓋壁爐後可以把穀烤成食物
    Given 1 位玩家的農家樂修訂版
    And 回合卡依序為 major_or_minor 與 sow_and_or_bake
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土
    And 玩家 1 放置工人到 major_or_minor
    Then 上次放置應成功
    And 玩家 1 應有 0 黏土
    And 玩家 1 應有壁爐
    When 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 1 穀
    And 玩家 1 放置工人到 sow_and_or_bake
    Then 玩家 1 應有 0 穀物
    And 玩家 1 應有 4 食物
