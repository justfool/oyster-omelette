Feature: 一次可蓋多間房
  農場擴建會一直蓋房間，直到材料不夠或沒有合法空地，剩下的木再蓋畜舍。

  Scenario: 10 木 4 蘆一次蓋兩間木屋
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 10 木與 4 蘆葦
    And 玩家 1 放置工人到 farm_expansion
    Then 上次放置應成功
    And 玩家 1 的房間數應為 4
    And 玩家 1 應有 0 木
    And 玩家 1 應有 0 蘆葦
