# Wall Of Text API
Little project for uploading and reading some texts and comments for them.

You can check this API at https://pashok11.tw1.su/apis/wall_of_text/docs
## How to use
(For now tested only on Linux and Docker, Python 3.11.1, 3.12.4, 3.13.1)

**Note**: if Docker doesn't working, try this:
- `systemctl start docker.socket` - for desktop
- `systemctl start docker.service` - for server

You can several ways to run:
- Docker Compose:
    - Copy `.env.example` to `.env` and edit it.
    - `docker compose up` - start Docker Compose. You can add `-d` for run start it in background.
    - `docker compose down` - stop Docker Compose. You can add `--rmi local` for delete related to compose images (only created by compose, not by pulling from docker hub), containers and networks.
- Docker:
    - **Optional**: Copy `.env.example` to `.env` and edit it.
    - `docker volume create wall-of-text-api_wall_of_text` - create a volume for the database (name it like this for simple migrate to Docker Compose).
    - `docker build -t wall_of_text .` for building an image.
    - `docker run -p 8000:8000 --mount type=volume,src=wall-of-text-api_wall_of_text,target=/app/db_n_logs --name wall_of_text_container wall_of_text` - run a container with name `wall_of_text_container`, with publishing `8000` port and mounting a volume `wall-of-text-api_wall_of_text` to the `/app/db_n_logs` directory in a container. You can add `-d` for run it in background, `--rm` for deleting container when it exits and `-e HOST=0.0.0.0 -e PORT=8000` for setting environment variables for a container (especially if you don't do anything with `.env` file).
    - Stop container with `docker stop <CONTAINER_NAME>` for just stop a container, `docker rm -f <CONTAINER_NAME>` for stop and delete a container or just press `Ctrl+C` if it in foreground to stop it.
- Bash scripts:
    - **Optional**: Copy `.env.example` to `.env` and edit it.
    - Set `HOST` and `PORT` environment variables to what you want (`HOST=0.0.0.0 && PORT=8000`) or edit `./start.sh` (or `./start_dev.sh`).
    - Run `./start.sh` (or `./start_dev.sh` for development). If you can't run it - make script executable (`chmod +x start.sh`).
- or any other common way to run FastAPI app, like `fastapi run main.py --host 0.0.0.0 --port 8000` or `uvicorn main:app --host 0.0.0.0 --port 8000`.