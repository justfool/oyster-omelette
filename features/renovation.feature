Feature: 翻修房子
  翻修要把全部木屋一次改成黏土屋，費用是 1 蘆葦加每間 1 黏土。
  之後再蓋房間改付 5 黏土 2 蘆葦。黏土屋每間 1 分。

  Scenario: 兩間木屋翻修要 1 蘆 2 黏土
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 renovation
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土與 1 蘆葦
    And 玩家 1 放置工人到 renovation
    Then 上次放置應成功
    And 第 1 列第 1 格應是黏土屋
    And 第 2 列第 1 格應是黏土屋
    And 玩家 1 應有 0 黏土
    And 玩家 1 應有 0 蘆葦
