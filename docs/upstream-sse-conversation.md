# Upstream SSE conversation

ChatGPT2API gọi ChatGPT web backend bằng SSE stream.

## Luồng tổng quát

1. Bootstrap trang ChatGPT để lấy thông tin client/build và dữ liệu challenge nếu cần.
2. Chuẩn bị chat requirements.
3. Tạo payload conversation.
4. Gửi request stream tới upstream conversation endpoint.
5. Parse SSE event và chuyển thành response tương thích OpenAI.

## Lưu ý

- Upstream có thể đổi format bất kỳ lúc nào.
- Model slug gửi lên không phải bảo đảm hard routing.
- Cần tránh tạo session mới cho mọi request; fork này đã thêm backend pool với giới hạn 10 lease/session.
