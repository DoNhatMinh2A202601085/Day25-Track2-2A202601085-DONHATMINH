| Task ID | Task Description | Status | Evidence / Notes |
|---|---|---|---|
| TASK-01 | Kiểm tra môi trường, tạo dữ liệu tất định và chạy kiểm thử ban đầu | COMPLETED | `python data/generate.py` OK, `verify.py` 11/11 PASS, `pytest -q` 15/15 PASS |
| TASK-02 | Rà soát & phân tích 5 Missions (M1-M5), xuất dữ liệu ban đầu | COMPLETED | M1-M5 runs OK, `outputs/focus_export.csv` 50 rows, `outputs/savings.png` generated, baseline $27,133 -> $14,626 (46.1% saved) |
| TASK-03 | Triển khai 3 Phần mở rộng "Your Turn" (Ext 1, Ext 3, Ext 4/5) & unit tests | COMPLETED | Implemented `cache_is_worth_it`, advanced `recommend_tier` with GPU interrupt rates & duration, reasoning & carbon simulation; added `tests/test_pricing_extensions.py`; 19/19 tests PASS |
| TASK-04 | Hoàn thiện Báo cáo kỹ thuật `outputs/report.md` & Thuyết minh `outputs/writeup.md` | COMPLETED | Created comprehensive `outputs/report.md`, `outputs/writeup.md`, and root `writeup.md` with 6 detailed sections, oral check answers, and 100% data consistency |
| TASK-05 | Kiểm tra hồi quy toàn diện (`verify.py`, `pytest`) & đóng gói giao phẩm | COMPLETED | 11/11 verify checks PASS, 19/19 pytest tests PASS, outputs verified and complete |
