import time
import cv2
import pyautogui
import pytesseract
import numpy as np
from PIL import ImageGrab
import pygetwindow as gw
import tkinter as tk
from tkinter import messagebox

# 初始化 Tesseract-OCR 的路径（如果需要）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 配置文件路径
TEMPLATE_IMAGE_PATH = "yuanbao_template.png"  # 替换为你的元宝模板图像路径

# 全局配置（将通过GUI设置）
TARGET_PRICE = 600  # 默认值
Tn = 6  # 默认值
transactions = 0  # 已完成交易数

# 新增的GUI函数
def create_config_gui():
    def on_confirm():
        global TARGET_PRICE, Tn  # 修正拼写错误为 TARGET_PRICE
        try:
            # 获取输入并验证
            new_price = int(price_entry.get())
            new_tn = int(num_entry.get())
            if new_price <= 0 or new_tn <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的正整数")
            return

        # 更新全局变量
        global TARGET_PRICE, Tn
        TARGET_PRICE = new_price
        Tn = new_tn

        # 关闭窗口并启动主程序
        root.destroy()
        main()

    root = tk.Tk()
    root.title("自动购买配置")
    root.geometry("300x150")

    # 价格设置
    tk.Label(root, text="最高购买价格：").grid(row=0, column=0, padx=5, pady=5)
    price_entry = tk.Entry(root)
    price_entry.grid(row=0, column=1, padx=5, pady=5)
    price_entry.insert(0, str(TARGET_PRICE))

    # 数量设置
    tk.Label(root, text="处理前几个物品：").grid(row=1, column=0, padx=5, pady=5)
    num_entry = tk.Entry(root)
    num_entry.grid(row=1, column=1, padx=5, pady=5)
    num_entry.insert(0, str(Tn))

    # 确认按钮
    confirm_btn = tk.Button(root, text="开始执行", command=on_confirm, width=15)
    confirm_btn.grid(row=2, columnspan=2, pady=10)

    root.mainloop()

# 以下保持原有函数不变...
def switch_to_game_window(window_title):
    """
    切换到指定的游戏窗口
    """
    try:
        # 获取所有窗口的列表
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            game_window = windows[0]  # 假设只匹配第一个符合标题的窗口
            game_window.activate()  # 激活窗口
            print(f"[INFO] 已切换到窗口: {game_window.title}")
            time.sleep(1)  # 给窗口一些加载时间
        else:
            print(f"[ERROR] 未找到标题包含 '{window_title}' 的窗口")
    except Exception as e:
        print(f"[ERROR] 切换窗口失败: {e}")

# 图像预处理函数
def preprocess_image(image):
    """
    预处理图像：灰度化 -> 二值化。
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 转为灰度图
    _, binary = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)  # 转为二值图
    return binary

# 截图
def capture_screen(region=None):
    """
    捕获屏幕截图，区域为 region（左，上，右，下）。
    """
    try:
        # print(f"[INFO] 正在截图，区域: {region}")
        screenshot = ImageGrab.grab(bbox=region)  # 截取指定区域
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2RGB)
        return screenshot
    except Exception as e:
        print(f"[ERROR] 截图失败: {e}")
        return None
    
# 模板匹配
def match_template(target_image, template_image, threshold=0.8):
    target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(target_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    # 查找匹配区域
    locations = np.where(result >= threshold)
    return locations, template_gray.shape
# 遮盖元宝区域
def mask_template_areas(image, locations, template_size):
    masked_image = image.copy()
    h, w = template_size
    for pt in zip(*locations[::-1]):
        cv2.rectangle(masked_image, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), -1)  # 用白色遮盖
    return masked_image

# 图像识别价格
def get_price_from_image(image):
    """
    从图像中提取价格。
    """
    try:
        config = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
        text = pytesseract.image_to_string(image, config=config)  # OCR 识别
        # 提取连续数字部分，忽略非数字字符
        numbers = ''.join(filter(str.isdigit, text))
        if len(numbers) > 0:
            price = int(numbers)
            return price
        else:
            return None
    except ValueError:
        print("[WARNING] OCR 无法识别出价格或结果为空")
        return None

# 模拟鼠标点击
def click_position(x, y):
    """
    模拟鼠标点击指定位置。
    """
    try:
        # print(f"[INFO] 正在点击位置: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.2)  # 移动鼠标
        pyautogui.click()  # 点击
    except Exception as e:
        print(f"[ERROR] 点击操作失败: {e}")

# 主逻辑
def main():
    GAME_WINDOW_TITLE = "ZhuxianClient"  # 游戏的窗口标题
    switch_to_game_window(GAME_WINDOW_TITLE)
    # 模拟一个鼠标点击，确保切换成功后可以执行脚本动作
    pyautogui.click(1000, 150)  # 随便点击某个位置
    print("已切换到游戏窗口")

    global transactions
    while transactions < Tn:
        # 点击第n个物品
        positionY = 382 + transactions*108
        click_position(1190, positionY)
        time.sleep(0.8)

        # 1. 截取交易行界面
        region = (1960, 360, 2090, 415)  # 根据游戏分辨率调整
        screen = capture_screen(region)
        # 保存截图

        # 2. 图像处理
        # 加载图像
        template_image = cv2.imread(TEMPLATE_IMAGE_PATH, cv2.IMREAD_COLOR)
        # 执行模板匹配
        locations, template_size = match_template(screen, template_image)
        # 遮盖元宝区域
        masked_image = mask_template_areas(screen, locations, template_size)
        # 灰度处理
        filtered_screen = preprocess_image(masked_image)  # 使用灰度化 + 二值化的处理方法

        # 3. OCR 识别价格
        price = get_price_from_image(filtered_screen)
        if price is not None:
            print(f"[INFO] OCR 识别价格: {price}")
            if price <= TARGET_PRICE:
                # 4. 执行购买操作
                click_position(2280, 382)  # 购买按钮位置
                time.sleep(0.2)  # 等待确认弹窗

                # 5. 点击确认按钮
                click_position(1180, 945)  # 确认按钮位置
                time.sleep(0.1)
                click_position(1156, 728)  # 二次确认按钮位置
                transactions += 1
                print(f"[INFO] 价格为{price}的商品购买成功！已处理的交易数：{transactions}")
            else:
                print(f"[INFO] 价格 {price} 超出目标价格 {TARGET_PRICE}，略过购买")
                transactions += 1
                click_position(570, 238)
                continue  # 跳出本轮循环
        else:
            print("[WARNING] 未能识别价格，跳过此商品。")

        # 6. 单击返回，等待下一轮
        click_position(570, 238)
        time.sleep(0.6)
    print("交易完成！")

# [原所有函数保持原样，此处为节省空间省略，实际使用时请保留完整函数]

if __name__ == "__main__":
    create_config_gui()  # 改为首先启动配置界面