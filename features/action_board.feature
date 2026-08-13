Feature: 2 人版行動板、累積格、工人擺放與回家
  農家樂修訂版 2 人固定行動格（括號內為穩定英文 id）：
  蓋房或畜舍（farm_expansion）、集會所（meeting_place）、
  穀物種子（grain_seeds）、農田（farmland）、課程（lessons）、
  日工（day_laborer）、森林（forest）、黏土坑（clay_pit）、
  蘆葦塘（reed_bank）、漁場（fishing）。

  每回合準備：翻開該回合的回合卡；赭色箭頭累積格再放入標示數量，沒拿走就繼續堆。
  工作階段由起始玩家開始，輪流各放 1 位家人到空的行動格並立刻結算。
  每格每回合最多 1 人。回家後家人回到自己的木屋，行動格淨空。

  擺放失敗回傳 PlaceResult.ok = false，error 為穩定英文原因：
  not_work_phase、not_your_turn、space_occupied、no_available_family、unknown_space。

  這一規格不涵蓋收成、圍籬幾何、主要改良效果與手牌。

  Background:
    Given 已開局的 2 人農家樂修訂版

  Scenario: 開局後尚未準備第 1 回合時，累積格沒有資源
    Then 目前回合應為 0
    And 尚未翻開任何回合卡
    And 行動格 forest 應有 0 木
    And 行動格 clay_pit 應有 0 黏土
    And 行動格 reed_bank 應有 0 蘆葦
    And 行動格 fishing 應有 0 食物
    And 2 人版固定行動格應包含 farm_expansion、meeting_place、grain_seeds、farmland、lessons、day_laborer、forest、clay_pit、reed_bank、fishing

  Scenario: 準備第 1 回合會翻開階段 1 回合卡，並放入累積資源
    When 準備這一回合
    Then 目前回合應為 1
    And 本回合翻開的回合卡應屬於階段 1
    And 輪到玩家 1 擺放
    And 行動格 forest 應有 3 木
    And 行動格 clay_pit 應有 1 黏土
    And 行動格 reed_bank 應有 1 蘆葦
    And 行動格 fishing 應有 1 食物

  Scenario: 準備回合之前不能擺放工人
    When 玩家 1 把家人放到 forest
    Then 這次擺放應該失敗，原因是 not_work_phase
    And 行動格 forest 應未被佔用
    And 玩家 1 還可擺放 2 位家人
    And 玩家 1 應有 0 木

  Scenario: 已被佔的行動格不能再放
    When 準備這一回合
    And 玩家 1 把家人放到 forest
    And 玩家 2 把家人放到 forest
    Then 這次擺放應該失敗，原因是 space_occupied
    And 行動格 forest 應被玩家 1 佔用
    And 玩家 2 還可擺放 2 位家人
    And 玩家 2 應有 0 木

  Scenario: 同一玩家不能在同一回合把兩個家人放到同一格
    When 準備這一回合
    And 玩家 1 把家人放到 forest
    And 玩家 2 把家人放到 day_laborer
    And 玩家 1 把家人放到 forest
    Then 這次擺放應該失敗，原因是 space_occupied
    And 行動格 forest 應被玩家 1 佔用
    And 玩家 1 還可擺放 1 位家人
    And 玩家 1 應有 3 木

  Scenario: 累積格連續兩回合沒人拿，第三回合拿走堆疊總和
    When 準備這一回合
    And 所有家人回家
    And 準備這一回合
    And 所有家人回家
    And 準備這一回合
    And 玩家 1 把家人放到 forest
    Then 這次擺放應該成功
    And 玩家 1 應有 9 木
    And 行動格 forest 應有 0 木

  Scenario: 有人拿走後下一回合準備只再放一份
    When 準備這一回合
    And 玩家 1 把家人放到 forest
    Then 玩家 1 應有 3 木
    And 行動格 forest 應有 0 木
    When 所有家人回家
    And 準備這一回合
    Then 行動格 forest 應有 3 木
    And 玩家 1 應有 3 木

  Scenario: 玩家沒有剩餘家人時不能再放
    When 準備這一回合
    And 玩家 1 把家人放到 forest
    And 玩家 2 把家人放到 clay_pit
    And 玩家 1 把家人放到 reed_bank
    And 玩家 2 把家人放到 fishing
    And 玩家 1 把家人放到 day_laborer
    Then 這次擺放應該失敗，原因是 no_available_family
    And 行動格 day_laborer 應未被佔用
    And 玩家 1 應有 2 食物
    And 玩家 1 還可擺放 0 位家人

  Scenario: 工作階段必須從起始玩家開始
    When 準備這一回合
    Then 輪到玩家 1 擺放
    When 玩家 2 把家人放到 day_laborer
    Then 這次擺放應該失敗，原因是 not_your_turn
    And 行動格 day_laborer 應未被佔用
    And 玩家 2 應有 3 食物
    And 玩家 2 還可擺放 2 位家人

  Scenario: 回家後行動格淨空，家人回到農場木屋
    When 準備這一回合
    And 玩家 1 把家人放到 forest
    And 玩家 2 把家人放到 clay_pit
    And 所有家人回家
    Then 行動格 forest 應未被佔用
    And 行動格 clay_pit 應未被佔用
    And 玩家 1 的第 1 列第 1 格應有 1 位家人
    And 玩家 1 的第 2 列第 1 格應有 1 位家人
    And 玩家 2 的第 1 列第 1 格應有 1 位家人
    And 玩家 2 的第 2 列第 1 格應有 1 位家人
    And 玩家 1 還可擺放 2 位家人
    And 玩家 2 還可擺放 2 位家人
    And 玩家 1 的家人數應為 2
    And 玩家 1 應有 3 木
    And 行動格 forest 應有 0 木

  Scenario: 非法行動格 id 不能放
    When 準備這一回合
    And 玩家 1 把家人放到 moon_landing
    Then 這次擺放應該失敗，原因是 unknown_space
    And 玩家 1 還可擺放 2 位家人
    When 玩家 1 把家人放到 Forest
    Then 這次擺放應該失敗，原因是 unknown_space
    And 行動格 forest 應未被佔用

  Scenario: 前 4 回合翻開的都是階段 1 回合卡
    When 連續準備 4 個回合並在每回合結束後回家
    Then 已翻開的回合卡應剛好是階段 1 的四張

  Scenario: 日工拿到 2 食物，且不會跨回合堆疊
    When 準備這一回合
    And 所有家人回家
    And 準備這一回合
    And 玩家 1 把家人放到 day_laborer
    Then 這次擺放應該成功
    And 玩家 1 應有 4 食物

  Scenario: 穀物種子拿到 1 穀
    When 準備這一回合
    And 玩家 1 把家人放到 grain_seeds
    Then 這次擺放應該成功
    And 玩家 1 應有 1 穀

  Scenario: 集會所讓後手成為起始玩家，下回合由其先放
    When 準備這一回合
    And 玩家 1 把家人放到 forest
    And 玩家 2 把家人放到 meeting_place
    Then 玩家 2 應是起始玩家
    And 玩家 1 不應是起始玩家
    When 所有家人回家
    And 準備這一回合
    Then 輪到玩家 2 擺放
    When 玩家 1 把家人放到 clay_pit
    Then 這次擺放應該失敗，原因是 not_your_turn
    When 玩家 2 把家人放到 clay_pit
    Then 這次擺放應該成功

  Scenario: 農田、課程、蓋房格這一增量只要能被佔
    When 準備這一回合
    And 玩家 1 把家人放到 farmland
    And 玩家 2 把家人放到 lessons
    Then 行動格 farmland 應被玩家 1 佔用
    And 行動格 lessons 應被玩家 2 佔用
    When 所有家人回家
    And 準備這一回合
    And 玩家 1 把家人放到 farm_expansion
    Then 行動格 farm_expansion 應被玩家 1 佔用

  Scenario: 回家後尚未準備下一回合時不能再放
    When 準備這一回合
    And 所有家人回家
    And 玩家 1 把家人放到 forest
    Then 這次擺放應該失敗，原因是 not_work_phase
    And 行動格 forest 應未被佔用

  Scenario: 輪到自己時才能放，不能連放兩位當對手還有家人
    When 準備這一回合
    And 玩家 1 把家人放到 forest
    And 玩家 1 把家人放到 clay_pit
    Then 這次擺放應該失敗，原因是 not_your_turn
    And 行動格 clay_pit 應未被佔用
    And 玩家 1 還可擺放 1 位家人
