from locust import HttpUser, task, between
import random
import uuid

MERCHANTS = ['GROCERY', 'FUEL', 'TRAVEL', 'ONLINE', 'ATM', 'RESTAURANT']
COUNTRIES = ['IN', 'US', 'UK', 'DE', 'FR']

class FraudAnalyst(HttpUser):
    wait_time = between(0.5, 2)

    @task(10)
    def score_transaction(self):
        self.client.post("/api/transactions/score", json={
            "account_id": f"ACC{random.randint(1, 1000):04d}",
            "amount": round(random.uniform(100, 50000), 2),
            "merchant_category": random.choice(MERCHANTS),
            "country": random.choice(COUNTRIES),
            "device_id": f"DEV{random.randint(1, 100):07d}",
            "ip_address": f"{random.randint(1,255)}.{random.randint(1,255)}.0.1",
            "TransactionAmt": round(random.uniform(100, 50000), 2),
            "card4": random.choice(["visa", "mastercard"]),
            "card6": random.choice(["credit", "debit"]),
            "P_emaildomain": random.choice(["gmail.com", "yahoo.com", "outlook.com"]),
            "R_emaildomain": random.choice(["gmail.com", "yahoo.com"]),
            "addr1": round(random.uniform(100, 500), 1),
            "addr2": 87.0,
            "dist1": round(random.uniform(0, 100), 1),
            "C1": 1.0, "C2": 1.0, "C3": 0.0, "C4": 0.0,
            "C5": 0.0, "C6": 1.0, "C7": 0.0, "C8": 0.0,
            "C9": 1.0, "C10": 0.0,
            "V1": 1.0, "V2": 1.0, "V3": 1.0, "V4": 1.0, "V5": 1.0,
            "V6": 1.0, "V7": 1.0, "V8": 1.0, "V9": 1.0, "V10": 1.0,
        }, timeout=30)

    @task(3)
    def get_recent_transactions(self):
        self.client.get("/api/transactions/recent?limit=20")

    @task(1)
    def health_check(self):
        self.client.get("/health")