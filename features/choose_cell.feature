Feature: 自己選農場格子
  耕田、圍籬可以指定列與行。不指定時仍自動選第一塊合法空地。
  指定不合法的格子會失敗，工人也不會放出去。

  Scenario: 指定耕在右下角
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 把工人放到 farmland 的第 3 列第 5 格
    Then 上次放置應成功
    And 第 3 列第 5 格應是田地
    And 第 1 列第 2 格應是空地

  Scenario: 不能耕在木屋上
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 把工人放到 farmland 的第 1 列第 1 格
    Then 上次放置應失敗且原因包含 illegal_cell
    And farmland 應沒有人
    And 第 1 列第 1 格應是木屋

  Scenario: 指定圍籬圍出第 3 列第 1 格
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 4 木
    And 玩家 1 把工人放到 fences 的第 3 列第 1 格
    Then 上次放置應成功
    And 第 3 列第 1 格應在牧場裡
    And 第 1 列第 2 格應是空地
