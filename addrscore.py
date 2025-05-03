"""
AddrScore: скоринговая оценка Bitcoin-адреса по его активности.
"""

import requests
import argparse
import time
from datetime import datetime

def get_address_data(address):
    url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}?transaction_details=true"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Ошибка при получении данных.")
    data = r.json()["data"][address]["address"]
    txs = r.json()["data"][address]["transactions"]
    return data, txs

def get_transaction_times(txs):
    times = []
    for txid in txs[:30]:
        url = f"https://api.blockchair.com/bitcoin/transactions?q=hash:{txid}"
        r = requests.get(url)
        if r.status_code == 200:
            try:
                t = r.json()["data"][0]["time"]
                times.append(int(time.mktime(datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timetuple())))
            except:
                continue
        time.sleep(0.1)
    return times

def score_address(data, tx_times):
    tx_count = data.get("transaction_count", 0)
    received = data.get("received", 0) / 1e8
    sent = data.get("sent", 0) / 1e8
    balance = data.get("balance", 0) / 1e8

    total_volume = received + sent
    avg_tx = total_volume / tx_count if tx_count else 0

    active_days = len(set(datetime.utcfromtimestamp(ts).date() for ts in tx_times))

    score = 0
    score += min(tx_count, 100) * 0.3
    score += min(avg_tx, 10) * 2
    score += min(active_days, 30) * 0.5
    if balance > 1:
        score += 5

    print("📊 Оценка активности:")
    print(f"🔹 Транзакций: {tx_count}")
    print(f"🔹 Объем (BTC): Получено {received:.4f}, Отправлено {sent:.4f}")
    print(f"🔹 Средний объем за транзакцию: {avg_tx:.4f} BTC")
    print(f"🔹 Активных дней: {active_days}")
    print(f"🔹 Остаток: {balance:.4f} BTC")
    print(f"
🏁 Итоговая репутация: {score:.2f} / 100")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AddrScore — скоринговая оценка BTC-адреса.")
    parser.add_argument("address", help="Bitcoin-адрес")
    args = parser.parse_args()
    data, txs = get_address_data(args.address)
    times = get_transaction_times(txs)
    score_address(data, times)
