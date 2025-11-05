# Khắc phục lỗi: Google Drive API chưa được bật / Fix: Google Drive API Not Enabled

## Lỗi (Error)

Nếu bạn gặp lỗi này:
```
Google Drive API has not been used in project ... or it is disabled.
Enable it by visiting https://console.developers.google.com/...
```

Điều này có nghĩa là Google Drive API chưa được bật trong dự án Google Cloud của bạn.

## Tại sao cần Google Drive API?

Google Forms API **yêu cầu** Google Drive API để tạo form. Khi bạn tạo một form mới, nó được tạo trong Google Drive, vì vậy cả hai API đều phải được bật.

## Cách khắc phục (Solution)

### Bước 1: Truy cập Google Cloud Console

1. Mở trình duyệt và truy cập: https://console.cloud.google.com/
2. Đăng nhập bằng tài khoản Google của bạn
3. Chọn dự án (project) mà bạn đã tạo

### Bước 2: Bật Google Drive API

1. Trong menu bên trái, click vào **"APIs & Services"**
2. Click vào **"Library"** (Thư viện)
3. Trong thanh tìm kiếm, nhập: **"Google Drive API"**
4. Click vào kết quả **"Google Drive API"**
5. Click nút **"Enable"** (Bật) màu xanh
6. Đợi vài giây để API được kích hoạt

### Bước 3: Xác minh Google Forms API đã bật

1. Vẫn ở trong "Library"
2. Tìm kiếm: **"Google Forms API"**
3. Kiểm tra xem đã bật chưa (nút sẽ hiển thị "Manage" thay vì "Enable")
4. Nếu chưa bật, click "Enable"

### Bước 4: Đợi vài phút

Sau khi bật API, Google cần vài phút để đồng bộ. Đợi 2-5 phút trước khi chạy lại script.

### Bước 5: Chạy lại script

```bash
python quick_start.py
```

## Kiểm tra APIs đã bật

Để xem danh sách các API đã bật:

1. Vào Google Cloud Console
2. Click "APIs & Services" > "Enabled APIs" (hoặc "APIs enabled")
3. Bạn sẽ thấy danh sách các API đã bật

Đảm bảo bạn thấy:
- ✅ **Google Drive API**
- ✅ **Google Forms API**
- ✅ **Google Docs API** (nếu bạn sử dụng tính năng Google Docs link)

## Hình ảnh minh họa (Visual Guide)

### Vị trí trong Google Cloud Console:
```
Google Cloud Console
├── APIs & Services
    ├── Library  ← Vào đây để bật API
    │   ├── Search: "Google Drive API"
    │   │   └── Click "Enable"
    │   └── Search: "Google Forms API"
    │       └── Click "Enable" (nếu chưa bật)
    └── Enabled APIs  ← Kiểm tra ở đây
```

## Lưu ý quan trọng (Important Notes)

1. **Cả hai API đều cần thiết:**
   - Google Forms API (để quản lý form)
   - Google Drive API (để tạo file form trong Drive)

2. **Thời gian kích hoạt:**
   - API thường được kích hoạt ngay lập tức
   - Nhưng có thể mất 2-5 phút để đồng bộ hoàn toàn
   - Nếu vẫn gặp lỗi sau 5 phút, thử:
     - Đăng xuất và đăng nhập lại Google Cloud Console
     - Xóa file `token.pickle` và xác thực lại

3. **Quyền truy cập:**
   - Đảm bảo bạn có quyền "Editor" hoặc "Owner" trong dự án
   - Nếu bạn không thấy nút "Enable", hãy kiểm tra quyền của bạn

## English Version

If you're seeing this error:
```
Google Drive API has not been used in project ... or it is disabled.
```

### Why Google Drive API is Needed

Google Forms API **requires** Google Drive API to create forms. When you create a new form, it's created in Google Drive, so both APIs must be enabled.

### Solution Steps

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account
   - Select your project

2. **Enable Google Drive API**
   - Click "APIs & Services" in the left menu
   - Click "Library"
   - Search for "Google Drive API"
   - Click on it
   - Click the "Enable" button

3. **Verify Google Forms API is Enabled**
   - Still in "Library"
   - Search for "Google Forms API"
   - Make sure it's enabled (button shows "Manage" not "Enable")
   - If not enabled, click "Enable"

4. **Wait a Few Minutes**
   - Google needs 2-5 minutes to sync after enabling APIs
   - Wait before running your script again

5. **Run Script Again**
   ```bash
   python quick_start.py
   ```

### Check Enabled APIs

To see which APIs are enabled:

1. Go to Google Cloud Console
2. Click "APIs & Services" > "Enabled APIs"
3. You should see:
   - ✅ **Google Drive API**
   - ✅ **Google Forms API**
   - ✅ **Google Docs API** (if using Google Docs link feature)

### Important Notes

- **Both APIs are required:** Forms API and Drive API
- **Activation time:** Usually instant, but may take 2-5 minutes to fully sync
- **Permissions:** Make sure you have "Editor" or "Owner" role in the project

---

**Still having issues?** Check the main `setup_guide.md` for more detailed instructions.

