Feature: 沒房間也能生
  階段 5 的緊急生育不檢查空房。
  新生兒這回合不工作，收成只吃 1 食。
  沒有空房時，一般生育格仍然不能用。

  Scenario: 兩間房兩個人也能用緊急生育
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 family_growth_without_room
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 family_growth_without_room
    Then 上次放置應成功
    And 玩家 1 的家人數應為 3
    And 玩家 1 的房間數應為 2

  Scenario: 沒有空房時一般生育仍然失敗
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 family_growth
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 family_growth
    Then 上次放置應失敗且原因包含 need_spare_room
    And 玩家 1 的家人數應為 2

  Scenario: 緊急生育的新生兒這回合不能工作
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 family_growth_without_room
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 family_growth_without_room
    And 玩家 1 放置工人到 day_laborer
    And 玩家 1 放置工人到 fishing
    Then 上次放置應失敗且原因包含 no_available_family
    And 玩家 1 的家人數應為 3
