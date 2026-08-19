Feature: 動物繁殖
  收成最後一步：同一種動物有 2 隻以上就生 1 隻，但要住得下。
  繁殖時不能把動物煮掉。

  Scenario: 兩隻羊住得下就生第三隻
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 圍出一塊牧場
    And 玩家 1 身上有 2 羊
    And 進行收成
    Then 玩家 1 應有 3 羊

  Scenario: 住滿就不能再生
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 身上有 1 羊
    And 進行收成
    Then 玩家 1 應有 1 羊

  Scenario: 兩隻豬住得下就生第三隻
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 圍出一塊牧場
    And 玩家 1 身上有 2 野豬
    And 進行收成
    Then 玩家 1 應有 3 野豬

  Scenario: 兩隻牛住得下就生第三隻
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 圍出一塊牧場
    And 玩家 1 身上有 2 牛
    And 進行收成
    Then 玩家 1 應有 3 牛

  Scenario: 繁殖時就算有壁爐也不能靠煮騰出空間
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 已有壁爐
    And 玩家 1 身上有 4 食物
    And 玩家 1 身上有 1 羊
    And 進行收成
    Then 玩家 1 應有 1 羊
    And 玩家 1 應有 0 食物
    And 玩家 1 應有 0 張討飯卡

