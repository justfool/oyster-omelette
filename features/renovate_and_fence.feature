Feature: 翻修後圍籬
  階段 6 那格必須先翻修，然後若木頭夠再圍 1 格牧場。
  付不起翻修就不能用這格。翻修成功但圍不起來，仍然算做完行動。

  Scenario: 材料和木頭都夠就翻修並圍牧場
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 renovation_and_fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土與 1 蘆葦
    And 玩家 1 身上有 4 木
    And 玩家 1 放置工人到 renovation_and_fences
    Then 上次放置應成功
    And 第 1 列第 1 格應是黏土屋
    And 玩家 1 的牧場數應為 1
    And 玩家 1 應有 0 木

  Scenario: 只能翻修時仍然可以用這格
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 renovation_and_fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土與 1 蘆葦
    And 玩家 1 身上有 0 木
    And 玩家 1 放置工人到 renovation_and_fences
    Then 上次放置應成功
    And 第 1 列第 1 格應是黏土屋
    And 玩家 1 的牧場數應為 0

  Scenario: 付不起翻修就不能用，即使木頭夠圍籬
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 renovation_and_fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 4 木
    And 玩家 1 放置工人到 renovation_and_fences
    Then 上次放置應失敗且原因包含 cannot_renovate
    And 第 1 列第 1 格應是木屋
    And 玩家 1 的牧場數應為 0

  Scenario: 翻修成功但籬笆已滿 15 段，仍算做完行動
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 renovation_and_fences
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土與 1 蘆葦
    And 玩家 1 身上有 4 木
    And 玩家 1 已用掉 15 段籬笆
    And 玩家 1 放置工人到 renovation_and_fences
    Then 上次放置應成功
    And 第 1 列第 1 格應是黏土屋
    And 玩家 1 的牧場數應為 0

