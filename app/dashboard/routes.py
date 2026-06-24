from flask import render_template
from flask_login import login_required, current_user
from app import db
from sqlalchemy import func
from app.dashboard import dashboard_bp
from app.models import Transaction, Category

@dashboard_bp.route('/')
@login_required
def index():
    # === Баланс ===
    income_total = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'income'
    ).scalar() or 0

    expense_total = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense'
    ).scalar() or 0

    balance = income_total - expense_total

    # === Последние транзакции ===
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc()).limit(5).all()

    # === Данные для круговой диаграммы (расходы по категориям) ===
    expense_by_category = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense'
    ).group_by(Category.name).all()

    chart_labels = [row[0] for row in expense_by_category]
    chart_data = [float(row[1]) for row in expense_by_category]

    # === Данные для линейного графика (доходы и расходы по датам) ===
    from collections import defaultdict
    from datetime import timedelta

    # Получаем все транзакции пользователя
    all_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date).all()

    # Группируем по датам
    income_by_date = defaultdict(float)
    expense_by_date = defaultdict(float)

    for t in all_transactions:
        date_str = t.date.strftime('%Y-%m-%d')
        if t.type == 'income':
            income_by_date[date_str] += t.amount
        else:
            expense_by_date[date_str] += t.amount

    # Объединяем все даты
    all_dates = sorted(set(list(income_by_date.keys()) + list(expense_by_date.keys())))

    line_labels = all_dates
    line_income = [income_by_date.get(d, 0) for d in all_dates]
    line_expense = [expense_by_date.get(d, 0) for d in all_dates]

    return render_template(
        'dashboard/index.html',
        balance=balance,
        income=income_total,
        expense=expense_total,
        recent_transactions=recent_transactions,
        chart_labels=chart_labels,
        chart_data=chart_data,
        line_labels=line_labels,
        line_income=line_income,
        line_expense=line_expense,
        title='Дашборд'
    )