# PRD: Tích hợp OCR PDF vào Advanced Translation Suite

**Phiên bản:** 1.0
**Ngày:** 2024-07-28
**Tác giả:** AI Assistant (Gemini) & User

## 1. Giới thiệu & Mục tiêu

### 1.1. Bối cảnh
Advanced Translation Suite hiện tại hỗ trợ dịch văn bản và tệp Excel. Tuy nhiên, người dùng thường gặp khó khăn khi cần dịch nội dung từ các tệp PDF, đặc biệt là các PDF được tạo từ hình ảnh quét hoặc có định dạng phức tạp khiến việc sao chép/dán văn bản trực tiếp không hiệu quả hoặc cho kết quả sai lệch (lỗi font, ký tự rác).

### 1.2. Mục tiêu sản phẩm
Tích hợp chức năng Nhận dạng Ký tự Quang học (OCR) trực tiếp vào giao diện web (Gradio) của Advanced Translation Suite để cho phép người dùng:
*   Tải lên tệp PDF.
*   Trích xuất nội dung văn bản từ PDF bằng công nghệ OCR.
*   Sử dụng văn bản đã trích xuất làm đầu vào cho chức năng dịch thuật hiện có của ứng dụng.

Mục tiêu là cung cấp một giải pháp liền mạch để xử lý và dịch các tệp PDF "cứng đầu", nâng cao tính linh hoạt và tiện ích của bộ công cụ.

## 2. Đối tượng sử dụng

*   Người dùng hiện tại của Advanced Translation Suite.
*   Bất kỳ ai cần dịch tài liệu PDF mà không thể trích xuất văn bản trực tiếp một cách đáng tin cậy.
*   Dịch giả, nhà nghiên cứu, sinh viên, nhân viên văn phòng thường xuyên làm việc với tài liệu PDF đa ngôn ngữ.

## 3. Chức năng (Features)

### 3.1. Tải lên tệp PDF (F1)
*   **Mô tả:** Người dùng có thể tải lên một tệp PDF duy nhất thông qua giao diện web.
*   **Chi tiết:**
    *   Cung cấp một thành phần tải tệp (File Upload) rõ ràng trên giao diện.
    *   Giới hạn chỉ cho phép tải lên các tệp có phần mở rộng `.pdf`.
    *   (Tùy chọn) Có thể xem xét giới hạn kích thước tệp tối đa để tránh quá tải tài nguyên server (ví dụ: 50MB).

### 3.2. Lựa chọn Ngôn ngữ OCR (F2)
*   **Mô tả:** Người dùng có thể chọn ngôn ngữ chính có trong tệp PDF để tối ưu hóa độ chính xác của OCR.
*   **Chi tiết:**
    *   Cung cấp một danh sách thả xuống (Dropdown) chứa các ngôn ngữ được hỗ trợ bởi engine OCR (Tesseract).
    *   Danh sách nên bao gồm các ngôn ngữ phổ biến như Tiếng Anh, Tiếng Việt, Pháp, Đức, Tây Ban Nha, Trung giản thể/phồn thể, Nhật, Hàn,...
    *   Ngôn ngữ mặc định có thể là Tiếng Anh (`eng`).
    *   Lựa chọn này sẽ được sử dụng để chỉ định ngôn ngữ cho Tesseract khi xử lý.

### 3.3. Thực hiện Trích xuất Văn bản (F3)
*   **Mô tả:** Người dùng có thể bắt đầu quá trình OCR sau khi đã tải tệp lên và chọn ngôn ngữ.
*   **Chi tiết:**
    *   Cung cấp một nút bấm (Button) "Trích xuất Văn bản từ PDF" (hoặc tương tự).
    *   Khi nhấn nút, backend sẽ thực hiện các bước sau:
        1.  Nhận tệp PDF và ngôn ngữ OCR đã chọn.
        2.  (Backend) Sử dụng thư viện như `pdf2image` để chuyển đổi từng trang PDF thành hình ảnh.
        3.  (Backend) Sử dụng thư viện OCR (ví dụ: `pytesseract`) để xử lý các hình ảnh này với ngôn ngữ đã chọn.
        4.  (Backend) Ghép nối văn bản trích xuất từ các trang thành một chuỗi văn bản hoàn chỉnh.
    *   Hiển thị trạng thái xử lý cho người dùng (ví dụ: "Đang xử lý trang X/Y...", "Đang nhận dạng văn bản...").

### 3.4. Hiển thị Kết quả OCR (F4)
*   **Mô tả:** Văn bản được trích xuất từ PDF sẽ được hiển thị cho người dùng.
*   **Chi tiết:**
    *   Cung cấp một vùng văn bản (TextArea) chỉ đọc (read-only) để hiển thị kết quả OCR.
    *   Nội dung của TextArea này sẽ được cập nhật sau khi quá trình OCR hoàn tất.
    *   Nếu có lỗi xảy ra trong quá trình OCR (ví dụ: không đọc được file, lỗi chuyển đổi ảnh, lỗi Tesseract), hiển thị thông báo lỗi rõ ràng cho người dùng.

### 3.5. (Tùy chọn) Chuyển Văn bản sang Khu vực Dịch (F5)
*   **Mô tả:** Cung cấp cách thuận tiện để người dùng sử dụng văn bản OCR làm đầu vào cho chức năng dịch hiện có.
*   **Chi tiết:**
    *   Thêm một nút "Gửi tới ô Dịch" (hoặc tương tự) bên cạnh TextArea kết quả OCR.
    *   Khi nhấn nút này, nội dung từ TextArea OCR sẽ được sao chép vào TextArea nhập liệu chính của phần dịch thuật.

## 4. Giao diện Người dùng (UI) và Trải nghiệm Người dùng (UX)

*   **Tích hợp:** Các thành phần UI mới (File Upload, Dropdown, Button, TextArea) cần được tích hợp một cách hợp lý vào tab/khu vực phù hợp trong giao diện Gradio hiện tại, tránh làm giao diện trở nên lộn xộn. Có thể tạo một Tab/Section riêng cho "Xử lý PDF".
*   **Phản hồi:** Cung cấp phản hồi trực quan trong quá trình OCR (thông báo trạng thái, chỉ báo tải).
*   **Thông báo lỗi:** Hiển thị thông báo lỗi thân thiện và dễ hiểu nếu có sự cố xảy ra.
*   **Luồng làm việc:** Luồng làm việc nên trực quan: Tải file -> Chọn ngôn ngữ -> Nhấn nút -> Xem kết quả -> (Tùy chọn) Gửi đi dịch.

## 5. Yêu cầu Kỹ thuật

*   **Ngôn ngữ Backend:** Python
*   **Framework Web:** Gradio
*   **Thư viện OCR:**
    *   `pytesseract` (Wrapper cho Tesseract)
    *   `easyocr` (Một lựa chọn thay thế, có thể dễ cài đặt hơn trên một số hệ thống) - *Cần quyết định chọn 1* -> **Quyết định:** Sử dụng `pytesseract` để tận dụng engine Tesseract mạnh mẽ.
*   **Thư viện xử lý PDF:** `pdf2image` (Để chuyển PDF thành ảnh)
*   **Dependencies Hệ thống:**
    *   **Tesseract OCR Engine:** Cần được cài đặt trên hệ thống chạy backend. Bao gồm cả các gói ngôn ngữ cần thiết (ví dụ: `tesseract-ocr-eng`, `tesseract-ocr-vie`,...).
    *   **Poppler:** Dependency của `pdf2image` để xử lý PDF. Cần được cài đặt trên hệ thống.
*   **Quản lý Dependencies:** Cập nhật `requirements.txt` với các thư viện Python mới.
*   **Kiến trúc:** Logic OCR sẽ được thực thi hoàn toàn ở phía backend (server-side).

## 6. Tiêu chí thành công (Metrics - Tùy chọn)

*   Số lượt sử dụng chức năng OCR thành công.
*   Tỷ lệ lỗi trong quá trình OCR.
*   Phản hồi từ người dùng về tính dễ sử dụng và hiệu quả của chức năng mới.

## 7. Câu hỏi mở/Cần quyết định

*   Giới hạn kích thước tệp PDF tải lên là bao nhiêu? (Đề xuất: 50MB)
*   Xử lý như thế nào nếu PDF được bảo vệ bằng mật khẩu? (Hiện tại: Báo lỗi không thể xử lý).
*   Cần hỗ trợ chính xác những ngôn ngữ OCR nào trong danh sách thả xuống? (Bắt đầu với các ngôn ngữ trong `OCR_LANGUAGES` của `script.js` trước). 