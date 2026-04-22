import pandas as pd
from playwright.sync_api import sync_playwright
import os

# --- CẤU HÌNH ---
KEYWORD = "realpewpew"
OUTPUT_EXCEL = f"Bao_Cao_Chuyen_Nghiep_{KEYWORD}.xlsx"

def scrape_with_headers(keyword):
    user_data_dir = os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Default")

    with sync_playwright() as p:
        print(f"🚀 Đang quét dữ liệu có gán nhãn cho: {keyword}")
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            page.goto("https://www.kalodata.com/creator", wait_until="networkidle")
            
            # Thực hiện tìm kiếm
            search_input = "input[placeholder*='Search']"
            page.wait_for_selector(search_input)
            page.fill(search_input, keyword)
            page.keyboard.press("Enter")
            
            page.wait_for_timeout(7000) # Đợi load bảng

            # 1. LẤY TÊN CỘT (HEADERS) TỪ GIAO DIỆN
            header_elements = page.query_selector_all("th") 
            headers = [h.inner_text().strip() for h in header_elements if h.inner_text().strip()]
            
            # Nếu không tìm thấy thẻ <th>, ta tự định nghĩa bộ khung chuẩn của Kalodata
            if not headers:
                headers = ["Creator", "Phân loại", "Quốc gia", "Followers", "Doanh thu (GMV)", "Đơn hàng", "Tỉ lệ chuyển đổi", "Video/Live"]

            # 2. LẤY DỮ LIỆU CÁC HÀNG
            rows = page.query_selector_all("tr")
            final_data = []

            for row in rows:
                # Chỉ lấy những hàng chứa từ khóa (để loại bỏ header lặp lại hoặc rác)
                row_text = row.inner_text()
                if keyword.lower() in row_text.lower():
                    # Lấy dữ liệu từng ô (td) trong hàng đó
                    cells = row.query_selector_all("td")
                    row_data = [c.inner_text().strip() for c in cells if c.inner_text().strip()]
                    
                    if row_data:
                        # Đảm bảo số lượng cột khớp với headers (tránh lệch hàng)
                        if len(row_data) > len(headers):
                            row_data = row_data[:len(headers)]
                        elif len(row_data) < len(headers):
                            row_data += [""] * (len(headers) - len(row_data))
                            
                        final_data.append(row_data)

            # 3. XUẤT FILE EXCEL CÓ TIÊU ĐỀ
            if final_data:
                df = pd.DataFrame(final_data, columns=headers)
                
                # Làm sạch dữ liệu một chút (xóa các dòng trống nếu có)
                df = df.dropna(how='all')
                
                df.to_excel(OUTPUT_EXCEL, index=False)
                print(f"✅ ĐÃ XUẤT FILE EXCEL CHUYÊN NGHIỆP: {OUTPUT_EXCEL}")
                print(f"📋 Các trường đã bắt được: {', '.join(headers)}")
            else:
                print("❌ Tìm thấy hàng nhưng không tách được các ô dữ liệu.")

        finally:
            browser.close()

if __name__ == "__main__":
    scrape_with_headers(KEYWORD)