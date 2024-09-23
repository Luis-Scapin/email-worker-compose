import json
import os

import psycopg2
import redis
from bottle import Bottle, request


class Sender(Bottle):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.route("/send", method="POST", callback=self.send)
        self.route("/sent/<id>", method="POST", callback=self.sent)

        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", 6379)
        redis_db = os.getenv("REDIS_DB", 0)
        self.fila = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

        db_host = os.getenv("DB_HOST", "localhost")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASS", "postgres")
        db_name = os.getenv("DB_NAME", "sender")

        dsn = f"dbname={db_name} user={db_user} password={db_password} host={db_host}"

        self.conn = psycopg2.connect(dsn)

    def registrar_mensagem(self, assunto, mensagem):
        SQL = (
            "INSERT INTO emails (assunto, mensagem, status) "
            "VALUES (%s, %s, %s) "
            "RETURNING id"
        )

        cursor = self.conn.cursor()
        cursor.execute(SQL, (assunto, mensagem, "PENDENTE"))
        msg_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()

        msg = {
            "id": msg_id,
            "assunto": assunto,
            "mensagem": mensagem,
        }
        self.fila.rpush("sender", json.dumps(msg))

        print("Mensagem registrada!")

    def sent(self, id):
        SQL = "UPDATE emails SET status='SUCESSO' WHERE id=%s"
        cursor = self.conn.cursor()
        cursor.execute(SQL, (id,))
        self.conn.commit()
        cursor.close()
        print(f"Mensagem {id} atualizada!")

    def send(self):
        assunto = request.forms.get("assunto")
        mensagem = request.forms.get("mensagem")

        self.registrar_mensagem(assunto, mensagem)

        return "Mensagem enfileirada! Assunto: {} Mensagem: {}".format(
            assunto, mensagem
        )


if __name__ == "__main__":
    sender = Sender()
    sender.run(host="0.0.0.0", port=8080, debug=True)
