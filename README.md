````markdown
# Smart Checkout 系統

基於 STM32 + Python 的智慧結帳原型，結合影像偵測、自動輸送與薄膜鍵盤／LCD 互動，實現自動結帳、手動修正、刪除與重置等功能。

---

## 功能特色

- **自動偵測**：每 N 幀使用 YOLOv8 模型（`model/best.pt`）辨識商品並追蹤。  
- **即時計價**：檢測到新物件即自動加價，並更新 LCD 顯示。  
- **手動輸入／刪除**：  
  - 按 **A** → 進入「刪除確認」或暫停檢測  
  - 按 **A**（再次）→ 確認刪除上一項  
  - 按 **B** → 恢復／啟動檢測（從暫停或結帳後）  
  - 按 **C** → 清除當前結帳紀錄並暫停  
  - 按 **0–9** → 手動加入對應索引商品  
  - 按 **\*** → 立即刪除上一項  
- **LCD 顯示**：I2C 接 `HD44780`，兩行動態顯示品名與價格／總價。  
- **薄膜鍵盤**：4×4 row/col 掃描，可配合鍵位重新映射。

---

## 硬體需求

- **STM32 Nucleo-F429ZI** (或相似 STM32F4 板)  
- **I2C LCD** (HD44780 + PCF8574)  
- **4×4 薄膜鍵盤**  
- **攝影機** (USB, 供 Python 偵測用)  
- **連接線**：STM32 ↔ LCD (I2C SDA/SCL)、STM32 ↔ 鍵盤 (4 行 + 4 列)、STM32 ↔ PC (USB-UART)

### 鍵盤腳位示例

| 鍵位 | Row/Col | STM32 腳位   |
| ---- | ------- | ------------ |
| Row1 | output  | PD9          |
| Row2 | output  | PD14         |
| Row3 | output  | PF15         |
| Row4 | output  | PE13         |
| Col1 | input   | PF14         |
| Col2 | input   | PE11         |
| Col3 | input   | PE9          |
| Col4 | input   | PF13         |

（依實際接線與 `keypad.c` 中設定匹配。）

---

## 軟體需求

- Python **3.9+**  
- Pip 套件：  
  ```text
  opencv-python
  numpy
  pyserial
  torch
  torchvision
  ultralytics
  scikit-image
  filterpy
````

* STM32 HAL、`liquidcrystal_i2c`、`keypad.c/.h`（STM32CubeMX 生成）

---

## 安裝與執行

1. **Clone 專案**

   ```bash
   git clone https://github.com/ZhwnWeiXiao/Smart_checkout_F.git
   cd Smart_checkout_F
   ```

2. **建立虛擬環境**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **安裝依賴**

   ```bash
   pip install -r requirements.txt
   ```

4. **上傳 STM32 程式**

   * 用 STM32CubeIDE 或相容工具編譯並燒錄 `main.c` + `keypad.c/.h` + `liquidcrystal_i2c`。
   * 確認 USART3 (115200 8N1) 已連接到 PC 的 COMx。

5. **執行 Python**

   ```bash
   python main.py
   ```

6. **按鍵操作**

   * **B**：啟動／繼續檢測
   * **A**：刪除確認／暫停
   * **A → A**：刪除上一項
   * **C**：結帳清空並暫停
   * **0–9**：手動加入
   * **\***：立即刪除
   * **q**：退出程式

---

## 專案結構

```
Smart_checkout_F/
├── main.py
├── requirements.txt
├── model/
│   └── best.pt
└── modules/
    ├── billing.py
    ├── detection.py
    ├── prices.py
    ├── sort.py
    ├── tracker.py
    └── uart_lcd.py
```

---

## 注意事項

* 請確認 STM32 的 **COM 埠號** 與 Python 端 `UART_PORT` 相符。
* 確保 `model/best.pt` 已放置並支援你自己的模型。
