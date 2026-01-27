def train(self, train_data):
    # Преобразуем numpy array в pandas Series
    if isinstance(train_data, np.ndarray):
        train_series = pd.Series(train_data)
    else:
        train_series = train_data
    
    df = self.create_features(train_series)
    if len(df) < 10:
        print("[ML] Недостаточно данных для обучения")
        return None
    
    X = df.drop('price', axis=1)
    y = df['price']
    
    print(f"[ML] Обучаю на {len(X)} примерах")
    self.model.fit(X, y)
    return self