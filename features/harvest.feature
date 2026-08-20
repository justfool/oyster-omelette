Feature: 收成
  第 4、7、9、11、13、14 回合回家後要收成。
  先從每塊有作物的田收 1，再餵每位家人 2 食物。
  食物不夠時穀和菜各算 1 食物。還不夠就拿討飯卡。

  Scenario: 田上的穀會收到手上並少 1
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sow_and_or_bake
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 grain_seeds
    And 玩家 1 放置工人到 farmland
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 sow_and_or_bake
    And 玩家 1 放置工人到 day_laborer
    And 所有家人回家
    And 進行收成
    Then 第 1 列第 2 格田上應有 2 穀
    And 玩家 1 應有 1 穀物

  Scenario: 養不起家人就拿討飯卡
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 所有家人回家
    And 進行收成
    Then 玩家 1 應有 0 食物
    And 玩家 1 應有 2 張討飯卡

  Scenario: 食物夠就不用討飯
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 day_laborer
    And 玩家 1 放置工人到 fishing
    And 所有家人回家
    And 進行收成
    Then 玩家 1 應有 1 食物
    And 玩家 1 應有 0 張討飯卡

  Scenario: 食物不夠先把穀當 1 食
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 身上有 0 食物
    And 玩家 1 身上有 4 穀
    And 進行收成
    Then 玩家 1 應有 0 穀
    And 玩家 1 應有 0 張討飯卡

  Scenario: 有穀也可以不換成食、改拿討飯
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 身上有 0 食物
    And 玩家 1 身上有 4 穀
    And 玩家 1 餵食時不把穀菜動物換成食物
    And 進行收成
    Then 玩家 1 應有 4 穀
    And 玩家 1 應有 4 張討飯卡

  Scenario: 有壁爐時餵食仍把穀當 1 食、不烤成 2
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 已有壁爐
    And 玩家 1 身上有 2 食物
    And 玩家 1 身上有 2 穀
    And 進行收成
    Then 玩家 1 應有 0 食物
    And 玩家 1 應有 0 穀
    And 玩家 1 應有 0 張討飯卡

  Scenario: 沒有爐時菜當 1 食
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 身上有 0 食物
    And 玩家 1 身上有 4 菜
    And 進行收成
    Then 玩家 1 應有 0 菜
    And 玩家 1 應有 0 張討飯卡

  Scenario: 有壁爐餵食時菜當 2 食
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 已有壁爐
    And 玩家 1 身上有 2 食物
    And 玩家 1 身上有 1 菜
    And 進行收成
    Then 玩家 1 應有 0 菜
    And 玩家 1 應有 0 張討飯卡

  Scenario: 有壁爐餵食時可煮羊
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 已有壁爐
    And 玩家 1 身上有 2 食物
    And 玩家 1 身上有 1 羊
    And 進行收成
    Then 玩家 1 應有 0 羊
    And 玩家 1 應有 0 張討飯卡

  Scenario: 兩塊田同時各收 1
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sow_and_or_bake
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    And 玩家 1 身上有 2 穀
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 sow_and_or_bake
    And 玩家 1 身上有 4 食物
    And 進行收成
    Then 第 1 列第 2 格田上應有 2 穀
    And 第 1 列第 3 格田上應有 2 穀
    And 玩家 1 應有 2 穀

  Scenario: 收成回合是 4、7、9、11、13、14
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    Then 第 4 回合應是收成回合
    And 第 7 回合應是收成回合
    And 第 9 回合應是收成回合
    And 第 11 回合應是收成回合
    And 第 13 回合應是收成回合
    And 第 14 回合應是收成回合
    And 第 1 回合不應是收成回合
    And 第 5 回合不應是收成回合
