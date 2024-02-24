import requests
import time
import os
from prometheus_client import start_http_server, Gauge, Info

BASE_URL = "https://api.qubic.li"

qubic_li_found_solutions = Gauge("qubic_li_found_solutions", "Number of found solutions")
#qubic_li_miner_name = Info("qubic_li_miner_name", "Name of the miner", labelnames=["alias"])
qubic_li_miner_currentIts = Gauge("qubic_li_miner_currentIts", "Current IT/s", ["alias"])
qubic_li_miner_solutionsFound = Gauge("qubic_li_miner_solutionsFound", "Number of solutions found", ["alias"])
qubic_li_miner_isActive = Gauge("qubic_li_miner_isActive", "Is the miner active 1 for true 0 for false", ["alias"])

def connect():
    USER = os.environ.get("USER")
    PASSWORD = os.environ.get("PASSWORD")

    payload = {"password": PASSWORD, "userName": USER, "twoFactorCode": ""}

    headers = {
        "authority": "api.qubic.li",
        "accept": "application/json",
        "accept-language": "fr-FR,fr;q=0.8",
        "content-type": "application/json-patch+json",
        "origin": "https://app.qubic.li",
        "referer": "https://app.qubic.li/",
    }

    return requests.post(
        BASE_URL + "/Auth/Login", headers=headers, json=payload
    ).json()["token"]


def find_metrics():
    token = connect()
    headers = {
        "authority": "api.qubic.li",
        "accept": "application/json",
        "accept-language": "fr-FR,fr;q=0.8",
        "authorization": f"Bearer {token}",
        "origin": "https://app.qubic.li",
        "referer": "https://app.qubic.li/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }

    response = requests.get(
        BASE_URL + "/My/Pool/f4535705-eeac-4c4f-9ddc-4c3a91b40b13/Performance",
        headers=headers,
    )

    print(response.json())
    qubic_li_found_solutions.set(response.json()["foundSolutions"])
    
    for miner in response.json()["miners"]:
        #qubic_li_miner_name.labels(alias=miner["alias"]).info(miner["alias"])
        qubic_li_miner_currentIts.labels(alias=miner["alias"]).set(miner["currentIts"])
        qubic_li_miner_solutionsFound.labels(alias=miner["alias"]).set(miner["solutionsFound"])
        qubic_li_miner_isActive.labels(alias=miner["alias"]).set(miner["isActive"])





if __name__ == "__main__":
    # Démarrer le serveur pour exposer les métriques à Prometheus sur le port 8000
    start_http_server(9000)
    print("Serveur exposant les métriques démarré sur le port 9000")

    while True:
        find_metrics()
        time.sleep(5)  # Attendre 5 secondes avant de trouver la prochaine solution
