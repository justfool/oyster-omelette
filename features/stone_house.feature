Feature: 石頭屋
  黏土屋再翻修會變成石頭屋，費用是 1 蘆葦加每間 1 石頭。
  之後蓋房間改付 5 石 2 蘆。石頭屋每間 2 分。

  Scenario: 兩間黏土屋翻修成石頭屋
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 renovation
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土與 1 蘆葦
    And 玩家 1 放置工人到 renovation
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 身上有 2 石頭與 1 蘆葦
    And 玩家 1 放置工人到 renovation
    Then 上次放置應成功
    And 第 1 列第 1 格應是石頭屋
    And 第 2 列第 1 格應是石頭屋
    And 玩家 1 應有 0 石頭
    And 玩家 1 應有 0 蘆葦
