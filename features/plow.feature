Feature: 耕田
  耕地行動會在農場放 1 塊田。
  第一塊田可放在任何空地；之後的田必須與已有的田相鄰。
  不能耕在房間上。沒有合法空地時不能使用這格。

  Background:
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合

  Scenario: 第一次耕地會放在第一塊合法空地
    When 玩家 1 放置工人到 farmland
    Then 上次放置應成功
    And 玩家 1 的田地數應為 1
    And 第 1 列第 2 格應是田地

  Scenario: 第二塊田必須跟已有的田相鄰
    When 玩家 1 放置工人到 farmland
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 farmland
    Then 上次放置應成功
    And 玩家 1 的田地數應為 2
    And 第 1 列第 3 格應是田地

  Scenario: 房間不能被耕成田
    Then 第 1 列第 1 格應是木屋
    When 玩家 1 放置工人到 farmland
    Then 第 1 列第 1 格應是木屋
