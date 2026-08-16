# Thiết kế kỹ thuật

## Kiến trúc

```text
Streamlit UI
    -> Input Validation
    -> Text Preprocessing & Synonym Expansion
    -> BM25 Retrieval
    -> Rule Matching
    -> Impact Analyzer
    -> BA Review
    -> SQLite / DOCX / XLSX
```

## Nguyên tắc

- Không gọi API ngoài.
- Không dùng LLM, embedding hoặc vector database.
- Seed data được lưu bằng JSON.
- Dữ liệu giao dịch và review được lưu bằng SQLite.
- UI và business logic được tách thành các module riêng.

## Phạm vi dữ liệu

- 5 module nghiệp vụ.
- 4 role.
- 8 User Story.
- 9 Business Rule.
- 3 SOP.
- 9 Test Case.
- 9 rule phân loại CR.
- 35 synonym mapping.
