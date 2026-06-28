# Trạng thái tính năng

File này đã được Việt hóa cho fork.

## Tương thích API

- Chat Completions: đã có compatibility layer.
- Responses: đã có shim, chưa phải runtime Responses đầy đủ.
- Models: liệt kê model upstream và model ảnh động theo account pool.
- Images: hỗ trợ generation/edit qua reverse path của ChatGPT web.
- Search: hỗ trợ qua adapter nội bộ.
- MCP/tools: chưa hỗ trợ như runtime `@app` của ChatGPT web. Tool chưa được implement sẽ bị guard.

## Vận hành

- Account pool: đã có.
- Backend session pool: đã có; rotate sau 10 high-level lease.
- Rate limiter/circuit breaker: chưa làm.
- Chẩn đoán model fallback: cần làm.
