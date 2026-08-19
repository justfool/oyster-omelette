Feature: 本專案目前的簡化
  這些不是官方最終規則，是現在引擎的行為。以後做選擇 UI 再改。

  Scenario: 沒指定目標時農場擴建會蓋到材料用完
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 12 木與 4 蘆葦
    And 玩家 1 放置工人到 farm_expansion
    Then 上次放置應成功
    And 玩家 1 的房間數應為 4
    And 玩家 1 應有 0 蘆葦

  Scenario: 住不下的羊有壁爐就全煮
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 sheep
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 已有壁爐
    And 羊市上有 3 羊
    And 玩家 1 放置工人到 sheep
    Then 玩家 1 應有 1 羊
    And 玩家 1 應有 6 食物

  Scenario: 繁殖容量只剩 1 時固定先羊
    Given 1 位玩家的農家樂修訂版
    When 完成開局設置
    And 玩家 1 圍出一塊牧場
    And 玩家 1 圍出一塊牧場
    And 玩家 1 身上有 2 羊
    And 玩家 1 身上有 2 野豬
    And 進行收成
    Then 玩家 1 應有 3 羊
    And 玩家 1 應有 2 野豬

  Scenario: 主要改良自動蓋第一張付得起的壁爐
    Given 1 位玩家的農家樂修訂版
    And 回合卡先翻 major_or_minor
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 身上有 2 黏土
    And 玩家 1 放置工人到 major_or_minor
    Then 玩家 1 應有壁爐
    And 玩家 1 應持有主要改良 fireplace_2
