# 烏嘎嘎 A／B 牌庫

來源：[烏嘎嘎農家樂卡牌中心](https://agricola-viewer.vercel.app/)（非官方譯本）。基本盒帶 `*` 的卡與 Artifex／Bubulcus 擴充都在。

| 資料夾 | 內容 |
|---|---|
| `text/` | 每張卡一份 JSON，檔名是卡號 |
| `images/` | 對應卡圖（多為 `.webp`，A039 是 `.jpg`） |

Windows 檔名不能有 `*`，所以 `A002*` 存成 `A002.json`／`A002.webp`；JSON 裡的 `卡片ID` 仍保留星號。

圖檔不進 git（實體卡照片、約 19MB）。本機重抓：

```powershell
uv run python database/ugg/fetch.py
```
