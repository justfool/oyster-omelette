Feature: TUI 除錯軌跡
  為了在鍵盤操作對不上畫面的時候能推測原因
  身為開發者
  我希望記得最近按了哪個鍵、鍵被誰處理，並可把軌跡寫進檔案

  Scenario: 按鍵與動作會記進軌跡
    Given 已開局的 2 人農家樂修訂版
    When 記錄按下 i 鍵並觸發動作 inspect
    Then 除錯軌跡應包含按下「i」鍵
    And 除錯軌跡應提到處理者 inspect

  Scenario: 軌跡保留最近幾筆
    Given 已開局的 2 人農家樂修訂版
    When 連續記錄超過上限的軌跡
    Then 只保留最近幾筆

  Scenario: 開啟檔案軌跡後會寫進檔案
    Given 已開局的 2 人農家樂修訂版
    When 開啟檔案軌跡寫入一筆
    Then 軌跡檔案應有那筆記錄