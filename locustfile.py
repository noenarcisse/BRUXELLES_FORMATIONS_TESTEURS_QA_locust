from locust import HttpUser, task, between, constant
import random

keyword_list = ["jazz", "electro", "QA", "cloud", "les schtroumpfs"]

# PascalCase pour le nom des classes
class Visiteur(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 3)
    weight = 3

    def on_start(self):
        response = self.client.get("/api/events", name="/api/events [init]")
        events_list = response.json()

        self.events_id = [event["id"] for event in events_list]

        self.events_city= list({event["city"] for event in events_list})

        # tests de fail volontaires
        self.events_id.append(9999999)
        self.events_city.append("Atlantis")
        
        return super().on_start()
    
    @task(2)
    def seek_city(self):
        random_city = random.choice(self.events_city)
        with self.client.get(
            "/api/events", 
            params={"city": random_city}, 
            name="/api/events?city=[random_city]", 
            catch_response=True) as res :

            if res.status_code != 200 :
                res.failure(f"HTTP status code failed: exp[200], seen[{res.status_code}]")
                return

            events = res.json()

            if len(events) <= 0 :
                res.failure(f"No events found for the city {random_city}")
                return

            if any(e["city"] != random_city for e in events) :
                res.failure(f"City found doesnt match: exp[{random_city}]")



    @task(2)
    def seek_keyword(self):
        random_event = random.choice(keyword_list)
        with self.client.get("/api/events", params={"q": random_event}, name="/api/events?q=[random_event]", catch_response=True) as res :
            if res.status_code != 200 :
                res.failure(f"HTTP status code failed: exp[200], seen[{res.status_code}]")
            events = res.json()
            if len(events) <= 0 :
                res.failure(f"No events found for the search {random_event}")
                return

            notmatching = [e for e in events if random_event.lower() not in events[0]["title"].lower()]
            if len(notmatching) > 0 : res.failure("One or more elements do not match the search terms")

    @task(3)
    def consulter_catalogue(self):
        self.client.get("/api/events")

    @task(5)
    def consulter_detail(self):
        event_id = random.choice(self.events_id)
        with self.client.get(f"/api/events/{event_id}", name="/api/events/[id]", catch_response=True) as res :
            if res.status_code != 200 : 
                res.failure(f"HTTP code : {res.status_code}")
                return
            event = res.json()

            if event["id"] != event_id :
                res.failure(f"Mauvais event on veut le {event_id}")
            elif not event["categories"] :
                res.failure("Y'a pas de categories ici, c'est un array vide mon gars")
                         


class Veilleur(HttpUser):
    host = "http://localhost:8000"
    wait_time = constant(5)

    @task
    def veiller(self):
        self.client.get("/api/health")

class ClientConnecte(HttpUser) :
    host = "http://localhost:8000"
    wait_time = between(2,5)
    weight = 1
    
    def on_start(self):

        data = {
            "username" : "client@eventflow.test",
            "password" : "client1234"
        }
        res = self.client.post(f"{self.host}/api/auth/token", data=data)
        res.raise_for_status()

        content = res.json()
        tokenType : str = content["token_type"]
        token : str = content["access_token"]

        self.client.headers["Authorization"] = f"{tokenType.capitalize()} {token}"
        return super().on_start()

# Corr exo2
""" 1
10 utilisateurs => RPS attendu ? (10 * 1 / (0.1 + 2)) => 10 / 2.1
=== Plus ou moins RPS de 5
"""

"""2
1 Veilleur => (1 * 1) / (0.01 + 5) => 1 / 5 ===> 0.2 RPS
Pour 2 RPS => 10 veilleurs
"""

"""3
5 utilisateurs à 0 wait_time => ((5 * 1) / (0.01 + 0))
=> RPS attendu = 500 RPS
"""
