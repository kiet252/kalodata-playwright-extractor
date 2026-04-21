HƯỚNG DẪN CHẠY TOOL LẤY DATA KALODATA

Cài đặt môi trường:

Mở Terminal/CMD tại thư mục chứa code.

Chạy lệnh: pip install -r requirements.txt

Chạy lệnh: playwright install chromium

Lưu ý quan trọng:

TẮT HẾT CHROME đang mở trên máy trước khi chạy script.

Ở lần chạy đầu tiên, script sẽ mở trình duyệt thật. Bạn hãy Đăng nhập vào Kalodata thủ công. Sau khi đăng nhập xong, hãy tắt trình duyệt đó đi để script bắt đầu chạy tự động cho các lần sau.

Cấu trúc dữ liệu:

Dữ liệu thô sẽ nằm trong thư mục captured_responses.

Dữ liệu bảng tính sẽ tự động xuất ra file .csv hoặc .xlsx.