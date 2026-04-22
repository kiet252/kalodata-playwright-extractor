import json
import os
import time
from playwright.sync_api import sync_playwright

# --- CẤU HÌNH ---
KEYWORD = "hang du muc"
timestamp = time.strftime("%Y%m%d_%H%M%S")
OUTPUT_JSON = f"Search_API_{KEYWORD}_{timestamp}.json"

def intercept_api_data(keyword):
    user_data_dir = os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Default")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        captured_data = {"success": True, "data": []}

        def handle_response(response):
            nonlocal captured_data
            # Chỉ bắt gói tin JSON từ các endpoint tìm kiếm/danh sách
            if "application/json" in response.headers.get("content-type", ""):
                # Lọc các URL đặc trưng của Kalodata khi search
                if any(x in response.url for x in ["query", "list", "search", "detail"]):
                    try:
                        data = response.json()
                        
                        # Hàm quét mọi object trong JSON
                        def find_items(obj):
                            if isinstance(obj, dict):
                                # Nếu thấy có nickname/handle thì kiểm tra
                                nick = str(obj.get("nickname", "")).lower()
                                hdl = str(obj.get("handle", "")).lower()
                                
                                if keyword.lower() in nick or keyword.lower() in hdl:
                                    if not any(d.get("id") == obj.get("id") for d in captured_data["data"]):
                                        captured_data["data"].append(obj)
                                        print(f"🎯 Đã bắt được: {obj.get('nickname')}")
                                
                                for v in obj.values(): find_items(v)
                            elif isinstance(obj, list):
                                for item in obj: find_items(item)

                        find_items(data)
                    except:
                        pass

        page.on("response", handle_response)

        try:
            print("🌐 Truy cập trang Creator...")
            page.goto("https://www.kalodata.com/creator", wait_until="networkidle")
            
            # 1. Thực hiện tìm kiếm
            search_input = "input[placeholder*='Search']"
            page.wait_for_selector(search_input)
            page.fill(search_input, keyword)
            page.wait_for_timeout(500) # Nghỉ nhẹ để web nhận text
            page.keyboard.press("Enter")
            
            print(f"⏳ Đang đợi kết quả cho '{keyword}'...")
            page.wait_for_timeout(7000) 

            # 2. CHIÊU CUỐI: Nếu vẫn chưa thấy data, hãy click vào hàng đầu tiên hiện ra
            if not captured_data["data"]:
                print("⚠️ API chưa phản hồi dữ liệu đúng. Đang thử kích hoạt bằng cách Click...")
                # Tìm hàng nào có chứa text keyword và click
                try:
                    target = page.locator("tr").filter(has_text=keyword).first
                    if target.is_visible():
                        target.click()
                        page.wait_for_timeout(5000) # Đợi trang detail load API
                except:
                    pass

            if captured_data["data"]:
                with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                    json.dump(captured_data, f, ensure_ascii=False, indent=4)
                print(f"✅ XONG! Đã lưu dữ liệu vào: {OUTPUT_JSON}")
            else:
                print("❌ Vẫn không thấy dữ liệu trong API. Hãy kiểm tra xem bạn đã Login Kalodata chưa.")

        finally:
            browser.close()

if __name__ == "__main__":
    intercept_api_data(KEYWORD)