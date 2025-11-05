# Web UI Guide - AI-Powered Google Form Creator

Giao diện web đơn giản, dễ sử dụng cho người dùng không chuyên về kỹ thuật.

## 🚀 Quick Start

### Windows:
1. Double-click `start_web_app.bat`
2. Hoặc chạy: `python run_app.py`

### macOS/Linux:
1. Chạy: `chmod +x start_web_app.sh`
2. Chạy: `./start_web_app.sh`
3. Hoặc: `python3 run_app.py`

### Hoặc chạy trực tiếp:
```bash
python run_app.py
```

## 📋 Prerequisites

1. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Đảm bảo đã setup Google Forms API:**
   - Xem `README.md` hoặc `setup_guide.md`
   - Cần có `credentials.json` trong thư mục project

## 🎯 Sử dụng

### Bước 1: Khởi động ứng dụng

Chạy script khởi động (Windows hoặc macOS/Linux):
- **Windows:** Double-click `start_web_app.bat`
- **macOS/Linux:** Chạy `./start_web_app.sh`

Hoặc:
```bash
python run_app.py
```

### Bước 2: Mở trình duyệt

Ứng dụng sẽ tự động mở trình duyệt tại: `http://127.0.0.1:5000`

Nếu không tự động mở, mở trình duyệt và truy cập: `http://127.0.0.1:5000`

### Bước 3: Tạo form

**Cách 1: Nhập text**
1. Chọn tab "📝 Text Input"
2. Nhập mô tả form của bạn
3. Click "Create Form"
4. Đợi AI tạo form
5. Click "View Form" để xem form đã tạo

**Cách 2: Upload file**
1. Chọn tab "📄 File Upload"
2. Kéo thả file hoặc click để chọn file
3. Click "Create Form"
4. Đợi AI phân tích và tạo form
5. Click "View Form" để xem form đã tạo

## 📁 File types được hỗ trợ

- **TXT** - Text files
- **PDF** - PDF documents (cần PyPDF2)
- **DOCX/DOC** - Word documents (cần python-docx)
- **XLSX/XLS/CSV** - Excel/CSV files (cần pandas, openpyxl)

## 🎨 Tính năng UI

- ✅ Giao diện hiện đại, dễ sử dụng
- ✅ Drag & drop file upload
- ✅ Real-time progress indicators
- ✅ Error handling với thông báo rõ ràng
- ✅ Responsive design (hoạt động trên mobile)
- ✅ Tự động mở trình duyệt
- ✅ Direct links đến form (view & edit)

## 🔧 Troubleshooting

### "Module not found: flask"

**Giải pháp:**
```bash
pip install flask
```

Hoặc:
```bash
pip install -r requirements.txt
```

### "Failed to initialize AI creator"

**Giải pháp:**
- Kiểm tra file `credentials.json` có trong thư mục project
- Đảm bảo Google Forms API và Drive API đã được bật
- Xem `setup_guide.md` để setup đầy đủ

### Browser không tự động mở

**Giải pháp:**
- Mở trình duyệt thủ công
- Truy cập: `http://127.0.0.1:5000`

### Port 5000 đã được sử dụng

**Giải pháp:**
- Sửa file `app.py` hoặc `run_app.py`
- Thay đổi port từ 5000 sang port khác (ví dụ: 5001)

### File upload bị lỗi

**Nguyên nhân có thể:**
- File quá lớn (max 16MB)
- File type không được hỗ trợ
- Thiếu dependencies cho file type (VD: python-docx cho Word)

**Giải pháp:**
- Cài đặt dependencies tương ứng:
  ```bash
  pip install python-docx PyPDF2 pandas openpyxl
  ```

## 💡 Tips

1. **Text input:** Mô tả càng chi tiết, form càng tốt
   - Ví dụ: "Tạo form đăng ký với họ tên (bắt buộc), email (bắt buộc), số điện thoại, và đánh giá (thang điểm 1-5)"

2. **File upload:** File có nội dung rõ ràng sẽ cho kết quả tốt hơn

3. **Tạo nhiều form:** Click "Create Another" sau khi tạo form xong

## 🛑 Dừng server

Nhấn `Ctrl+C` trong terminal/command prompt để dừng server.

## 📱 Cross-platform

Ứng dụng web hoạt động trên:
- ✅ Windows
- ✅ macOS
- ✅ Linux
- ✅ Mobile browsers (responsive design)

## 📖 Xem thêm

- `README.md` - Tài liệu chính
- `README_AI.md` - Hướng dẫn AI integration
- `setup_guide.md` - Hướng dẫn setup Google APIs

