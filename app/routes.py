from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .parser_ozon import parse_ozon
from .models import db, Item, PriceHistory
from datetime import date
import os

# Прогноз
from prophet import Prophet
import pandas as pd

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    print("📂 Текущая рабочая директория:", os.getcwd())
    print("📄 Ожидаем файл шаблона:", os.path.abspath("templates/index.html"))

    template_path = os.path.join(os.getcwd(), "templates")
    if os.path.exists(template_path):
        print("✅ Найден каталог templates:")
        print(os.listdir(template_path))
    else:
        print("❌ Каталог templates не найден!")

    return render_template('index.html')

@main_bp.route('/add', methods=['POST'])
@login_required
def add_item():
    url = request.form['url']
    data = parse_ozon(url)
    if not data:
        return 'Парсинг не удался', 400

    item = Item(name=data['title'], url=url, site='ozon', user_id=current_user.id)
    db.session.add(item)
    db.session.commit()

    ph = PriceHistory(item_id=item.id, date=date.today(), price=data['price'])
    db.session.add(ph)
    db.session.commit()

    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    items = Item.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', items=items)

@main_bp.route('/product/<int:item_id>')
@login_required
def product_detail(item_id):
    item = Item.query.get_or_404(item_id)
    history = PriceHistory.query.filter_by(item_id=item.id).order_by(PriceHistory.date).all()

    dates = [h.date.strftime("%Y-%m-%d") for h in history]
    prices = [h.price for h in history]

    # 🔮 Прогноз на 30 дней
    if len(history) >= 3:
        df = pd.DataFrame({
            'ds': [h.date for h in history],
            'y': [h.price for h in history]
        })

        model = Prophet(daily_seasonality=True)
        model.fit(df)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        forecast_dates = forecast['ds'].dt.strftime('%Y-%m-%d').tolist()
        forecast_prices = forecast['yhat'].round(2).tolist()
    else:
        forecast_dates = []
        forecast_prices = []

    return render_template('product.html',
                           item=item,
                           dates=dates,
                           prices=prices,
                           forecast_dates=forecast_dates,
                           forecast_prices=forecast_prices)
