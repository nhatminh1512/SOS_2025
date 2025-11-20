# 🚨 Hệ thống Quản lý Yêu cầu Cứu hộ SOS

Ứng dụng web Streamlit để quản lý và tìm kiếm các yêu cầu cứu hộ với tích hợp Gemini AI để phân tích địa chỉ.

## ✨ Tính năng

1. **🔍 Tìm kiếm & Lọc dữ liệu**
   - Lọc theo mức độ ưu tiên (Khẩn cấp, Cao, Trung bình, Thấp)
   - Lọc theo khu vực
   - Tìm kiếm theo địa chỉ
   - Phân trang dữ liệu
   - Tải xuống dữ liệu đã lọc

2. **➕ Thêm yêu cầu cứu hộ mới**
   - Form nhập thông tin đầy đủ
   - Tùy chọn sử dụng Gemini AI để cải thiện địa chỉ tự động
   - Lưu trực tiếp vào file CSV

3. **📊 Phân tích địa chỉ với Gemini AI**
   - Nhập địa chỉ để phân tích
   - Gemini AI sẽ chuẩn hóa và làm rõ địa chỉ
   - So sánh địa chỉ gốc và địa chỉ đã cải thiện

4. **📊 Thống kê**
   - Tổng số trường hợp
   - Số trường hợp khẩn cấp
   - Top 10 khu vực có nhiều yêu cầu nhất

## 🚀 Cài đặt và Chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Lấy Gemini API Key

1. Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Tạo API key mới
3. Copy API key

### 3. Chạy ứng dụng

```bash
streamlit run app.py
```

Ứng dụng sẽ mở tự động trong trình duyệt tại `http://localhost:8501`

## 📝 Cấu trúc dữ liệu

File CSV cần có các cột sau:
- `Mức độ ưu tiên`: Mức độ ưu tiên của yêu cầu
- `Chi tiết khu vực`: Tên khu vực
- `Số người`: Số lượng người cần cứu hộ
- `Địa chỉ`: Địa chỉ chi tiết
- `Số điện thoại`: Số điện thoại liên hệ

## 🔧 Sử dụng

### Tìm kiếm và Lọc

1. Chọn tab "🔍 Tìm kiếm & Lọc"
2. Sử dụng các bộ lọc:
   - **Mức độ ưu tiên**: Chọn mức độ ưu tiên
   - **Khu vực**: Chọn khu vực cụ thể
   - **Tìm kiếm theo địa chỉ**: Nhập từ khóa để tìm
3. Xem kết quả và tải xuống nếu cần

### Thêm yêu cầu mới

1. Chọn tab "➕ Thêm yêu cầu mới"
2. Điền thông tin:
   - Mức độ ưu tiên (bắt buộc)
   - Chi tiết khu vực (bắt buộc)
   - Số người
   - Địa chỉ (bắt buộc)
   - Số điện thoại
3. Tích chọn "Sử dụng Gemini để cải thiện địa chỉ" nếu muốn
4. Nhấn "➕ Thêm yêu cầu"

### Phân tích địa chỉ

1. Nhập Gemini API Key trong sidebar
2. Chọn tab "📊 Phân tích địa chỉ"
3. Nhập địa chỉ cần phân tích
4. Nhấn "🔍 Phân tích"
5. Xem kết quả địa chỉ đã được cải thiện

## 📦 Dependencies

- `streamlit`: Framework web app
- `pandas`: Xử lý dữ liệu CSV
- `google-generativeai`: Tích hợp Gemini AI

## ⚠️ Lưu ý

- Đảm bảo file CSV có tên chính xác: `mở quyền sửa đổi - HOÀN THIỆN - KV.csv`
- Gemini API Key cần được nhập trong sidebar để sử dụng tính năng phân tích địa chỉ
- Dữ liệu mới sẽ được lưu trực tiếp vào file CSV gốc

## 📄 License

MIT License

