# main.py

import cv2
import numpy as np
import time

from modules.detection import Detector
from modules.tracker   import Tracker
from modules.prices    import PRODUCT_PRICES
from modules.billing   import Billing
from modules.uart_lcd  import UART_LCD

# --- Parameters ---
MODEL_PATH     = "model/best.pt"
CONF_THRESH    = 0.4
UART_PORT      = "COM3"
BAUDRATE       = 115200
FRAME_INTERVAL = 3    # detect every 3 frames

def main():
    detector       = Detector(MODEL_PATH, conf=CONF_THRESH)
    tracker        = Tracker()
    billing        = Billing()
    lcd            = UART_LCD(UART_PORT, BAUDRATE, timeout=0.1)
    lcd.reset_input_buffer()

    cap            = cv2.VideoCapture(0)
    frame_count    = 0
    last_dets      = []
    confirm_delete = False
    pause_detect   = True   # 默认暂停检测，等待 B 启动

    # 初始提示
    lcd.clear()
    lcd.send_text("Press B to start")
    print("System idle: press 'B' to start detection")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # --- Auto-detect & draw & billing if running ---
            if not pause_detect and not confirm_delete:
                frame_count += 1
                if frame_count % FRAME_INTERVAL == 0:
                    last_dets = detector.detect(frame)

                dets_arr = np.array([d[:5] for d in last_dets]) if last_dets else np.empty((0,5))
                tracks   = tracker.update(dets_arr)

                for x1, y1, x2, y2, tid in tracks:
                    # 始终画框和 ID
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.putText(frame, f"ID:{tid}", (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

                    # 新出现的 tid 做计价
                    for dx1, dy1, dx2, dy2, conf, cls in last_dets:
                        if (max(0, min(x2,dx2)-max(x1,dx1)) *
                            max(0, min(y2,dy2)-max(y1,dy1))) > 0:
                            if tid not in tracker.seen_ids:
                                tracker.seen_ids.add(tid)
                                label = detector.model.names[cls]
                                price = PRODUCT_PRICES.get(label, 0)

                                lcd.clear()
                                line1 = f"{label}: ${price:.2f}"
                                billing.add_item(label, price)
                                line2 = f"Total: ${billing.total:.2f}"
                                lcd.send_text(line1)
                                lcd.send_text(line2)
                                print(f"[AUTO] {line1} | {line2}")

                            cv2.putText(frame, f"{label} {conf:.2f}",
                                        (x1, y2+20),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                        (255,255,255), 2)
                            break

            # --- Keypad input handling ---
            key = lcd.receive_text().strip()
            if key:
                print(f"[KEY] {repr(key)}")

                # 1) 确认删除
                if key.upper() == 'A' and confirm_delete:
                    name, price = billing.remove_last_item()
                    confirm_delete = False
                    pause_detect   = False
                    lcd.clear()
                    lcd.send_text(f"Deleted: {name}" if name else "Delete failed")
                    lcd.send_text(f"Total: ${billing.total:.2f}")
                    print(f"[KEY] Deleted: {name} (−${price:.2f})")

                # 2) 进入删除确认
                elif key.upper() == 'A' and billing.items:
                    confirm_delete = True
                    lcd.clear()
                    lcd.send_text(f"Confirm delete: {billing.items[-1][0]}")
                    lcd.send_text("Press 'A' to confirm")

                # 3) 启动/继续检测
                elif key.upper() == 'B':
                    pause_detect   = False
                    confirm_delete = False
                    tracker.seen_ids.clear()
                    frame_count    = 0
                    lcd.clear()
                    lcd.send_text("Detection RUNNING")
                    print("[CTRL] Detection RESUMED")

                # 4) 结账完成并暂停
                elif key.upper() == 'C':
                    billing = Billing()
                    tracker.seen_ids.clear()
                    confirm_delete = False
                    pause_detect   = True
                    lcd.clear()
                    lcd.send_text("Checkout Cleared")
                    lcd.send_text("Press B to start")
                    print("[CTRL] Checkout CLEARED, paused")

                # 5) 立即删除
                elif key == '*':
                    name, price = billing.remove_last_item()
                    lcd.clear()
                    lcd.send_text(f"Removed: {name}" if name else "Remove failed")
                    lcd.send_text(f"Total: ${billing.total:.2f}")
                    print(f"[KEY] Removed: {name} (−${price:.2f})")

                # 6) 取消删除确认
                elif confirm_delete:
                    confirm_delete = False
                    pause_detect   = False
                    lcd.clear()
                    lcd.send_text("Delete canceled")
                    lcd.send_text(f"Total: ${billing.total:.2f}")
                    print("[KEY] Delete canceled")

                # 7) 手动添加
                elif key.isdigit():
                    idx = int(key)
                    try:
                        label, price = billing.add_item_by_index(idx)
                        lcd.clear()
                        lcd.send_text(f"{label}: ${price:.2f}")
                        lcd.send_text(f"Total: ${billing.total:.2f}")
                        print(f"[KEY] Added: {label}")
                    except Exception:
                        lcd.clear()
                        lcd.send_text("Invalid index")

                # 8) 暂停检测（备用）
                elif key.upper() == 'A':
                    pause_detect = True
                    lcd.clear()
                    lcd.send_text("Detection PAUSED")
                    print("[CTRL] Detection PAUSED")

                # 9) 其他
                else:
                    lcd.clear()
                    lcd.send_text(f"Key: {key}")
                    print(f"[KEY] Unknown: {key}")

            # 显示画面 & 退出
            cv2.imshow("Smart Checkout", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.01)

    finally:
        cap.release()
        lcd.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
