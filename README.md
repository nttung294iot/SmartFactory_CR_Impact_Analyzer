# SmartFactory Change Impact Analyzer

Prototype minh họa cho đề tài thực tập tốt nghiệp của **Nguyễn Thanh Tùng**.

## Mục tiêu

Ứng dụng hỗ trợ Business Analyst thực hiện một luồng đơn giản:

1. Tiếp nhận Change Request.
2. Chuẩn hóa nội dung và xác định từ khóa.
3. Tìm các tài liệu nghiệp vụ liên quan.
4. Đề xuất module và artefact cần rà soát.
5. Tạo câu hỏi làm rõ, rủi ro và yêu cầu dự thảo.
6. Cho phép BA chỉnh sửa, xác nhận và xuất báo cáo.

Prototype sử dụng dữ liệu giả lập và không phải sản phẩm chính thức của FPT Software.

## Phạm vi giao diện

Ứng dụng gồm 5 trang:

- **Dashboard**: tổng quan các Change Request.
- **New Change Request**: tạo, lưu nháp và phân tích yêu cầu.
- **Analysis Workspace**: rà soát kết quả, chỉnh sửa và xuất báo cáo.
- **Knowledge Base**: tra cứu artefact nghiệp vụ ở chế độ chỉ đọc.
- **History**: mở lại, phân tích lại, xuất hoặc xóa bản ghi.

## Công nghệ

- Python 3.11 hoặc phiên bản tương thích.
- Streamlit.
- SQLite.
- `rank-bm25` / `BM25Okapi`.
- `python-docx` và `openpyxl`.
- pytest.

Ứng dụng không sử dụng LLM, API bên ngoài, embedding hoặc vector database.

## Cài đặt nhanh trên Windows 11

1. Giải nén project vào một thư mục không chứa ký tự đặc biệt.
2. Chạy `setup.bat`.
3. Chờ quá trình tạo `.venv` và cài thư viện hoàn tất.
4. Chạy `run_app.bat`.
5. Trình duyệt mở tại `http://localhost:8501`.

Lần cài thư viện đầu tiên cần kết nối Internet. Sau khi cài xong, ứng dụng có thể chạy cục bộ mà không gửi dữ liệu ra ngoài.

## Chạy thủ công

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts\initialize_demo.py
streamlit run app.py
```

## Cấu trúc dự án

```text
SmartFactory_CR_Impact_Analyzer/
├── app.py                      # File khởi tạo và điều hướng Streamlit UI
├── config/                     # Cấu hình cài đặt và logging JSON
├── data/
│   ├── seed/                   # Dữ liệu mẫu JSON (KB, Rules, Synonyms, CRs)
│   └── exports/                # Thư mục chứa báo cáo xuất .docx / .xlsx
├── docs/                       # Tài liệu kỹ thuật, hướng dẫn sử dụng, data dictionary
├── sample_outputs/             # File báo cáo mẫu minh họa
├── scripts/                    # Utility scripts (khởi tạo, reset DB, smoke test, evaluation)
├── src/                        # Core backend logic (BM25, Rule Engine, Database, Exporter...)
├── tests/                      # Automated pytest suite (41 test cases)
├── ui/                         # CSS styling và các UI components
└── views/                      # Các trang giao diện Streamlit (Dashboard, Workspace...)
```

## Chạy kiểm thử

```bat
.venv\Scripts\activate
pytest -q
python scripts\smoke_test.py
```

## Dữ liệu demo

- `data/seed/knowledge_base.json`: 38 artefact (5 module, 4 role, 8 user story, 9 business rule, 3 SOP, 9 test case).
- `data/seed/rules.json`: 9 rule.
- `data/seed/synonyms.json`: 35 mapping.
- `data/seed/sample_change_requests.json`: 5 CR mẫu.
- `data/app.db`: SQLite có dữ liệu lịch sử minh họa.

## Export

- Báo cáo Impact Analysis: `.docx`.
- Requirement Traceability Matrix: `.xlsx`.
- File được tạo tại `data/exports/`.
- Các ví dụ có sẵn tại `sample_outputs/`.

## Reset dữ liệu

Chạy `reset_demo_data.bat`. Script sẽ sao lưu database hiện tại trước khi tạo lại dữ liệu seed.

## Hạn chế

- Dữ liệu không phản ánh hệ thống hoặc khách hàng thật.
- Kết quả chỉ là gợi ý ban đầu, không tự động phê duyệt Change Request.
- Khả năng xử lý yêu cầu mới phụ thuộc vào Knowledge Base, synonym và rule đã cấu hình.
- Business Analyst vẫn là người xác nhận phạm vi và nội dung cuối cùng.
