import logging

from locust import HttpUser, constant, events, task
from locust.env import Environment

from Users.ClientConnecte import ClientConnecte
from Users.Organisateur import Organisateur
from Users.Visiteur import Visiteur


class Veilleur(HttpUser):
    host = "http://localhost:8000"
    wait_time = constant(5)

    @task
    def veiller(self):
        self.client.get("/api/health")


threshold = 300

@events.test_stop.addlistener
def eval_result(environment : Environment, **kwargs) :
    p95 = environment.stats.total.get_response_time_percentile(.95)
    logging.info("Bilan p95 %s", p95)

    if p95 > threshold :
        logging.info("Condition non respectée")
        environment.process_exit_code = 1
    else : 
        environment.process_exit_code = 0


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
