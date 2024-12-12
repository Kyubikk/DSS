import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Linh0711',  # Đổi 'yourpassword' thành mật khẩu của bạn
        database='VNUIS_CanteenDSS'
    )
    print("Kết nối thành công!")
except pymysql.MySQLError as e:
    print("Không thể kết nối MySQL.")
    print(e)
