import json
import os
from datetime import datetime, date
import matplotlib.pyplot as plt


# ---------- Класс, описывающий один расход ----------
class Expense:
    """Простой объект расхода: сумма, категория, дата."""
    def __init__(self, amount: float, category: str, expense_date: date):
        self.amount = amount           # сумма
        self.category = category       # категория
        self.date = expense_date       # дата (объект date)

    def __str__(self):
        return f"{self.date} | {self.category:15s} | {self.amount:8.2f}"


# ---------- Менеджер всех расходов ----------
class ExpenseManager:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = []             # список объектов Expense
        self.load()

    # --- Загрузка из JSON ---
    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                raw_data = json.load(f)               # список словарей
            self.expenses = []
            for item in raw_data:
                # Превращаем словарь обратно в объект Expense
                dt = datetime.strptime(item["date"], "%Y-%m-%d").date()
                exp = Expense(item["amount"], item["category"], dt)
                self.expenses.append(exp)
            print(f"Загружено расходов: {len(self.expenses)}")
        else:
            print("Файл данных не найден, начинаем с пустого списка.")

    # --- Сохранение в JSON ---
    def save(self):
        data_to_save = []
        for exp in self.expenses:
            data_to_save.append({
                "amount": exp.amount,
                "category": exp.category,
                "date": exp.date.isoformat()   # дата в виде строки
            })
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        print(f"Данные сохранены в {self.filename}")

    # --- Добавление нового расхода ---
    def add(self, amount, category, expense_date):
        new_expense = Expense(amount, category, expense_date)
        self.expenses.append(new_expense)
        print("Расход добавлен.")

    # --- Удаление расхода по индексу ---
    def delete(self, index):
        if 0 <= index < len(self.expenses):
            removed = self.expenses.pop(index)
            print(f"Удалён: {removed}")
        else:
            print("Ошибка: неверный индекс.")

    # --- Вывод всех расходов (или переданного списка) ---
    def show(self, expense_list=None):
        if expense_list is None:
            expense_list = self.expenses
        if not expense_list:
            print("Список расходов пуст.")
            return
        print(f"{'№':<4} {'Дата':<12} {'Категория':<17} {'Сумма':>8}")
        print("-" * 45)
        for i, exp in enumerate(expense_list):
            print(f"{i:<4} {exp}")
        print("-" * 45)

    # --- Фильтр по категории ---
    def filter_by_category(self, category):
        result = []
        for exp in self.expenses:
            if exp.category.lower() == category.lower():
                result.append(exp)
        return result

    # --- Фильтр по периоду (включая границы) ---
    def filter_by_period(self, start, end):
        result = []
        for exp in self.expenses:
            if start <= exp.date <= end:
                result.append(exp)
        return result

    # --- Общая сумма за период ---
    def total_in_period(self, start, end):
        total = 0.0
        for exp in self.filter_by_period(start, end):
            total += exp.amount
        return total

    # --- Построение столбчатой диаграммы по категориям ---
    def plot_categories(self):
        if not self.expenses:
            print("Нет данных для графика.")
            return

        # Суммируем суммы по каждой категории
        sums = {}
        for exp in self.expenses:
            if exp.category not in sums:
                sums[exp.category] = 0.0
            sums[exp.category] += exp.amount

        categories = list(sums.keys())
        amounts = list(sums.values())

        plt.figure(figsize=(8, 5))
        bars = plt.bar(categories, amounts, color='skyblue')
        plt.xlabel("Категория")
        plt.ylabel("Общая сумма")
        plt.title("Расходы по категориям")
        plt.xticks(rotation=45, ha='right')

        for bar, val in zip(bars, amounts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     f"{val:.2f}", ha='center', va='bottom')

        plt.tight_layout()
        plt.show()


# ---------- Вспомогательные функции ввода с проверками ----------
def get_positive_float(message):
    """Запрашивает положительное число."""
    while True:
        try:
            value = float(input(message).replace(',', '.'))
            if value <= 0:
                print("Сумма должна быть больше нуля!")
                continue
            return value
        except ValueError:
            print("Ошибка: нужно ввести число.")

def get_date(message):
    """Запрашивает дату в формате ГГГГ-ММ-ДД."""
    while True:
        raw = input(message + " (ГГГГ-ММ-ДД): ").strip()
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("Неверный формат. Используйте ГГГГ-ММ-ДД, например 2025-04-01.")

def get_nonempty(message):
    """Запрашивает непустую строку."""
    while True:
        s = input(message).strip()
        if s:
            return s
        print("Поле не может быть пустым.")


# ---------- Главное меню ----------
def main():
    manager = ExpenseManager("expenses.json")

    while True:
        print("\n" + "=" * 30)
        print("EXPENSE CHART")
        print("=" * 30)
        print("1. Показать все расходы")
        print("2. Добавить расход")
        print("3. Удалить расход")
        print("4. Фильтр по категории")
        print("5. Фильтр по периоду")
        print("6. Показать график")
        print("0. Выход с сохранением")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            manager.show()

        elif choice == "2":
            amount = get_positive_float("Введите сумму расхода: ")
            cat = get_nonempty("Введите категорию: ")
            d = get_date("Введите дату расхода")
            manager.add(amount, cat, d)

        elif choice == "3":
            manager.show()
            if not manager.expenses:
                continue
            try:
                idx = int(input("Номер записи для удаления: "))
                manager.delete(idx)
            except ValueError:
                print("Нужно ввести целое число.")

        elif choice == "4":
            cat = get_nonempty("Категория для фильтра: ")
            filtered = manager.filter_by_category(cat)
            print(f"Расходы категории '{cat}':")
            manager.show(filtered)
            total = sum(exp.amount for exp in filtered)
            print(f"Общая сумма: {total:.2f}")

        elif choice == "5":
            print("Введите начало и конец периода.")
            start = get_date("Начальная дата")
            end = get_date("Конечная дата")
            if start > end:
                print("Ошибка: начальная дата позже конечной.")
                continue
            filtered = manager.filter_by_period(start, end)
            total = manager.total_in_period(start, end)
            print(f"Расходы с {start} по {end}:")
            manager.show(filtered)
            print(f"Общая сумма за период: {total:.2f}")

        elif choice == "6":
            manager.plot_categories()

        elif choice == "0":
            manager.save()
            print("До свидания!")
            break

        else:
            print("Неверный пункт меню, попробуйте снова.")

if __name__ == "__main__":
    main()