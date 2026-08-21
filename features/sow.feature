Feature: 播種
  有空田和穀物時，播種會把 1 穀放到田裡，田上變成 3 穀。
  一次可以播所有空田。沒有空田或沒有種子時不能用播種格。

  Scenario: 有田有穀就能播成 3 穀
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sow_and_or_bake
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 grain_seeds
    And 玩家 1 放置工人到 farmland
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 sow_and_or_bake
    Then 上次放置應成功
    And 玩家 1 應有 0 穀物
    And 第 1 列第 2 格田上應有 3 穀

  Scenario: 沒有種子不能播種
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sow_and_or_bake
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    And 玩家 1 放置工人到 sow_and_or_bake
    Then 上次放置應失敗且原因包含 cannot_sow

  Scenario: 有菜會播成田上 2 菜
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sow_and_or_bake
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    And 玩家 1 身上有 1 菜
    And 玩家 1 放置工人到 sow_and_or_bake
    Then 上次放置應成功
    And 玩家 1 應有 0 菜
    And 第 1 列第 2 格田上應有 2 菜

  Scenario: 目前一次會把所有空田先穀後菜播滿
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sow_and_or_bake
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 2 穀
    And 玩家 1 放置工人到 sow_and_or_bake
    Then 第 1 列第 2 格田上應有 3 穀
    And 第 1 列第 3 格田上應有 3 穀
    And 玩家 1 應有 0 穀

  Scenario: 指定只播一塊田時另一塊保持空
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sow_and_or_bake
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 2 穀
    And 玩家 1 下次播種只在第 1 列第 2 格播穀
    And 玩家 1 放置工人到 sow_and_or_bake
    Then 上次放置應成功
    And 第 1 列第 2 格田上應有 3 穀
    And 第 1 列第 3 格應是空田
    And 玩家 1 應有 1 穀物

  Scenario: 身上有穀也可以指定播菜
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sow_and_or_bake
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 1 穀
    And 玩家 1 身上有 1 菜
    And 玩家 1 下次播種只在第 1 列第 2 格播菜
    And 玩家 1 放置工人到 sow_and_or_bake
    Then 上次放置應成功
    And 第 1 列第 2 格田上應有 2 菜
    And 玩家 1 應有 1 穀物
