import requests
import datetime
import pandas as pd

api_key = 'CG-zcrDBGKQkMdhBSPJWtAijUdT'


url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'

headers = {"accept": "application/json",
    "x-cg-api-key": "CG-zcrDBGKQkMdhBSPJWtAijUdT"}

# Параметры запроса
params = {
    'vs_currency': 'usd',  # Валюта для отображения цены (например, USD)
    'days': '365',         # Данные за последний год
    'interval': 'daily'    # Получение данных на ежедневной основе
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

# Создаем список для хранения отформатированных данных
formatted_data = []

# Извлекаем данные
for i in range(len(data["prices"])):
    # Извлекаем timestamp (одинаковый для всех ключей)
    timestamp = data["prices"][i][0]
    
    # Переводим метку времени из миллисекунд в секунды
    timestamp_in_seconds = timestamp / 1000
    
    # Преобразуем timestamp в объект даты
    date = datetime.datetime.fromtimestamp(timestamp_in_seconds).strftime('%Y-%m-%d')
    
    # Извлекаем уникальные значения для каждого ключа
    price = data["prices"][i][1]
    market_cap = data["market_caps"][i][1]
    total_volumes = data["total_volumes"][i][1]
    
    # Добавляем отформатированные данные в список
    formatted_data.append([date, price, market_cap, total_volumes])

# Создаем DataFrame с колонками "timestamp", "price", "market_cap", "total_volumes"
df = pd.DataFrame(formatted_data, columns=['timestamp', 'prices', 'market_caps', 'total_volumes'])

# Выводим DataFrame
print(df.head())

# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import root_mean_squared_error
# from sklearn.model_selection import train_test_split

# X = df[["market_caps", "total_volumes"]]
# y = df["prices"]


# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# model = LinearRegression()
# model.fit(X_train, y_train)
# y_pred = model.predict(X_test)
# res = root_mean_squared_error(y_test, y_pred)
# print(res)
# print(y_pred[:5])
# print(y_test[:5])