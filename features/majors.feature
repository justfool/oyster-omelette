Feature: 主要改良
  主要或次要改良格會自動蓋「付得起的下一張」主要改良。
  已有壁爐時，可以用壁爐免費換成灶。
  蓋烤爐會立刻烤一次。工坊在收成換食物。井在之後幾個回合各給 1 食。

  Scenario: 有壁爐可以用它免費換成灶
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土
    And 玩家 1 放置工人到 major_or_minor
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 major_or_minor
    Then 上次放置應成功
    And 玩家 1 應有灶
    And 玩家 1 不應有壁爐牌

  Scenario: 黏土爐蓋成立刻把 1 穀烤成 5 食
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 clay_oven
    And 玩家 1 身上有 3 黏土與 1 石頭
    And 玩家 1 身上有 1 穀
    And 玩家 1 放置工人到 major_or_minor
    Then 玩家 1 應有 0 穀物
    And 玩家 1 應有 7 食物
    And 玩家 1 應有黏土爐

  Scenario: 木工坊收成時用 1 木換 2 食
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 joinery
    And 玩家 1 身上有 2 木與 2 石頭
    And 玩家 1 放置工人到 major_or_minor
    And 所有家人回家
    And 玩家 1 身上有 3 木
    And 進行收成
    Then 玩家 1 應有 2 木
    And 玩家 1 應有 0 食物

  Scenario: 井會在之後的準備回合給食物
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 well
    And 玩家 1 身上有 1 木與 3 石頭
    And 玩家 1 放置工人到 major_or_minor
    And 所有家人回家
    And 準備下一回合
    Then 玩家 1 應有 3 食物
