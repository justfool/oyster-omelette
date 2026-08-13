Feature: 畜舍
  付不起房間但有 2 木時，農場擴建會蓋 1 間畜舍。
  沒圍籬的畜舍可多養 1 隻；蓋在牧場裡會讓那塊牧場容量加倍。

  Scenario: 2 木蓋畜舍，沒圍籬也可多養 1 隻
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 木
    And 玩家 1 放置工人到 farm_expansion
    Then 上次放置應成功
    And 第 1 列第 2 格應有畜舍
    And 玩家 1 的動物容量應為 2

  Scenario: 牧場裡的畜舍讓容量加倍
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 圍出一塊牧場
    And 準備下一回合
    And 玩家 1 身上有 2 木
    And 玩家 1 放置工人到 farm_expansion
    Then 玩家 1 的動物容量應為 5
