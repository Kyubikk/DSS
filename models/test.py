import pandas as pd
from xgboost import XGBRegressor
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

def add_custom_features(data):
    # Thêm cột ExamPeriod và SummerHoliday
    data['ExamPeriod'] = data['OrderDate'].apply(
        lambda x: 1 if ((x.month == 12 and x.day >= 15) or 
                        (x.month == 1 and x.day <= 15) or 
                        (x.month == 5 and x.day >= 15) or 
                        (x.month == 6 and x.day <= 15)) else 0
    )
    data['SummerHoliday'] = data['OrderDate'].apply(lambda x: 1 if x.month in [7, 8] else 0)

    # Thêm lag features và rolling mean
    data['Lag_1'] = data['DailyRevenue'].shift(1)
    data['Lag_7'] = data['DailyRevenue'].shift(7)
    data['Rolling_Mean_7'] = data['DailyRevenue'].rolling(window=7).mean()

    data.fillna(0, inplace=True)
    return data

def train_total_sales_model(engine):
    # Truy vấn dữ liệu
    total_sales_query = """
    SELECT OrderDate, SUM(TotalAmount) AS DailyRevenue
    FROM `Order`
    GROUP BY OrderDate
    ORDER BY OrderDate;
    """
    total_sales = pd.read_sql(total_sales_query, con=engine)

    # Kiểm tra dữ liệu
    print(total_sales.head())  # Xem dữ liệu
    print(total_sales.columns)  # Xem các cột hiện có

    # Chuyển đổi và thêm đặc trưng
    total_sales['OrderDate'] = pd.to_datetime(total_sales['OrderDate'])
    total_sales['Day'] = total_sales['OrderDate'].dt.day
    total_sales['Month'] = total_sales['OrderDate'].dt.month
    total_sales['Year'] = total_sales['OrderDate'].dt.year
    total_sales['Weekday'] = total_sales['OrderDate'].dt.weekday
    total_sales = add_custom_features(total_sales)

    # Tách dữ liệu
    X = total_sales[['Day', 'Month', 'Year', 'Weekday', 'ExamPeriod', 'SummerHoliday', 'Lag_1', 'Lag_7', 'Rolling_Mean_7']]
    y = total_sales['DailyRevenue']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Huấn luyện mô hình
    model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    # Dự đoán và đánh giá
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Tổng Doanh Số - MAE: {mae}, MSE: {mse}, R²: {r2}")

    # Vẽ biểu đồ
    plt.plot(y_test.values, label="Actual", marker="o")
    plt.plot(y_pred, label="Predicted", marker="x")
    plt.title("Actual vs Predicted Total Sales")
    plt.legend()
    plt.show()

    return model

def main():
    # Kết nối SQLAlchemy
    engine = create_engine("mysql+pymysql://root:Linh0711@localhost/VNUIS_CanteenDSS")

    # Huấn luyện mô hình
    train_total_sales_model(engine)

if __name__ == "__main__":
    main()
