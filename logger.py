import os
import json
import time
import subprocess
from datetime import datetime
import Quartz
from Vision import VNImageRequestHandler, VNRecognizeTextRequest, VNRequestTextRecognitionLevelAccurate
from Cocoa import NSURL

def get_display_ids():
    """接続されているすべてのディスプレイIDを取得する"""
    max_displays = 10
    # CGGetActiveDisplayList を使用して接続中のディスプレイIDリストを取得
    (error, ids, count) = Quartz.CGGetActiveDisplayList(max_displays, None, None)
    if error != 0:
        return []
    return ids

def get_display_bounds():
    """各ディスプレイの座標範囲を取得する"""
    display_ids = get_display_ids()
    bounds = []
    for display_id in display_ids:
        rect = Quartz.CGDisplayBounds(display_id)
        bounds.append({
            'id': display_id,
            'x': rect.origin.x,
            'y': rect.origin.y,
            'width': rect.size.width,
            'height': rect.size.height
        })
    return bounds

def get_display_for_window(window_bounds, display_bounds_list):
    """ウィンドウがどのディスプレイにあるかを判定"""
    win_x = window_bounds.get('X', 0)
    win_y = window_bounds.get('Y', 0)
    win_w = window_bounds.get('Width', 0)
    win_h = window_bounds.get('Height', 0)
    win_center_x = win_x + win_w / 2
    win_center_y = win_y + win_h / 2

    for i, db in enumerate(display_bounds_list):
        if (db['x'] <= win_center_x < db['x'] + db['width'] and
            db['y'] <= win_center_y < db['y'] + db['height']):
            return i
    return 0

def get_active_apps_per_display():
    """各ディスプレイの最前面アプリを取得"""
    display_bounds_list = get_display_bounds()
    num_displays = len(display_bounds_list)

    if num_displays == 0:
        return ["Unknown"]

    # 各ディスプレイの最前面アプリを格納
    display_apps = [None] * num_displays

    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    for window in window_list:
        if window.get('kCGWindowLayer') != 0:
            continue

        bounds = window.get('kCGWindowBounds')
        if not bounds:
            continue

        display_idx = get_display_for_window(bounds, display_bounds_list)

        # まだそのディスプレイのアプリが記録されていなければ記録
        if display_apps[display_idx] is None:
            app_name = window.get('kCGWindowOwnerName', 'Unknown')
            display_apps[display_idx] = app_name

        # 全ディスプレイ分取得できたら終了
        if all(app is not None for app in display_apps):
            break

    # Noneのままのディスプレイは"Unknown"に
    return [app if app else "Unknown" for app in display_apps]

def perform_ocr(image_path):
    """Vision FrameworkでOCR実行"""
    input_url = NSURL.fileURLWithPath_(image_path)
    request = VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(VNRequestTextRecognitionLevelAccurate)
    request.setRecognitionLanguages_(["ja-JP", "en-US"])
    handler = VNImageRequestHandler.alloc().initWithURL_options_(input_url, None)
    success, error = handler.performRequests_error_([request], None)
    if not success: return ""
    return "\n".join([r.topCandidates_(1)[0].string() for r in request.results()])

def main():
    log_file = f"log_{datetime.now().strftime('%Y%m%d')}.jsonl"
    print(f"記録開始。保存先: {log_file} (Ctrl+Cで停止)")
    
    try:
        while True:
            apps = get_active_apps_per_display()
            display_ids = get_display_ids()

            ocr_texts = []
            for i, display_id in enumerate(display_ids):
                temp_img = f"tmp_cap_{i}.png"

                # -D オプションでディスプレイIDを指定して確実に撮影
                subprocess.run(["screencapture", "-x", "-D", str(display_id), temp_img])

                if os.path.exists(temp_img):
                    text = perform_ocr(temp_img)
                    if text:
                        # どちらの画面のテキストか分かるようにラベルを付与
                        ocr_texts.append(f"--- Screen {i} ---\n{text}")
                    os.remove(temp_img)

            all_text = "\n".join(ocr_texts)

            data = {
                "timestamp": datetime.now().isoformat(),
                "apps": apps,
                "text": all_text
            }

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")

            # 画面数をログに表示
            apps_str = ", ".join(apps)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Recorded: [{apps_str}] ({len(display_ids)} screens)")

            # 1分待機
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n停止しました。")

if __name__ == "__main__":
    main()