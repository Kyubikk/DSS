from flask import Flask, render_template
from db_connection import get_db_connection
from models.forecast_model import train_and_predict
import pymysql


app = Flask(__name__)

# Trang chủ
@app.route('/')
def index():
    return render_template('base.html')

# Trang dự đoán
@app.route('/forecast')
def forecast():
    try:
        total_forecast, product_forecasts = train_and_predict()
        return render_template('forecast.html', total_forecast=total_forecast, product_forecasts=product_forecasts)
    except Exception as e:
        print(f"Lỗi trong route /forecast: {e}")
        return f"Lỗi trong route /forecast: {e}", 500


@app.route('/test_connection')
def test_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Linh0711',  # Mật khẩu mới
            database='VNUIS_CanteenDSS'
        )
        return "Database connection successful!"
    except pymysql.err.OperationalError as e:
        return f"Database connection failed: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
