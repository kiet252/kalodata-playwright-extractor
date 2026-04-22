import pandas as pd
from playwright.sync_api import sync_playwright
import os

# --- CẤU HÌNH ---
KEYWORD = "Hang du muc"
OUTPUT_EXCEL = f"Danh_Sach_KOC_{KEYWORD.replace(' ', '_')}.xlsx"

def scrape_all_profiles(keyword):
    user_data_dir = os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Default")

    with sync_playwright() as p:
        print(f"🚀 Đang quét TẤT CẢ profile cho từ khóa: {keyword}")
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            page.goto("https://www.kalodata.com/creator", wait_until="networkidle")
            
            # 1. Thực hiện tìm kiếm
            search_input = "input[placeholder*='Search']"
            page.wait_for_selector(search_input)
            page.fill(search_input, keyword)
            page.keyboard.press("Enter")
            
            # Đợi load danh sách (tăng thời gian vì nhiều kết quả cần load lâu hơn)
            page.wait_for_timeout(10000) 

            # 2. LẤY TIÊU ĐỀ BẢNG
            headers = [h.inner_text().strip() for h in page.query_selector_all("th") if h.inner_text().strip()]
            if not headers:
                headers = ["STT", "Creator", "Phân loại", "Followers", "Doanh thu (GMV)", "Đơn hàng", "Tỉ lệ chuyển đổi", "Video/Live", "Quốc gia"]

            # 3. QUÉT TẤT CẢ CÁC HÀNG (TR)
            rows = page.query_selector_all("tr")
            final_data = []

            print(f"📊 Tìm thấy {len(rows)} hàng tiềm năng. Đang tách dữ liệu...")

            for row in rows:
                # Lấy text của cả hàng để kiểm tra xem có phải hàng chứa dữ liệu không
                row_text = row.inner_text().strip()
                
                # Loại bỏ hàng tiêu đề hoặc hàng trống
                if not row_text or row_text == "".join(headers):
                    continue
                
                # KỸ THUẬT MỚI: Thử lấy dữ liệu từ td, nếu không được thì tự tách chuỗi theo dòng (newline)
                cells = row.query_selector_all("td")
                if cells:
                    row_data = [c.inner_text().strip().replace('\n', ' ') for c in cells]
                else:
                    # Nếu không có td (do dùng div), ta tách theo xuống dòng
                    row_data = [line.strip() for line in row_text.split('\n') if line.strip()]

                if len(row_data) > 1: # Đảm bảo không phải hàng rác
                    # Cân bằng số cột để khớp với Excel
                    if len(row_data) > len(headers):
                        row_data = row_data[:len(headers)]
                    else:
                        row_data += [""] * (len(headers) - len(row_data))
                    
                    final_data.append(row_data)

            # 4. XUẤT EXCEL
            if final_data:
                df = pd.DataFrame(final_data, columns=headers[:len(final_data[0])])
                df.to_excel(OUTPUT_EXCEL, index=False)
                print(f"✅ THÀNH CÔNG! Đã lấy được {len(final_data)} profile vào file: {OUTPUT_EXCEL}")
            else:
                print("❌ Vẫn không tách được dữ liệu. Có thể bảng đang load chậm.")

        finally:
            browser.close()

if __name__ == "__main__":
    scrape_all_profiles(KEYWORD)