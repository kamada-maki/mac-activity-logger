import os
import json
import time
import subprocess
from datetime import datetime
import Quartz
from Vision import VNImageRequestHandler, VNRecognizeTextRequest, VNRequestTextRecognitionLevelAccurate
from Cocoa import NSURL

def get_active_window_info():
    """現在アクティブなアプリ名を取得"""
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
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
    temp_img = "tmp_capture.png"
    print(f"記録開始。保存先: {log_file} (Ctrl+Cで停止)")
    
    try:
        while True:
            app_name, win_title = get_active_window_info()
            # スクショ撮影（-x でシャッター音なし）
            subprocess.run(["screencapture", "-x", temp_img])
            
            ocr_text = ""
            if os.path.exists(temp_img):
                ocr_text = perform_ocr(temp_img)
                os.remove(temp_img)
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "app": app_name,
                "title": win_title,
                "text": ocr_text
            }
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Recorded: {app_name}")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n停止しました。")

if __name__ == "__main__":
    main()