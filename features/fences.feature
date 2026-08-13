Feature: 圍籬與牧場
  圍籬行動用木頭圍出完整牧場。這一版一次圍 1 格空地。
  第一塊 1 格牧場要 4 木；之後貼著圍，共用邊會少 1 木。
  1 格牧場可養 2 隻動物。房子裡還能當寵物養 1 隻。

  Scenario: 4 木可以圍出第一塊牧場
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 4 木
    And 玩家 1 放置工人到 fences
    Then 上次放置應成功
    And 玩家 1 應有 0 木
    And 玩家 1 的牧場數應為 1
    And 第 1 列第 2 格應在牧場裡
    And 玩家 1 的動物容量應為 3

  Scenario: 木頭不夠就不能圍
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 3 木
    And 玩家 1 放置工人到 fences
    Then 上次放置應失敗且原因包含 cannot_fence

  Scenario: 第二塊牧場貼著第一塊，只要 3 木
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 4 木
    And 玩家 1 放置工人到 fences
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 3 木
    And 玩家 1 放置工人到 fences
    Then 上次放置應成功
    And 玩家 1 的牧場數應為 2
    And 玩家 1 的動物容量應為 5
