import serial
import time

class UART_LCD:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        if not self.ser.is_open:
            raise RuntimeError(f"无法开启串口 {port}")

    def send_text(self, text: str):
        data = text.encode('utf-8') + b'\n'
        self.ser.write(data)
        time.sleep(0.05)

    def send_raw(self, data: bytes):
        self.ser.write(data)
        time.sleep(0.02)

    def clear(self):
        """发送 CLS 文本命令，触发 STM32 上的清屏逻辑。"""
        self.send_text("CLS")

    def receive_text(self) -> str:
        line = self.ser.readline()
        return line.decode('utf-8', errors='ignore').strip()

    def reset_input_buffer(self):
        self.ser.reset_input_buffer()

    def close(self):
        self.ser.close()
