Feature: 動物要有地方住
  拿羊、豬、牛時要住得下。房子可當寵物養 1 隻。
  住不下的：有壁爐就煮成食物，沒有就跑掉。

  Scenario: 沒牧場也能養 1 隻寵物羊
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sheep
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 sheep
    Then 上次放置應成功
    And 玩家 1 應有 1 羊

  Scenario: 住不下又沒壁爐，多的羊會跑掉
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sheep
    When 完成開局設置
    And 準備下一回合
    And 羊市上有 3 羊
    And 玩家 1 放置工人到 sheep
    Then 玩家 1 應有 1 羊
    And 玩家 1 應有 2 食物

  Scenario: 有壁爐時，住不下的羊煮成食物
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sheep
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 已有壁爐
    And 羊市上有 3 羊
    And 玩家 1 放置工人到 sheep
    Then 玩家 1 應有 1 羊
    And 玩家 1 應有 6 食物
