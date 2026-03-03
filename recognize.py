import cv2
import ddddocr
import threading
import numpy as np
from typing import List, Tuple

ocr = ddddocr.DdddOcr(show_ad=False)
det = ddddocr.DdddOcr(det=True, show_ad=False)
ocr_lock = threading.Lock()


def safe_ocr(buf: bytes) -> str:
    """线程安全的 OCR 调用"""
    with ocr_lock:
        return ocr.classification(buf).strip()


def rotate_recognize(img: np.ndarray, target_chars: set, idx: int) -> str:
    """旋转识别单字符（带打印）"""
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2

    for ang in range(0, 360, 15):
        M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)
        rimg = cv2.warpAffine(img, M, (w, h), borderValue=(220, 240, 250))

        ok, buf = cv2.imencode(".jpg", rimg)
        if not ok:
            continue

        txt = safe_ocr(buf.tobytes())
        if txt in target_chars:
            print(f"✅ 字符{idx+1} 识别成功：{txt}（旋转 {ang}°）")
            return txt

    print(f"❌ 字符{idx+1} 识别失败（无匹配）")
    return ""


def getchar(cap_path: str = "captcha.jpg",
            up_crop: int = 100,
            bot_crop: Tuple[int, int] = (120, 210)) -> List[Tuple[int, int]]:
    """
    稳健优化版：
    - 必须识别 >=3 个字符
    - 自动配对最多 1 个字符
    """



    # ============================ 读取图片 ============================
    img = cv2.imread(cap_path)
    if img is None:
        print("❌ 无法读取图片")
        return []

    up_crop = min(up_crop, img.shape[0])
    bot_crop = (max(bot_crop[0], 0), min(bot_crop[1], img.shape[1]))

    up_img = img[:up_crop]
    bot_img = img[up_crop:, bot_crop[0]:bot_crop[1]]

    # ============================ 底栏识别 ============================
    ok, bot_buf = cv2.imencode(".jpg", bot_img)
    if not ok:
        print("❌ 底栏编码失败")
        return []

    bot_txt = safe_ocr(bot_buf.tobytes())
    print(f"底栏识别结果：{bot_txt}")

    if len(bot_txt) != 4 or len(set(bot_txt)) != 4:
        print("❌ 底栏字符必须为 4 个且不重复")
        return []

    target_chars = set(bot_txt)

    # ============================ 上部检测 ============================
    ok, up_buf = cv2.imencode(".jpg", up_img)
    bboxes = det.detection(up_buf.tobytes())

    print(f"检测到字符框：{bboxes}")

    if len(bboxes) != 4:
        print(f"❌ 上部检测到 {len(bboxes)} 个，应为 4 个")
        return []

    # ============================ 多线程旋转识别 ============================
    results = [""] * 4
    threads = []

    def worker(i, img):
        results[i] = rotate_recognize(img, target_chars, i)

    for i, (x1, y1, x2, y2) in enumerate(bboxes):
        char_img = up_img[y1:y2, x1:x2]
        t = threading.Thread(target=worker, args=(i, char_img))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # ============================ 整理字符数据 ============================
    items = []
    for i, ((x1, y1, x2, y2), txt) in enumerate(zip(bboxes, results)):
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        items.append({
            "txt": txt,
            "cx": cx,
            "cy": cy,
            "used": False
        })

    # ============================ 自动配对规则 ============================
    recognized = sum(1 for it in items if it["txt"])
    missing = 4 - recognized

    print(f"识别成功：{recognized}/4  缺失：{missing}")

    # 必须 >=3
    if recognized < 3:
        print("❌ 有效识别 <3，失败")
        return []

    # 只允许缺失 1 个
    if missing > 1:
        print("❌ 缺失超过 1 个，不允许自动配对")
        return []

    # 未识别的字符（最多 1 个）
    unused_items = [it for it in items if not it["txt"]]


    result = []



    for ch in bot_txt:
        found = None

        # ① 先找识别正确的
        for it in items:
            if not it["used"] and it["txt"] == ch:
                found = it
                break

        # ② 若未识别 → 自动配对（最多只有一个）
        if not found:
            if unused_items:
                found = unused_items.pop(0)
                print(f"⚠ 自动配对：底栏 '{ch}' → ({found['cx']}, {found['cy']})")
            else:
                print(f"❌ 无法配对底栏字符 '{ch}'")
                return []

        found["used"] = True
        result.append((found["cx"], found["cy"]))
        print(f"底栏 '{ch}' → ({found['cx']}, {found['cy']})")

    return result
