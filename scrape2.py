import os
import json
import pandas as pd

def find_and_export_data(keyword="realpewpew"):
    folder = "captured_responses"
    
    if not os.path.exists(folder):
        print(f"❌ Thư mục '{folder}' không tồn tại!")
        return

    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            path = os.path.join(folder, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if keyword.lower() in content.lower():
                        print(f"🌟 TÌM THẤY RỒI! File: {filename}")
                        data = json.loads(content)
                        
                        # Lưu bản sao dự phòng
                        with open("KHO_BAU_DATA.json", "w", encoding="utf-8") as f2:
                            json.dump(data, f2, indent=4, ensure_ascii=False)
                        
                        # Gọi hàm xử lý dữ liệu
                        extract_to_excel(data, keyword)
                        return
            except Exception:
                continue
    print(f"❌ Không tìm thấy dữ liệu cho '{keyword}'")

def extract_to_excel(json_data, keyword):
    try:
        # KIỂM TRA CẤU TRÚC: Nếu json_data là list thì dùng luôn, 
        # nếu là dict thì mới tìm vào bên trong
        if isinstance(json_data, list):
            items = json_data
        elif isinstance(json_data, dict):
            # Thử các trường hợp phổ biến của Kalodata
            items = json_data.get("data", {}).get("list", []) if isinstance(json_data.get("data"), dict) else json_data.get("data", [])
            if not items: # Nếu vẫn không thấy, lấy chính nó nếu nó chứa danh sách
                items = [json_data]
        else:
            items = []

        if not items:
            print("⚠️ Cấu trúc JSON lạ, không tìm thấy danh sách Creator.")
            return

        # Chuyển đổi sang DataFrame
        df = pd.DataFrame(items)
        
        # Xuất file Excel
        output_name = f"Data_Kalodata_{keyword}.xlsx"
        df.to_excel(output_name, index=False)
        
        print(f"✅ ĐÃ XUẤT FILE EXCEL: {output_name}")
        print("-" * 30)
        # Hiển thị các cột nếu chúng tồn tại trong data
        cols = [c for c in ['nickname', 'uniqueId', 'followerCount'] if c in df.columns]
        if cols:
            print(df[cols].head())
            
    except Exception as e:
        print(f"❌ Lỗi xử lý Excel: {e}")

if __name__ == "__main__":
    find_and_export_data("realpewpew")