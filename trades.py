import csv
import os
from datetime import date

FILE_NAME = "trades.csv"
commission_rate = 0.0005

DAY_WARNING_LOSS = -250
DAY_WARNING_PROFIT = 400
DAY_HARD_LOSS = -500
DAY_HARD_PROFIT = 800


def load_data():
    positions = {}
    today_pnl = 0
    today = str(date.today())

    if not os.path.exists(FILE_NAME):
        return positions, today_pnl

    with open(FILE_NAME, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            inst = row["instrument"]
            action = row["action"]
            side = row["side"]
            qnt = float(row["quantity"])
            price = float(row["price"])
            pnl = float(row["pnl"])
            trade_date = row["date"]

            if inst not in positions:
                positions[inst] = {
                    "long_qty": 0,
                    "long_value": 0,
                    "short_qty": 0,
                    "short_value": 0
                }

            if action == "buy" and side == "long":
                positions[inst]["long_qty"] += qnt
                positions[inst]["long_value"] += qnt * price

            elif action == "sell" and side == "long":
                avg = positions[inst]["long_value"] / positions[inst]["long_qty"]
                positions[inst]["long_qty"] -= qnt
                positions[inst]["long_value"] -= avg * qnt

            elif action == "sell" and side == "short":
                positions[inst]["short_qty"] += qnt
                positions[inst]["short_value"] += qnt * price

            elif action == "buy" and side == "short":
                avg = positions[inst]["short_value"] / positions[inst]["short_qty"]
                positions[inst]["short_qty"] -= qnt
                positions[inst]["short_value"] -= avg * qnt

            if trade_date == today:
                today_pnl += pnl

    return positions, today_pnl


def save_trade(data):
    file_exists = os.path.exists(FILE_NAME)

    with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "date", "instrument", "action", "side",
            "quantity", "price", "commission", "pnl"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)


def show_stats():
    if not os.path.exists(FILE_NAME):
        print("Нет данных.")
        return

    stats = {}

    with open(FILE_NAME, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            trade_date = row["date"]
            pnl = float(row["pnl"])

            if trade_date not in stats:
                stats[trade_date] = 0

            stats[trade_date] += pnl

    total = 0
    print("\nСТАТИСТИКА ПО ДНЯМ:\n")

    for d in sorted(stats.keys()):
        day_pnl = stats[d]
        total += day_pnl
        sign = "+" if day_pnl >= 0 else ""
        print(f"{d}  {sign}{day_pnl:.2f}")

    print("-" * 20)
    sign = "+" if total >= 0 else ""
    print(f"ИТОГО: {sign}{total:.2f}\n")
    
positions, today_pnl = load_data()
today = str(date.today())

print("\nТЕКУЩИЕ ПОЗИЦИИ:")
for inst, data in positions.items():
    if data["long_qty"] > 0:
        avg = data["long_value"] / data["long_qty"]
        print(f"{inst} LONG: {data['long_qty']} | средняя {avg:.2f}")
    if data["short_qty"] > 0:
        avg = data["short_value"] / data["short_qty"]
        print(f"{inst} SHORT: {data['short_qty']} | средняя {avg:.2f}")

print(f"\nPnL за сегодня: {today_pnl:.2f}")


while True:

    if today_pnl <= DAY_WARNING_LOSS:
        print("⚠ Превышен дневной убыток!")

    if today_pnl >= DAY_WARNING_PROFIT:
        print("⚠ Превышена дневная прибыль!")

    action = input("\nbuy / sell / info / exit: ").lower()

    if action == "info":
        show_stats()
        continue

    if action == "exit":
        break

    side = input("long / short: ").lower()
    instrument = input("Инструмент: ").upper()
    qnt = float(input("Количество: "))
    price = float(input("Цена: "))

    commission = qnt * price * commission_rate
    pnl = -commission

    if instrument not in positions:
        positions[instrument] = {
            "long_qty": 0,
            "long_value": 0,
            "short_qty": 0,
            "short_value": 0
        }

    # LONG
    if action == "buy" and side == "long":
        positions[instrument]["long_qty"] += qnt
        positions[instrument]["long_value"] += qnt * price

    elif action == "sell" and side == "long":
        avg = positions[instrument]["long_value"] / positions[instrument]["long_qty"]
        profit = qnt * (price - avg)
        positions[instrument]["long_qty"] -= qnt
        positions[instrument]["long_value"] -= avg * qnt
        pnl += profit
        print(f"PnL: {pnl:.2f}")

    # SHORT
    elif action == "sell" and side == "short":
        positions[instrument]["short_qty"] += qnt
        positions[instrument]["short_value"] += qnt * price

    elif action == "buy" and side == "short":
        avg = positions[instrument]["short_value"] / positions[instrument]["short_qty"]
        profit = qnt * (avg - price)
        positions[instrument]["short_qty"] -= qnt
        positions[instrument]["short_value"] -= avg * qnt
        pnl += profit
        print(f"PnL: {pnl:.2f}")

    else:
        print("Ошибка ввода")
        continue

    
    today_pnl += pnl

    trade_data = {
        "date": today,
        "instrument": instrument,
        "action": action,
        "side": side,
        "quantity": qnt,
        "price": price,
        "commission": commission,
        "pnl": pnl
    }

    save_trade(trade_data)

    if today_pnl <= DAY_HARD_LOSS:
        print("💀 Жёсткий лимит убытка. Программа закрыта.")
        break

    if today_pnl >= DAY_HARD_PROFIT:
        print("💀 Жёсткий лимит прибыли. Программа закрыта.")
        break

print("\nСессия завершена.")