Feature: 行動板與工人擺放
  2 人版開局後，準備回合會翻開階段卡並在累積格放資源。
  從起始玩家開始輪流放家人，每格每回合只能 1 人。
  回家後行動格淨空，家人回到木屋。

  Background:
    Given 2 位玩家的農家樂修訂版
    And 回合卡順序已指定為預設

  Scenario: 開局後累積格還是空的
    When 完成開局設置
    Then 森林應有 0 木

  Scenario: 第 1 回合準備後累積格放上資源
    When 完成開局設置
    And 準備下一回合
    Then 目前回合應為 1
    And 本回合翻開的卡應屬於階段 1
    And 森林應有 3 木
    And 黏土坑應有 1 黏土
    And 蘆葦岸應有 1 蘆葦
    And 漁場應有 1 食物

  Scenario: 工作階段必須從起始玩家開始
    When 完成開局設置
    And 準備下一回合
    Then 輪到玩家 1
    When 玩家 2 放置工人到 day_laborer
    Then 上次放置應失敗且原因包含 not_your_turn
    And day_laborer 應沒有人

  Scenario: 日工拿到 2 食物、穀種拿到 1 穀
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 day_laborer
    Then 上次放置應成功
    And 玩家 1 應有 4 食物
    When 玩家 2 放置工人到 grain_seeds
    Then 玩家 2 應有 1 穀物

  Scenario: 累積格拿走後歸零
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    Then 上次放置應成功
    And 玩家 1 應有 3 木
    And 森林應有 0 木

  Scenario: 連續兩回合沒人拿森林，第三回合拿走 9 木
    When 完成開局設置
    And 準備下一回合
    And 所有家人回家
    And 準備下一回合
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    Then 玩家 1 應有 9 木
    And 森林應有 0 木

  Scenario: 拿走後下一回合準備只再放一份
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 所有家人回家
    And 準備下一回合
    Then 森林應有 3 木

  Scenario: 已被佔的行動格不能再放
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 fishing
    And 玩家 2 放置工人到 fishing
    Then 上次放置應失敗且原因包含 space_occupied
    And fishing 應被玩家 1 佔領

  Scenario: 同一玩家不能把兩個家人放到同一格
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 clay_pit
    And 玩家 2 放置工人到 day_laborer
    And 玩家 1 放置工人到 clay_pit
    Then 上次放置應失敗且原因包含 space_occupied

  Scenario: 沒有剩餘家人時不能再放
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 玩家 2 放置工人到 clay_pit
    And 玩家 1 放置工人到 reed_bank
    And 玩家 2 放置工人到 fishing
    And 玩家 1 放置工人到 day_laborer
    Then 上次放置應失敗且原因包含 no_available_family

  Scenario: 非法行動格不能放
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 moon_farm
    Then 上次放置應失敗且原因包含 unknown_space

  Scenario: 回家後行動格淨空且家人回到木屋
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 玩家 2 放置工人到 clay_pit
    And 所有家人回家
    Then forest 應沒有人
    And clay_pit 應沒有人
    And 玩家 1 的家人數應為 2
    And 第 1 列第 1 格應有 1 位家人
    And 第 2 列第 1 格應有 1 位家人
    And 輪到玩家 1

  Scenario: 聚會所會把起始玩家交給放置者
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 day_laborer
    And 玩家 2 放置工人到 meeting_place
    And 所有家人回家
    Then 玩家 2 應是起始玩家
    And 輪到玩家 2
