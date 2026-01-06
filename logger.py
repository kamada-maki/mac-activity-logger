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

def get_active_window_info():
    """現在アクティブなアプリ名を取得"""
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    # 修正箇所: kNULLWindowID -> kCGNullWindowID
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
    for window in window_list:
        if window.get('kCGWindowLayer') == 0:
            return window.get('kCGWindowOwnerName', 'Unknown'), window.get('kCGWindowName', 'Unknown')
    return "Unknown", "Unknown"

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
            app_name, win_title = get_active_window_info()
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
                "app": app_name,
                "title": win_title,
                "text": all_text
            }
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
            # 画面数をログに表示
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Recorded: {app_name} ({len(display_ids)} screens)")
            
            # 1分待機
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n停止しました。")

if __name__ == "__main__":
    main()