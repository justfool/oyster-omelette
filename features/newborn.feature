Feature: 新生兒收成
  本回合剛生的家人，收成餵食只吃 1 食；其他大人仍吃 2。
  新生兒這回合沒工作，收成只吃 1；下一回合起算大人。

  Scenario: 本回合生小孩後立刻收成
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 family_growth
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 5 木與 2 蘆葦
    And 玩家 1 放置工人到 farm_expansion
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 family_growth
    And 玩家 1 身上有 5 食物
    And 進行收成
    Then 玩家 1 應有 0 食物
    And 玩家 1 應有 0 張討飯卡
    And 玩家 1 的家人數應為 3

  Scenario: 沒有新生兒時 3 人家庭收成要 6 食
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 family_growth
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 5 木與 2 蘆葦
    And 玩家 1 放置工人到 farm_expansion
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 family_growth
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 5 食物
    And 進行收成
    Then 玩家 1 應有 0 食物
    And 玩家 1 應有 1 張討飯卡
    And 玩家 1 的家人數應為 3
