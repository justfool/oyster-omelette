Feature: 蓋房間與生小孩
  農場擴建在付得起 5 木 2 蘆、且有貼著房子的空地時，會蓋 1 間木屋。
  房間比家人多時，生育格可以生 1 個小孩。新生兒這回合不工作。

  Scenario: 有材料就能在房子旁邊蓋一間木屋
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 5 木與 2 蘆葦
    And 玩家 1 放置工人到 farm_expansion
    Then 上次放置應成功
    And 玩家 1 應有 0 木
    And 玩家 1 應有 0 蘆葦
    And 第 1 列第 2 格應是木屋
    And 玩家 1 的房間數應為 3

  Scenario: 多一間房就能生小孩
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 family_growth
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 5 木與 2 蘆葦
    And 玩家 1 放置工人到 farm_expansion
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 family_growth
    Then 上次放置應成功
    And 玩家 1 的家人數應為 3

  Scenario: 蓋房必須貼著既有房間
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 5 木與 2 蘆葦
    And 玩家 1 把工人放到 farm_expansion 的第 1 列第 1 格
    Then 上次放置應失敗且原因包含 illegal_cell
    And 第 1 列第 1 格應是木屋

  Scenario: 家人滿 5 人不能再生
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 family_growth_without_room
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 的家人數設為 5
    And 玩家 1 放置工人到 family_growth_without_room
    Then 上次放置應失敗且原因包含 family_full
