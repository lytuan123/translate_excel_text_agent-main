# Hướng dẫn sử dụng Advanced Translation Suite

## Giới thiệu

Advanced Translation Suite là một công cụ dịch thuật đa năng hỗ trợ dịch văn bản, tệp PDF và Excel. Công cụ này sử dụng các mô hình ngôn ngữ tiên tiến để cung cấp bản dịch chất lượng cao với nhiều tùy chọn tùy chỉnh.

## Cài đặt

1. Tải và giải nén gói Advanced Translation Suite
2. Chạy file `install.bat` để cài đặt tự động
3. Sau khi cài đặt hoàn tất, chạy file `run.bat` để khởi động ứng dụng

## Các tính năng chính

### 1. Dịch văn bản thông thường

**Cách sử dụng:**
1. Nhập hoặc dán văn bản cần dịch vào ô văn bản
2. Chọn ngôn ngữ nguồn và đích
3. (Tùy chọn) Chọn phong cách dịch
4. (Tùy chọn) Thêm hướng dẫn tùy chỉnh
5. (Tùy chọn) Tải lên file thuật ngữ tùy chỉnh
6. Nhấn "Dịch"

**Quy trình xử lý:**
1. Hệ thống kiểm tra và chuẩn bị văn bản
2. Chia văn bản thành các đoạn phù hợp
3. Dịch từng đoạn với phong cách đã chọn
4. Kiểm tra và cải thiện bản dịch
5. Kết hợp các đoạn và trả về kết quả

### 2. Dịch tệp PDF

**Cách sử dụng:**
1. Tải lên tệp PDF cần dịch
2. Chọn ngôn ngữ nguồn và đích
3. (Tùy chọn) Chọn phong cách dịch
4. (Tùy chọn) Thêm hướng dẫn tùy chỉnh
5. (Tùy chọn) Tải lên file thuật ngữ tùy chỉnh
6. Nhấn "Dịch PDF"

**Quy trình xử lý:**
1. Trích xuất văn bản từ PDF
2. Phát hiện ngôn ngữ trong các đoạn văn
3. Dịch từng đoạn với phong cách đã chọn
4. Tạo hai tệp đầu ra:
   - PDF: Giữ nguyên định dạng gốc
   - TXT: Văn bản thuần túy

### 3. Dịch tệp Excel

**Cách sử dụng:**
1. Tải lên tệp Excel (.xlsx hoặc .xls)
2. Chọn ngôn ngữ nguồn và đích
3. (Tùy chọn) Chọn phong cách dịch
4. (Tùy chọn) Thêm hướng dẫn tùy chỉnh
5. (Tùy chọn) Tải lên file thuật ngữ tùy chỉnh
6. Nhấn "Dịch Excel"

**Quy trình xử lý:**
1. Đọc tệp Excel
2. Phát hiện ngôn ngữ trong các ô
3. Dịch từng ô với phong cách đã chọn
4. Giữ nguyên định dạng và công thức
5. Tạo tệp Excel mới với nội dung đã dịch

## Các phong cách dịch

1. **General**: Dịch thông thường, chính xác và rõ ràng
2. **Literary**: Phong cách văn học, chú trọng vẻ đẹp ngôn ngữ
3. **Technical**: Phong cách kỹ thuật, chính xác về thuật ngữ
4. **Financial**: Phong cách tài chính, chuyên nghiệp
5. **Legal**: Phong cách pháp lý, chính xác và trang trọng
6. **Medical**: Phong cách y tế, chính xác về thuật ngữ y khoa
7. **Scientific**: Phong cách khoa học, khách quan và chính xác
8. **Casual**: Phong cách thân mật, tự nhiên
9. **Formal**: Phong cách trang trọng, lịch sự
10. **Marketing**: Phong cách tiếp thị, hấp dẫn
11. **Educational**: Phong cách giáo dục, dễ hiểu
12. **Creative**: Phong cách sáng tạo, linh hoạt

## Tùy chỉnh thuật ngữ

Bạn có thể tạo file thuật ngữ tùy chỉnh với định dạng:
```
source_term=target_term
```

Mỗi cặp thuật ngữ trên một dòng. Ví dụ:
```
computer=máy tính
software=phần mềm
hardware=phần cứng
```

## Xử lý lỗi thường gặp

1. **Lỗi tải lên file**
   - Đảm bảo file không quá lớn
   - Kiểm tra định dạng file (PDF: .pdf, Excel: .xlsx/.xls)
   - Thử tải lại file

2. **Lỗi dịch**
   - Kiểm tra kết nối internet
   - Xác nhận API key còn hiệu lực
   - Thử lại với đoạn văn bản nhỏ hơn

3. **Lỗi định dạng**
   - Đảm bảo file không bị hỏng
   - Kiểm tra quyền truy cập file
   - Thử mở file bằng ứng dụng khác

## Hỗ trợ

Nếu bạn gặp vấn đề hoặc cần hỗ trợ:
1. Kiểm tra file hướng dẫn này
2. Xem log lỗi trong thư mục `logs`
3. Liên hệ hỗ trợ kỹ thuật 