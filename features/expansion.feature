Feature: 農場擴建可蓋房又蓋畜舍
  材料夠就先蓋 1 間房；剩下木頭還夠 2 就再蓋 1 間畜舍。
  只付得起其中一件時，行為跟以前一樣。

  Scenario: 7 木 2 蘆同一行動蓋一房一畜舍
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 7 木與 2 蘆葦
    And 玩家 1 放置工人到 farm_expansion
    Then 上次放置應成功
    And 第 1 列第 2 格應是木屋
    And 第 1 列第 3 格應有畜舍
    And 玩家 1 應有 0 木
    And 玩家 1 的房間數應為 3

  Scenario: 黏土屋後新房間付 5 黏 2 蘆
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 renovation
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土與 1 蘆葦
    And 玩家 1 放置工人到 renovation
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 5 黏土與 2 蘆葦
    And 玩家 1 放置工人到 farm_expansion
    Then 上次放置應成功
    And 第 1 列第 2 格應是黏土屋
    And 玩家 1 應有 0 黏土

  Scenario: 石頭屋後新房間付 5 石 2 蘆
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 renovation
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土與 1 蘆葦
    And 玩家 1 放置工人到 renovation
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 2 石頭與 1 蘆葦
    And 玩家 1 放置工人到 renovation
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 5 石頭與 2 蘆葦
    And 玩家 1 放置工人到 farm_expansion
    Then 上次放置應成功
    And 第 1 列第 2 格應是石頭屋
    And 玩家 1 應有 0 石頭
