import random

from locust import HttpUser, between, constant, task

from constants import HOST


class Organisateur(HttpUser) :
    host=HOST
    wait_time = between(5,10)
    weight = 1

    def on_start(self):
        payload = {
            "username" : "orga@eventflow.test",
            "password" : "orga1234"
        } 

        res = self.client.post("/api/auth/token", data=payload)
        res.raise_for_status()

        content = res.json()

        tokenType : str = content["token_type"]
        token = content["access_token"]

        self.client.headers["Authorization"] = f"{tokenType.capitalize()} {token}"

        return super().on_start()

    @task(1)
    def consulter_le_summary(self) :
        with self.client.get("/api/admin/summary", catch_response=True) as res :

            if res.status_code != 200 :
                res.failure(f"Erreur de code de retour, attendu 200, recu {res.status_code}")
                return


            content = res.json()

            if content["published"] > content["events"]:
                res.failure("Le nombre d'event publiés est supérieur au total d'events") 
        
    @task(2)
    def consulter_les_events_admin(self):
        with self.client.get("/api/admin/events", catch_response=True) as res : 

            if res.status_code != 200 :
                res.failure(f"Erreur de code de retour, attendu 200, recu {res.status_code}")
                return


            events = res.json()

            if any(e["sold"] > e["capacity"] for e in events) :
                res.failure("Le nombre de ticket vendus est supérieur a la capcité d'au moins 1 event") 
