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

  Scenario: 井最多連續給 5 回合食物
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 well
    And 玩家 1 身上有 1 木與 3 石頭
    And 玩家 1 放置工人到 major_or_minor
    And 所有家人回家
    And 準備下一回合
    And 所有家人回家
    And 準備下一回合
    And 所有家人回家
    And 準備下一回合
    And 所有家人回家
    And 準備下一回合
    And 所有家人回家
    And 準備下一回合
    Then 玩家 1 應有 7 食物
    When 所有家人回家
    And 準備下一回合
    Then 玩家 1 應有 7 食物

  Scenario: 只剩 3 黏土壁爐也能蓋
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 fireplace_3
    And 玩家 1 身上有 3 黏土
    And 玩家 1 放置工人到 major_or_minor
    Then 玩家 1 應持有主要改良 fireplace_3

  Scenario: 只剩 4 黏土灶也能蓋
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 hearth_4
    And 玩家 1 身上有 4 黏土
    And 玩家 1 放置工人到 major_or_minor
    Then 玩家 1 應有灶
    And 玩家 1 應持有主要改良 hearth_4

  Scenario: 只剩 5 黏土灶也能蓋
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 hearth_5
    And 玩家 1 身上有 5 黏土
    And 玩家 1 放置工人到 major_or_minor
    Then 玩家 1 應持有主要改良 hearth_5

  Scenario: 石頭爐蓋成立刻把 1 穀烤成 4 食
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 stone_oven
    And 玩家 1 身上有 3 黏土與 1 石頭
    And 玩家 1 身上有 1 穀
    And 玩家 1 放置工人到 major_or_minor
    Then 玩家 1 應有 0 穀物
    And 玩家 1 應持有主要改良 stone_oven

  Scenario: 陶藝坊收成時用 1 黏換 2 食
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 pottery
    And 玩家 1 身上有 2 黏土與 2 石頭
    And 玩家 1 放置工人到 major_or_minor
    And 所有家人回家
    And 玩家 1 身上有 3 黏土
    And 進行收成
    Then 玩家 1 應有 2 黏土

  Scenario: 籃匠工坊收成時用 1 蘆換 3 食
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 公共供應只剩下 basketmaker
    And 玩家 1 身上有 2 石頭與 2 蘆葦
    And 玩家 1 放置工人到 major_or_minor
    And 所有家人回家
    And 玩家 1 身上有 2 蘆葦
    And 進行收成
    Then 玩家 1 應有 1 蘆葦

  Scenario: 有壁爐也可以免費換成剩下的 5 黏土灶
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土
    And 玩家 1 放置工人到 major_or_minor
    And 所有家人回家
    And 準備下一回合
    And 公共供應只剩下 hearth_5
    And 玩家 1 放置工人到 major_or_minor
    Then 玩家 1 應有灶
    And 玩家 1 應持有主要改良 hearth_5
    And 玩家 1 不應有壁爐牌
