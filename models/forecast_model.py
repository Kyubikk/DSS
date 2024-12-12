import pandas as pd
from xgboost import XGBRegressor
from sqlalchemy import create_engine
from datetime import datetime

def train_and_predict():
    # Kết nối SQLAlchemy
    engine = create_engine("mysql+pymysql://root:Linh0711@localhost/VNUIS_CanteenDSS")

    # Lấy dữ liệu tổng doanh số
    total_sales_query = """
    SELECT OrderDate, SUM(TotalAmount) AS DailyRevenue
    FROM `Order`
    GROUP BY OrderDate
    ORDER BY OrderDate;
    """
    total_sales = pd.read_sql(total_sales_query, con=engine)

    # Kiểm tra dữ liệu
    if 'OrderDate' not in total_sales.columns or total_sales.empty:
        raise ValueError("Dữ liệu `OrderDate` hoặc `DailyRevenue` không tồn tại hoặc rỗng!")

    # Xử lý dữ liệu tổng doanh số
    total_sales['OrderDate'] = pd.to_datetime(total_sales['OrderDate'])
    total_sales['Day'] = total_sales['OrderDate'].dt.day
    total_sales['Month'] = total_sales['OrderDate'].dt.month
    total_sales['Year'] = total_sales['OrderDate'].dt.year

    X_total = total_sales[['Day', 'Month', 'Year']]
    y_total = total_sales['DailyRevenue']

    # Huấn luyện mô hình tổng doanh số
    total_model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
    total_model.fit(X_total, y_total)

    # Dự đoán tổng doanh số 30 ngày tới từ thời gian thực
    today = datetime.today()  # Thời gian thực
    future_dates = pd.date_range(start=today, periods=30)
    future_data = pd.DataFrame({
        'Day': future_dates.day,
        'Month': future_dates.month,
        'Year': future_dates.year
    })
    total_predictions = total_model.predict(future_data)

    # Chuyển đổi dữ liệu thành kiểu Python tiêu chuẩn
    total_forecast = [{"date": str(date.date()), "predicted_sales": float(sales)} for date, sales in zip(future_dates, total_predictions)]

    # Lấy dữ liệu doanh số từng sản phẩm
    product_sales_query = """
    SELECT oi.ProductID, p.ProductName, DATE(o.OrderDate) AS OrderDate, SUM(oi.Quantity * oi.UnitPrice) AS ProductRevenue
    FROM OrderItem oi
    JOIN `Order` o ON oi.OrderID = o.OrderID
    JOIN Product p ON oi.ProductID = p.ProductID
    GROUP BY oi.ProductID, OrderDate
    ORDER BY OrderDate;
    """
    product_sales = pd.read_sql(product_sales_query, con=engine)

    # Dự đoán doanh số từng sản phẩm trong 7 ngày tới từ thời gian thực
    product_forecasts = []
    for (product_id, product_name), group_data in product_sales.groupby(['ProductID', 'ProductName']):
        group_data['OrderDate'] = pd.to_datetime(group_data['OrderDate'])
        group_data['Day'] = group_data['OrderDate'].dt.day
        group_data['Month'] = group_data['OrderDate'].dt.month
        group_data['Year'] = group_data['OrderDate'].dt.year

        X_product = group_data[['Day', 'Month', 'Year']]
        y_product = group_data['ProductRevenue']

        # Huấn luyện mô hình từng sản phẩm
        product_model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
        product_model.fit(X_product, y_product)

        # Tạo dữ liệu cho 7 ngày tới
        future_dates_7 = pd.date_range(start=today, periods=7)
        future_data_7 = pd.DataFrame({
            'Day': future_dates_7.day,
            'Month': future_dates_7.month,
            'Year': future_dates_7.year
        })

        product_predictions = product_model.predict(future_data_7)
        product_forecast = [{"date": str(date.date()), 
                             "product_id": int(product_id),  # Chuyển đổi `int64` thành `int`
                             "product_name": product_name, 
                             "predicted_sales": float(sales)}
                            for date, sales in zip(future_dates_7, product_predictions)]
        product_forecasts.extend(product_forecast)

    return total_forecast, product_forecasts
