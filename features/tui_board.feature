Feature: 行動板像桌遊那樣分格
  為了有實體桌遊的感覺
  身為玩家
  我希望每個行動格是獨立可選的格子，並分成固定區與回合卡區

  Background:
    Given 已開局的 2 人農家樂修訂版

  Scenario: 固定區與回合卡區
    When 準備這一回合
    Then 固定區應包含農場擴建、聚會所、穀種、耕地、上課、日工、森林、黏土坑、蘆葦岸、漁場
    And 回合卡區應有 1 張已翻開
    And 回合卡區應有蓋著的空位
    And 蓋著的空位不應顯示卡名

  Scenario: 方向鍵選格與快捷鍵看說明
    When 準備這一回合
    And 選取行動格 forest
    Then 目前選取應是 forest
    And 選取說明應提到堆疊
    And 選取說明應提到木頭
    And 選取說明應提到是否要選農場格

  Scenario: 佔用格顯示工人圖示
    When 準備這一回合
    And 玩家 1 放置工人到 forest
    Then forest 格子應顯示玩家 1 的工人圖示
    And forest 格子不應只在文字尾端寫佔用人編號

  Scenario: 上帝模式才看得到未翻開卡名
    When 準備這一回合
    Then 蓋著的空位不應顯示卡名
    When 開啟上帝模式
    Then 未翻開回合卡可在上帝模式顯示名稱
