# AI-Powered Google Form Creator

Tích hợp Google Gemini AI để tự động tạo Google Forms từ text hoặc file upload.

## Tính năng

- 🤖 Sử dụng Google Gemini 2.5 Flash để phân tích yêu cầu
- 📝 Tạo form từ mô tả bằng text
- 📄 Tạo form từ file upload (txt, pdf, docx, csv, xlsx)
- ✨ Tự động tạo câu hỏi phù hợp dựa trên nội dung
- 🔗 Tự động tạo Google Form và trả về link

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Đảm bảo đã setup Google Forms API

Xem hướng dẫn trong `README.md` hoặc `setup_guide.md` để:
- Bật Google Forms API và Google Drive API
- Tạo OAuth credentials
- Cấu hình OAuth consent screen

### 3. Cài đặt dependencies tùy chọn (cho file upload)

**Để hỗ trợ PDF:**
```bash
pip install PyPDF2
```

**Để hỗ trợ Word documents:**
```bash
pip install python-docx
```

**Để hỗ trợ Excel/CSV:**
```bash
pip install pandas openpyxl
```

## Sử dụng

### Cách 1: Chạy script tương tác

```bash
python ai_form_creator.py
```

Script sẽ hỏi bạn:
1. Chọn phương thức: Text input hoặc File upload
2. Nhập text mô tả hoặc đường dẫn file
3. AI sẽ tự động tạo form cho bạn

### Cách 2: Sử dụng trong code

```python
from ai_form_creator import AIFormCreator

# Khởi tạo với Gemini API key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Get from https://aistudio.google.com/app/apikey
creator = AIFormCreator(GEMINI_API_KEY)

# Tạo form từ text
form_url = creator.create_form_from_text("""
Tôi cần tạo form khảo sát về sản phẩm mới với các câu hỏi:
- Tên khách hàng
- Đánh giá sản phẩm (thang điểm 1-5)
- Màu sắc yêu thích
- Gợi ý cải thiện
""")

# Hoặc tạo form từ file
form_url = creator.create_form_from_file("requirements.txt")
```

## Ví dụ

### Ví dụ 1: Tạo form từ text

**Input:**
```
Tôi cần form đăng ký sự kiện với:
- Họ tên (bắt buộc)
- Email (bắt buộc)
- Số điện thoại
- Ngày tham gia
- Thời gian ưa thích
- Chế độ ăn uống (vegetarian, vegan, normal)
- Ghi chú đặc biệt
```

**Output:**
- Form được tạo tự động với các câu hỏi phù hợp
- Link form để chia sẻ

### Ví dụ 2: Tạo form từ file

Bạn có file `survey_requirements.txt`:
```
Khảo sát mức độ hài lòng khách hàng:
- Tên khách hàng
- Mức độ hài lòng (1-10)
- Sản phẩm đã mua
- Khả năng giới thiệu (có/không/có thể)
- Góp ý
```

Chạy:
```bash
python ai_form_creator.py
# Chọn option 2
# Nhập đường dẫn: survey_requirements.txt
```

## Các loại file được hỗ trợ

- **Text files (.txt)**: Đọc trực tiếp
- **PDF (.pdf)**: Cần PyPDF2
- **Word (.docx, .doc)**: Cần python-docx
- **Excel/CSV (.xlsx, .xls, .csv)**: Cần pandas

## Cấu trúc form được tạo

AI sẽ tự động tạo:
- **Title**: Tiêu đề form
- **Description**: Mô tả form
- **Questions**: Các câu hỏi với:
  - Loại câu hỏi phù hợp (text, choice, scale, etc.)
  - Options cho câu hỏi multiple choice
  - Required/optional flags
  - Scale min/max cho rating questions

## Troubleshooting

### Lỗi: "Error parsing Gemini response"

- AI có thể trả về format không đúng
- Thử lại với text mô tả rõ ràng hơn
- Kiểm tra API key có đúng không

### Lỗi: "File not found"

- Kiểm tra đường dẫn file có đúng không
- Sử dụng đường dẫn tuyệt đối nếu cần
- Đảm bảo file tồn tại và có quyền đọc

### Lỗi: "Module not found" khi đọc file

- Cài đặt dependencies cho loại file tương ứng:
  - PDF: `pip install PyPDF2`
  - Word: `pip install python-docx`
  - Excel: `pip install pandas openpyxl`

## API Key

Script hiện tại sử dụng API key được hardcode. Để bảo mật hơn, bạn có thể:

1. Sử dụng environment variable:
```python
import os
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-key-here')
```

2. Hoặc tạo file `.env`:
```
GEMINI_API_KEY=your-key-here
```

## License

MIT License


