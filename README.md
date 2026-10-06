# Lunari-like bot (học tập)

Bot Discord đa năng cơ bản: moderation, economy, fun. Dùng discord.py 2.x + slash command + SQLite.

## Chạy
1. Tạo bot ở https://discord.com/developers/applications, copy token.
2. Mời bot vào server với scope `bot` + `applications.commands`.
3. `copy .env.example .env` rồi điền `DISCORD_TOKEN` (và `DEV_GUILD_ID` nếu muốn lệnh cập nhật tức thì).
4. ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

## Cấu trúc
- `main.py`: khởi tạo bot, tự load cog, xử lý lỗi lệnh
- `db.py`: lớp SQLite (aiosqlite)
- `cogs/`: mỗi file là một nhóm lệnh, thêm file mới là tự được load

Thêm tính năng: copy `cogs/fun.py` làm mẫu.
