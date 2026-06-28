<h1 align="center">ChatGPT2API</h1>

<p align="center">ChatGPT2API là adapter reverse cho ChatGPT web, cung cấp API tương thích OpenAI cho chat, Responses, tạo ảnh, chỉnh sửa ảnh, search, quản lý account pool, log, backup, proxy và triển khai tự host bằng Docker.</p>

> [!WARNING]
> Dự án này chỉ dành cho học tập cá nhân, nghiên cứu kỹ thuật và trao đổi phi thương mại. Upstream ChatGPT web có thể thay đổi bất kỳ lúc nào; người dùng tự chịu rủi ro khi triển khai.

## Cài đặt nhanh

### Docker

```bash
git clone git@github.com:Hiroshimeow/chatgpt2api.git
cd chatgpt2api
docker compose up -d
```

- Web UI: `http://localhost:3000`
- API base: `http://localhost:3000/v1`
- Dữ liệu runtime: `./data`

### WARP / FlareSolverr

```bash
cp .env.example .env
docker compose -f docker-compose.warp.yml up -d --build
```

Các service chính:

- `warp-proxy`: SOCKS5 proxy qua WARP.
- `privoxy`: chuyển SOCKS5 sang HTTP proxy.
- `flaresolverr`: xử lý Cloudflare challenge.
- `init-config`: ghi cấu hình proxy runtime ban đầu.
- `app`: chạy ChatGPT2API.

### Chạy local

Backend:

```bash
git clone git@github.com:Hiroshimeow/chatgpt2api.git
cd chatgpt2api
uv sync
uv run main.py
```

Frontend:

```bash
cd chatgpt2api/web
bun install
bun run dev
```

Cập nhật Docker image:

```bash
docker pull ghcr.io/basketikun/chatgpt2api:latest
docker-compose down
docker-compose up -d
```

## Lưu trữ

Chọn backend bằng `STORAGE_BACKEND`:

- `json` - lưu JSON local, mặc định.
- `sqlite` - lưu bằng SQLite.
- `postgres` - lưu bằng PostgreSQL, cần `DATABASE_URL`.
- `git` - lưu qua Git repository, cần `Git remote URL` và `Git credential`.

Ví dụ PostgreSQL:

```yaml
environment:
  - STORAGE_BACKEND=postgres
  - DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Tính năng

- `POST /v1/chat/completions` - Chat Completions tương thích OpenAI.
- `POST /v1/responses` - Responses API shim.
- `GET /v1/models` - danh sách model.
- `POST /v1/images/generations` - tạo ảnh.
- `POST /v1/images/edits` - chỉnh sửa ảnh.
- `POST /v1/search` - search adapter.
- `POST /v1/ppt/generations` - tạo PPT qua task nội bộ.
- `POST /v1/psd/generations` - tạo PSD qua task nội bộ.

Model thường gặp: `auto`, `gpt-5`, `gpt-5-1`, `gpt-5-2`, `gpt-5-3`, `gpt-5-3-mini`, `gpt-5-mini`, `gpt-5-5`, `gpt-image-2`, `codex-gpt-image-2`.

Lưu ý: text model trên ChatGPT web có thể bị upstream auto-route. Gửi `gpt-5-5` không bảo đảm backend thật sự chạy 5.5.

## Web UI

- Quản lý account pool.
- Import tài khoản bằng nhiều phương thức.
- Tạo ảnh và quản lý lịch sử ảnh.
- Xem log request/API.
- Cấu hình proxy, FlareSolverr, backup, user key và third-party app.
- Debug chat, search, image, PPT, PSD và editable file task.

## Quy trình repo

- Dùng `origin` cho fork cá nhân.
- Dùng `upstream` cho repo gốc.
- Trước khi pull upstream, kiểm tra diff và rủi ro conflict.
- Khi thêm task mới, cập nhật `todo.md`, `plan.md`, `done.md`.

## License

Xem license của upstream. Người dùng tự chịu trách nhiệm khi triển khai và sử dụng.


