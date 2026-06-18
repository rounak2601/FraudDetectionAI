import requests
import random
import time

url = 'http://localhost:8000/api/transactions/score'

burner_emails = ['mailinator.com', 'guerrillamail.com', 'tempmail.com']
normal_emails = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']

def normal_tx(acc_id):
    return {
        'account_id': acc_id,
        'amount': round(random.uniform(10, 500), 2),
        'merchant_category': 'GROCERY',
        'country': 'IN',
        'device_id': f'DEV{random.randint(1,50):07d}',
        'ip_address': '192.168.1.1',
        'TransactionAmt': round(random.uniform(10, 500), 2),
        'card4': 'visa',
        'card6': 'credit',
        'P_emaildomain': random.choice(normal_emails),
        'R_emaildomain': random.choice(normal_emails),
        'addr1': random.uniform(100, 500),
        'addr2': 87.0,
        'dist1': random.uniform(0, 10),
        'C1': 1.0, 'C2': 1.0, 'C3': 0.0, 'C4': 0.0,
        'C5': 0.0, 'C6': 1.0, 'C7': 0.0, 'C8': 0.0,
        'C9': 1.0, 'C10': 0.0,
        'V1': 1.0, 'V2': 1.0, 'V3': 1.0, 'V4': 1.0, 'V5': 1.0,
        'V6': 1.0, 'V7': 1.0, 'V8': 1.0, 'V9': 1.0, 'V10': 1.0,
    }

def suspicious_tx(acc_id):
    return {
        'account_id': acc_id,
        'amount': round(random.uniform(8000, 80000), 2),
        'merchant_category': random.choice(['ATM', 'ONLINE', 'TRAVEL']),
        'country': random.choice(['NG', 'CN']),
        'device_id': f'DEV{random.randint(1,50):07d}',
        'ip_address': f'41.{random.randint(1,255)}.1.1',
        'TransactionAmt': round(random.uniform(8000, 80000), 2),
        'card4': 'mastercard',
        'card6': 'debit',
        'P_emaildomain': random.choice(burner_emails),
        'R_emaildomain': random.choice(burner_emails),
        'addr1': -999,
        'addr2': -999,
        'dist1': random.uniform(500, 5000),
        'C1': 5.0, 'C2': 8.0, 'C3': 3.0, 'C4': 2.0,
        'C5': 1.0, 'C6': 0.0, 'C7': 3.0, 'C8': 2.0,
        'C9': 0.0, 'C10': 2.0,
        'V1': 0.0, 'V2': 0.0, 'V3': 0.0, 'V4': 0.0, 'V5': 0.0,
        'V6': 0.0, 'V7': 0.0, 'V8': 0.0, 'V9': 0.0, 'V10': 0.0,
    }

def medium_tx(acc_id):
    return {
        'account_id': acc_id,
        'amount': round(random.uniform(1000, 8000), 2),
        'merchant_category': random.choice(['ONLINE', 'TRAVEL']),
        'country': random.choice(['DE', 'FR', 'SG']),
        'device_id': f'DEV{random.randint(1,50):07d}',
        'ip_address': '85.214.1.1',
        'TransactionAmt': round(random.uniform(1000, 8000), 2),
        'card4': 'visa',
        'card6': 'debit',
        'P_emaildomain': random.choice(normal_emails),
        'R_emaildomain': random.choice(normal_emails),
        'addr1': random.uniform(200, 400),
        'addr2': 87.0,
        'dist1': random.uniform(50, 200),
        'C1': 2.0, 'C2': 3.0, 'C3': 1.0, 'C4': 0.0,
        'C5': 0.0, 'C6': 1.0, 'C7': 1.0, 'C8': 0.0,
        'C9': 1.0, 'C10': 0.0,
        'V1': 1.0, 'V2': 0.0, 'V3': 1.0, 'V4': 0.0, 'V5': 1.0,
        'V6': 0.0, 'V7': 1.0, 'V8': 0.0, 'V9': 1.0, 'V10': 0.0,
    }

scenarios = []

# 25 normal transactions
for i in range(25):
    scenarios.append(normal_tx(f'ACC{random.randint(100,300):04d}'))

# 15 medium risk
for i in range(15):
    scenarios.append(medium_tx(f'ACC{random.randint(300,400):04d}'))

# 10 suspicious/high risk
for i in range(10):
    scenarios.append(suspicious_tx(f'ACC{random.randint(400,500):04d}'))

random.shuffle(scenarios)

print(f'Sending {len(scenarios)} transactions...')
for i, data in enumerate(scenarios):
    try:
        r = requests.post(url, json=data, timeout=60)
        result = r.json()
        score = result.get('fraud_probability', 0)
        risk = result.get('risk_level', 'N/A')
        print(f'  [{i+1}/{len(scenarios)}] acc={data["account_id"]} amt={data["TransactionAmt"]} score={score:.2f} risk={risk}')
    except Exception as e:
        print(f'  [{i+1}] Error: {e}')
    time.sleep(0.3)

print('Done! Refresh the dashboard.')