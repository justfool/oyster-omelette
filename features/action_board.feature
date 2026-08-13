Feature: 2 人版行動板的刁鑽規則
  固定格英文 id：farm_expansion（蓋房或畜舍）、meeting_place（集會所）、
  grain_seeds（穀物種子）、farmland（農田）、lessons（課程）、
  day_laborer（日工）、forest（森林）、clay_pit（黏土坑）、
  reed_bank（蘆葦塘）、fishing（漁場）。

  工作階段只在準備回合之後、回家之前。
  擺放失敗時格子維持原狀，家人也不消耗。
  未指定回合卡時，14 張依 6 階段在段內洗牌。
  這一規格不測收成、圍籬幾何、主要改良效果與手牌。

  Background:
    Given 2 位玩家的農家樂修訂版

  Scenario: 開局後尚未準備第 1 回合時，累積格沒有資源
    When 完成開局設置
    Then 目前回合應為 0
    And 尚未翻開任何回合卡
    And 森林應有 0 木
    And 黏土坑應有 0 黏土
    And 蘆葦岸應有 0 蘆葦
    And 漁場應有 0 食物
    And 2 人版固定行動格應包含 farm_expansion、meeting_place、grain_seeds、farmland、lessons、day_laborer、forest、clay_pit、reed_bank、fishing

  Scenario: 準備第 1 回合會翻開階段 1 回合卡，並放入累積資源
    When 完成開局設置
    And 準備下一回合
    Then 目前回合應為 1
    And 本回合翻開的卡應屬於階段 1
    And 輪到玩家 1
    And 森林應有 3 木
    And 黏土坑應有 1 黏土
    And 蘆葦岸應有 1 蘆葦
    And 漁場應有 1 食物

  Scenario: 準備回合之前不能擺放工人
    When 完成開局設置
    And 玩家 1 放置工人到 forest
    Then 上次放置應失敗且原因包含 不是工作階段
    And forest 應沒有人
    And 玩家 1 還可擺放 2 位家人
    And 玩家 1 應有 0 木

  Scenario: 已被佔的行動格不能再放，且仍被原玩家佔
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 玩家 2 放置工人到 forest
    Then 上次放置應失敗且原因包含 已經有人
    And forest 應被玩家 1 佔領
    And 玩家 2 還可擺放 2 位家人
    And 玩家 2 應有 0 木

  Scenario: 同一玩家不能在同一回合把兩個家人放到同一格
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 玩家 2 放置工人到 day_laborer
    And 玩家 1 放置工人到 forest
    Then 上次放置應失敗且原因包含 已經有人
    And forest 應被玩家 1 佔領
    And 玩家 1 還可擺放 1 位家人
    And 玩家 1 應有 3 木

  Scenario: 累積格連續兩回合沒人拿，第三回合拿走堆疊總和
    When 完成開局設置
    And 準備下一回合
    And 所有家人回家
    And 準備下一回合
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    Then 上次放置應成功
    And 玩家 1 應有 9 木
    And 森林應有 0 木

  Scenario: 有人拿走後下一回合準備只再放一份
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    Then 玩家 1 應有 3 木
    And 森林應有 0 木
    When 所有家人回家
    And 準備下一回合
    Then 森林應有 3 木
    And 玩家 1 應有 3 木

  Scenario: 玩家沒有剩餘家人時不能再放
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 玩家 2 放置工人到 clay_pit
    And 玩家 1 放置工人到 reed_bank
    And 玩家 2 放置工人到 fishing
    And 玩家 1 放置工人到 day_laborer
    Then 上次放置應失敗且原因包含 沒有可放置的家人
    And day_laborer 應沒有人
    And 玩家 1 應有 2 食物
    And 玩家 1 還可擺放 0 位家人

  Scenario: 工作階段必須從起始玩家開始
    When 完成開局設置
    And 準備下一回合
    Then 輪到玩家 1
    When 玩家 2 放置工人到 day_laborer
    Then 上次放置應失敗且原因包含 不是這位玩家的回合
    And day_laborer 應沒有人
    And 玩家 2 應有 3 食物
    And 玩家 2 還可擺放 2 位家人

  Scenario: 回家後行動格淨空，兩位玩家的家人都回到木屋
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 玩家 2 放置工人到 clay_pit
    And 所有家人回家
    Then forest 應沒有人
    And clay_pit 應沒有人
    And 玩家 1 的第 1 列第 1 格應有 1 位家人
    And 玩家 1 的第 2 列第 1 格應有 1 位家人
    And 玩家 2 的第 1 列第 1 格應有 1 位家人
    And 玩家 2 的第 2 列第 1 格應有 1 位家人
    And 玩家 1 還可擺放 2 位家人
    And 玩家 2 還可擺放 2 位家人
    And 玩家 1 的家人數應為 2
    And 玩家 1 應有 3 木
    And 森林應有 0 木

  Scenario: 非法行動格 id 區分大小寫，且不消耗家人
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 moon_landing
    Then 上次放置應失敗且原因包含 沒有這個行動格
    And 玩家 1 還可擺放 2 位家人
    When 玩家 1 放置工人到 Forest
    Then 上次放置應失敗且原因包含 沒有這個行動格
    And forest 應沒有人

  Scenario: 前 4 回合翻開的都是階段 1 回合卡
    When 完成開局設置
    And 連續準備 4 個回合並在每回合結束後回家
    Then 已翻開的回合卡應剛好是階段 1 的四張

  Scenario: 日工拿到 2 食物，且不會跨回合堆疊
    When 完成開局設置
    And 準備下一回合
    And 所有家人回家
    And 準備下一回合
    And 玩家 1 放置工人到 day_laborer
    Then 上次放置應成功
    And 玩家 1 應有 4 食物

  Scenario: 穀物種子拿到 1 穀
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 grain_seeds
    Then 上次放置應成功
    And 玩家 1 應有 1 穀物

  Scenario: 集會所讓後手成為起始玩家，下回合由其先放
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 玩家 2 放置工人到 meeting_place
    Then 玩家 2 應是起始玩家
    And 玩家 1 不應是起始玩家
    When 所有家人回家
    And 準備下一回合
    Then 輪到玩家 2
    When 玩家 1 放置工人到 clay_pit
    Then 上次放置應失敗且原因包含 不是這位玩家的回合
    When 玩家 2 放置工人到 clay_pit
    Then 上次放置應成功

  Scenario: 課程與蓋房格這一增量只要能被佔
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 lessons
    And 玩家 2 身上有 5 木與 2 蘆葦
    And 玩家 2 放置工人到 farm_expansion
    Then lessons 應被玩家 1 佔領
    And farm_expansion 應被玩家 2 佔領

  Scenario: 回家後尚未準備下一回合時不能再放
    When 完成開局設置
    And 準備下一回合
    And 所有家人回家
    And 玩家 1 放置工人到 forest
    Then 上次放置應失敗且原因包含 不是工作階段
    And forest 應沒有人

  Scenario: 輪到自己時才能放，不能連放兩位當對手還有家人
    When 完成開局設置
    And 準備下一回合
    And 玩家 1 放置工人到 forest
    And 玩家 1 放置工人到 clay_pit
    Then 上次放置應失敗且原因包含 不是這位玩家的回合
    And clay_pit 應沒有人
    And 玩家 1 還可擺放 1 位家人
