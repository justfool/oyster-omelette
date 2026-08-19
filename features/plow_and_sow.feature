Feature: 耕且／或播
  階段 5 的 plow_and_or_sow 可以先耕一塊田，再播種。

  Scenario: 有穀時一格耕完再播
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 plow_and_or_sow
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 1 穀
    And 玩家 1 放置工人到 plow_and_or_sow
    Then 上次放置應成功
    And 第 1 列第 2 格應是田地
    And 第 1 列第 2 格田上應有 3 穀
    And 玩家 1 應有 0 穀
