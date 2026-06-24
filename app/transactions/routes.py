from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Transaction, Category
from app.forms import TransactionForm
from app.transactions import transactions_bp
from datetime import date as dt


def get_or_create_default_categories(user_id):
    """Создаёт дефолтные категории при первом использовании"""
    default_categories = [
        ('Продукты', 'expense'),
        ('Транспорт', 'expense'),
        ('Жильё', 'expense'),
        ('Развлечения', 'expense'),
        ('Зарплата', 'income'),
        ('Фриланс', 'income'),
        ('Другое', 'expense'),
    ]

    existing = Category.query.filter(
        (Category.user_id == user_id) | (Category.user_id.is_(None))
    ).count()

    if existing == 0:
        for name, cat_type in default_categories:
            cat = Category(name=name, type=cat_type, user_id=None)
            db.session.add(cat)
        db.session.commit()


@transactions_bp.route('/')
@login_required
def index():
    # Получаем параметры фильтров из URL
    search = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '')
    category_filter = request.args.get('category', type=int, default=0)

    # Базовый запрос
    query = Transaction.query.filter_by(user_id=current_user.id)

    # Применяем фильтры
    if search:
        query = query.filter(Transaction.description.ilike(f'%{search}%'))

    if type_filter in ['income', 'expense']:
        query = query.filter(Transaction.type == type_filter)

    if category_filter > 0:
        query = query.filter(Transaction.category_id == category_filter)

    transactions = query.order_by(Transaction.date.desc()).all()

    # Форма для модального окна
    form = TransactionForm()
    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id.is_(None))
    ).order_by(Category.name).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    today = dt.today().strftime('%Y-%m-%d')

    return render_template(
        'transactions/index.html',
        transactions=transactions,
        form=form,
        today=today,
        categories=categories,
        search=search,
        type_filter=type_filter,
        category_filter=category_filter,
        title='Мои транзакции'
    )


@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    get_or_create_default_categories(current_user.id)

    form = TransactionForm()

    # Получаем категории
    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id.is_(None))
    ).order_by(Category.name).all()

    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        transaction = Transaction(
            amount=form.amount.data,
            type=form.type.data,
            category_id=form.category_id.data,
            date=form.date.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Транзакция успешно добавлена!', 'success')
        return redirect(url_for('transactions.index'))

    # Передаём сегодняшнюю дату в шаблон (для модального окна)
    today = dt.today().strftime('%Y-%m-%d')

    return render_template(
        'transactions/add.html',
        form=form,
        title='Добавить транзакцию',
        today=today
    )


@transactions_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != current_user.id:
        flash('Нет доступа к этой транзакции', 'danger')
        return redirect(url_for('transactions.index'))

    form = TransactionForm(obj=transaction)

    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id.is_(None))
    ).order_by(Category.name).all()

    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.type = form.type.data
        transaction.category_id = form.category_id.data
        transaction.date = form.date.data
        transaction.description = form.description.data
        db.session.commit()
        flash('Транзакция обновлена!', 'success')
        return redirect(url_for('transactions.index'))

    return render_template('transactions/edit.html', form=form, transaction=transaction,
                           title='Редактировать транзакцию')


@transactions_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != current_user.id:
        flash('Нет доступа', 'danger')
        return redirect(url_for('transactions.index'))

    db.session.delete(transaction)
    db.session.commit()
    flash('Транзакция удалена', 'info')
    return redirect(url_for('transactions.index'))