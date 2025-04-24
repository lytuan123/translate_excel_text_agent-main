# Tasks for PDF OCR Integration

Đây là danh sách các task cần thực hiện để tích hợp chức năng OCR PDF vào Advanced Translation Suite, dựa trên PRD_OCR_Integration.md.

- [x] **[Setup-1]** Cài đặt Dependencies hệ thống: Hướng dẫn/Xác nhận việc cài đặt Tesseract OCR và Poppler.
- [x] **[Setup-2]** Cập nhật Dependencies Python: Thêm `pytesseract` và `pdf2image` vào `requirements.txt`.
- [x] **[Backend-1]** Tạo module xử lý OCR: Tạo file `app/ocr_processor.py` chứa hàm `process_pdf_ocr(pdf_file_path, lang_code)`.
- [x] **[Backend-2]** Implement PDF to Image: Trong `process_pdf_ocr`, sử dụng `pdf2image` để chuyển đổi PDF thành ảnh.
- [x] **[Backend-3]** Implement Image to Text (OCR): Trong `process_pdf_ocr`, sử dụng `pytesseract` để đọc văn bản từ ảnh.
- [x] **[Backend-4]** Hoàn thiện logic OCR: Ghép nối text, xử lý lỗi, trả về kết quả.
- [x] **[Frontend-1]** Định nghĩa danh sách ngôn ngữ OCR: Tạo list ngôn ngữ OCR trong `app/web_app.py`.
- [x] **[Frontend-2]** Thêm UI Components vào Gradio: Thêm `gr.File`, `gr.Dropdown`, `gr.Button`, `gr.TextArea` vào `app/web_app.py`.
- [x] **[Integration-1]** Kết nối Button và Backend: Kết nối sự kiện click của nút Extract với hàm `process_pdf_ocr`.
- [x] **[Integration-2]** Xử lý đầu vào/đầu ra: Truyền đúng tham số và hiển thị kết quả lên UI.
- [x] **[Integration-3]** Xử lý trạng thái/lỗi UI: Hiển thị thông báo loading và lỗi trên giao diện.
- [x] **[Feature-Enhancement]** (Optional) Implement "Send to Translate": Thêm nút/logic chuyển text OCR sang ô dịch.
- [ ] **[Testing-1]** Kiểm thử cơ bản: Test với PDF tiếng Anh đơn giản.
- [ ] **[Testing-2]** Kiểm thử đa ngôn ngữ: Test với PDF tiếng Việt,...
- [ ] **[Testing-3]** Kiểm thử PDF phức tạp/hình ảnh: Test với PDF dạng ảnh quét.
- [x] **[Docs]** Cập nhật README: Ghi chú về dependencies hệ thống và tính năng mới. 