# CHANGELOG

Nhật ký thay đổi được Việt hóa cho fork này.

## Hiện tại

- Hỗ trợ Chat Completions, Responses shim, image generation/edit, search, PPT/PSD task và quản lý account pool.
- Đã thêm quy trình làm việc qua `todo.md`, `plan.md`, `done.md`.
- Đã thêm GPT backend/session pool để tái sử dụng session tối đa 10 lease/call trước khi rotate.
- Cần tiếp tục theo dõi vấn đề upstream auto-route text model về `gpt-5-3-mini` dù client yêu cầu `gpt-5-5`.

## Quy tắc cập nhật

- Khi đồng bộ upstream, ghi rõ commit nguồn, phạm vi thay đổi, rủi ro conflict và kết quả test.
- Không ghi dữ liệu runtime hoặc thông tin truy cập cá nhân vào changelog.
