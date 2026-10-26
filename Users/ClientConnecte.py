import random

from locust import HttpUser, between, constant, task

from constants import HOST

class ClientConnecte(HttpUser) :
    host = HOST
    wait_time = between(2,5)
    weight = 1
    
    def on_start(self):

        data = {
            "username" : "client@eventflow.test",
            "password" : "client1234"
        }
        res = self.client.post("/api/auth/token", data=data)
        res.raise_for_status()

        content = res.json()
        tokenType : str = content["token_type"]
        token : str = content["access_token"]

        self.client.headers["Authorization"] = f"{tokenType.capitalize()} {token}"
        return super().on_start()

    @task(3)
    def voir_mes_commandes(self):
        self.client.get("/api/orders/me")

    @task(4)
    def voir_mon_profil(self):
        self.client.get("/api/auth/me")

    @task(1)
    def consulter_le_summary(self) :
        with self.client.get("/api/admin/summary", catch_response=True) as res :

            if res.status_code != 403 :
                res.failure(f"Erreur de code de retour, attendu 403, recu {res.status_code}")
            else : 
                res.success()
