import json
import os
from random import randint
from time import sleep

import redis
import requests

if __name__ == "__main__":
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", 6379)
    redis_db = os.getenv("REDIS_DB", 0)
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    api_url = os.getenv("API_URL", "http://localhost/api/")

    print("Aguardando mensagens...")

    while True:
        mensagem = json.loads(r.blpop("sender")[1])
        # Simulando envio de e-mail...
        print("Enviando a mensagem:", mensagem["assunto"])
        sleep(randint(15, 45))

        requests.post(f"{api_url}sent/{mensagem['id']}")

        print("Mensagem", mensagem["assunto"], "enviada!")
