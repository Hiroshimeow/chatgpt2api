# FlareSolverr và Cloudflare

Khi ChatGPT web backend gặp Cloudflare challenge, có thể dùng FlareSolverr để xử lý challenge rồi retry request.

## Thành phần

- WARP: cải thiện route mạng.
- Privoxy: chuyển SOCKS5 sang HTTP.
- FlareSolverr: xử lý challenge.
- App: ChatGPT2API sử dụng proxy runtime khi gọi upstream.

## Khởi động

```bash
cp .env.example .env
docker compose -f docker-compose.warp.yml up -d --build
```

## Vận hành

- Nếu request bị chặn, thử refresh lại trạng thái proxy/challenge.
- Nếu vẫn lỗi, kiểm tra log của `flaresolverr`, `privoxy`, `warp-proxy` và `app`.
- Không retry vô hạn; cần backoff để tránh bị upstream đánh dấu lạm dụng.
