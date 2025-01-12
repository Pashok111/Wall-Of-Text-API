# Wall Of Text API

You can check this API at https://pashok11.tw1.su/apis/wall_of_text/docs

## How to use
(For now tested only on Linux, Python 3.11.1 and Python 3.12.4)

Rename `config.toml.example` to `config.toml` and edit it. Then you can run `./start.sh` (or `./dev_start.sh` for development) or any other common way to run FastAPI app (like `uvicorn main:app --host 127.0.0.1 --port 8001`).

**Note**: `main_api_address` and `main_address` in `config.toml` are optional and if not specified - will be set to `/api` and `` (empty) respectively.

**Note**: `./start.sh` and `./dev_start.sh` are not supported on other platforms than Linux.

### Full README coming soon.