from sshtunnel import SSHTunnelForwarder
import time
import os

# Нужно создать файл .pgpass c правами 600 в /home/user
# С содержимым hostname:port:database:username:password

POSTGRES_USER = "mematik"
DB = "kwork"
BACKUP_DIR = "."
NOW = round(time.time())
FILENAME = f"{DB}-{NOW}.backup"
PORT = 5432
SSH_TUNNEL_POSTGRES = {
    "ssh_address_or_host": ("192.168.181.128", 22),
    "ssh_username": "alex",
    "ssh_password": "123",
    "remote_bind_address": ("localhost", 5432),
    "local_bind_address": ("localhost", PORT)
}


def main():
    # server = SSHTunnelForwarder(**SSH_TUNNEL_POSTGRES)
    # server.start()
    os.system(f"pg_dump -h localhost -p {PORT} -U {POSTGRES_USER} -d {DB} > {BACKUP_DIR}/{FILENAME}")


if __name__ == "__main__":
    main()
