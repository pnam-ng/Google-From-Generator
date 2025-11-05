# Khắc phục lỗi 403: access_denied / Fix 403: access_denied Error

## Lỗi (Error)

Nếu bạn gặp lỗi này:
```
FormGeneration chưa hoàn tất quy trình xác minh của Google. 
Ứng dụng này đang trong giai đoạn kiểm thử và chỉ những người kiểm thử 
được nhà phát triển phê duyệt mới có thể truy cập.

Lỗi 403: access_denied
```

Đây là lỗi phổ biến khi ứng dụng Google OAuth ở chế độ "Testing" (Kiểm thử).

## Cách khắc phục (Solution)

### Bước 1: Truy cập Google Cloud Console
1. Mở trình duyệt và truy cập: https://console.cloud.google.com/
2. Đăng nhập bằng tài khoản Google của bạn
3. Chọn dự án (project) mà bạn đã tạo

### Bước 2: Mở OAuth Consent Screen
1. Trong menu bên trái, click vào **"APIs & Services"**
2. Click vào **"OAuth consent screen"**

### Bước 3: Thêm Test User (Người dùng thử nghiệm)
1. Cuộn xuống phần **"Test users"** (ở cuối trang)
2. Click nút **"ADD USERS"** hoặc **"+ ADD USERS"**
3. Nhập **chính xác** địa chỉ email Google của bạn
   - Email này phải là email bạn sử dụng để đăng nhập Google
   - Ví dụ: `yourname@gmail.com`
4. Click **"ADD"**
5. Lặp lại nếu bạn muốn thêm nhiều người dùng khác
6. Click **"SAVE"** ở cuối trang

### Bước 4: Chạy lại script
1. Xóa file `token.pickle` nếu có (để bắt đầu xác thực mới)
2. Chạy lại script Python của bạn:
   ```bash
   python quick_start.py
   ```
3. Lần này bạn sẽ có thể đăng nhập thành công!

## Hình ảnh minh họa (Visual Guide)

### Vị trí Test Users trong OAuth Consent Screen:
```
OAuth consent screen
├── App information
├── App domain
├── Authorized domains
├── Developer contact information
└── Test users  ← Ở đây! (Here!)
    └── [+ ADD USERS]  ← Click vào đây
```

## Lưu ý quan trọng (Important Notes)

1. **Email phải chính xác**: Email bạn thêm phải khớp 100% với email bạn dùng để đăng nhập Google
2. **Chế độ Testing**: Ứng dụng ở chế độ Testing có giới hạn 100 người dùng thử nghiệm
3. **Production Mode**: Để sử dụng với nhiều người dùng hơn, bạn cần:
   - Publish ứng dụng (yêu cầu xác minh từ Google)
   - Hoặc chuyển sang Google Workspace domain (không cần xác minh)

## Vẫn gặp lỗi? (Still having issues?)

1. Kiểm tra lại email đã thêm có đúng không
2. Đảm bảo bạn đã click "SAVE" sau khi thêm email
3. Xóa file `token.pickle` và thử lại
4. Đảm bảo bạn đang đăng nhập đúng tài khoản Google trong trình duyệt
5. Thử chờ vài phút sau khi thêm test user (có thể cần thời gian đồng bộ)

## English Version

If you're seeing this error:
```
FormGeneration hasn't completed Google's verification process.
This app is in testing mode and only approved test users can access it.

Error 403: access_denied
```

### Solution Steps:

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account
   - Select your project

2. **Open OAuth Consent Screen**
   - Click "APIs & Services" in the left menu
   - Click "OAuth consent screen"

3. **Add Test Users**
   - Scroll down to "Test users" section (at the bottom)
   - Click "ADD USERS" or "+ ADD USERS"
   - Enter your Google email address (the exact one you use to sign in)
   - Click "ADD"
   - Click "SAVE" at the bottom of the page

4. **Run Script Again**
   - Delete `token.pickle` file if it exists
   - Run your script again: `python quick_start.py`
   - You should now be able to authenticate successfully!

### Important:
- The email must match exactly with your Google sign-in email
- Testing mode allows up to 100 test users
- For production use, you need to publish the app (requires verification)

---

**Need help?** Check the main `setup_guide.md` for more detailed instructions.

