def train(self, train_data):
    try:
        # Преобразуем в pandas Series если нужно
        if isinstance(train_data, np.ndarray):
            train_series = pd.Series(train_data)
        else:
            train_series = train_data
        
        print(f"[ARIMA] Обучаю на {len(train_series)} точках")
        self.model = ARIMA(train_series, order=(5, 1, 0))
        self.model_fit = self.model.fit()
        return self
    except Exception as e:
        print(f"[ARIMA] Ошибка обучения: {e}")
        return None