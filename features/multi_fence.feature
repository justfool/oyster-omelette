Feature: 一次圍籬可連圍多格
  圍籬行動會一直圍下一塊 1 格牧場，直到木頭不夠或沒有合法空地。
  指定格子時，先圍那一格，剩下的木再自動往下圍。

  Scenario: 7 木一次圍出兩塊貼著的牧場
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 7 木
    And 玩家 1 放置工人到 fences
    Then 上次放置應成功
    And 玩家 1 的牧場數應為 2
    And 玩家 1 應有 0 木

  Scenario: 6 木指定兩格圍成一塊 2 格牧場
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 6 木
    And 玩家 1 把工人放到 fences 圍第 1 列第 2 格與第 1 列第 3 格
    Then 上次放置應成功
    And 玩家 1 應有 0 木
    And 玩家 1 的牧場數應為 1
    And 第 1 列第 2 格應在牧場裡
    And 第 1 列第 3 格應在牧場裡
    And 玩家 1 的動物容量應為 5
    And 玩家 1 的籬笆段數應為 6

  Scenario: 8 木指定四格圍成一塊 2×2 牧場
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 8 木
    And 玩家 1 把工人放到 fences 圍第 1 列第 2 格、第 1 列第 3 格、第 2 列第 2 格與第 2 列第 3 格
    Then 上次放置應成功
    And 玩家 1 應有 0 木
    And 玩家 1 的牧場數應為 1
    And 玩家 1 的動物容量應為 9
    And 玩家 1 的籬笆段數應為 8

  Scenario: 不相連的兩格不能圍成一塊
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 8 木
    And 玩家 1 把工人放到 fences 圍第 1 列第 2 格與第 1 列第 5 格
    Then 上次放置應失敗且原因包含 illegal_cell
    And 玩家 1 的牧場數應為 0

