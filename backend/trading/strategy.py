import pandas as pd


class RiskManagedStrategy:

    def __init__(
        self,
        balance,
        risk_per_trade=0.005,
        reward_ratio=3,
    ):
        self.balance = float(balance)
        self.risk_per_trade = risk_per_trade
        self.reward_ratio = reward_ratio

    def clean_dataframe(self, df):
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.copy()

        df = df.dropna()

        return df

    def calculate_atr(self, df, period=14):
        high = df["High"].astype(float)
        low = df["Low"].astype(float)
        close = df["Close"].astype(float)

        high_low = high - low
        high_close = (high - close.shift()).abs()
        low_close = (low - close.shift()).abs()

        true_range = pd.concat(
            [high_low, high_close, low_close],
            axis=1
        ).max(axis=1)

        return true_range.rolling(period).mean()

    def add_indicators(self, df):
        df = self.clean_dataframe(df)

        df["ema_20"] = df["Close"].astype(float).ewm(span=20).mean()
        df["ema_50"] = df["Close"].astype(float).ewm(span=50).mean()
        df["atr"] = self.calculate_atr(df)

        df = df.dropna()

        return df

    def signal(self, df):
        last = df.iloc[-1]

        ema_20 = float(last["ema_20"])
        ema_50 = float(last["ema_50"])

        if ema_20 > ema_50:
            return "BUY"

        if ema_20 < ema_50:
            return "SELL"

        return "HOLD"

    def calculate_position_size(self, entry_price, stop_loss):
        risk_amount = self.balance * self.risk_per_trade
        risk_per_unit = abs(entry_price - stop_loss)

        if risk_per_unit == 0:
            return 0

        return risk_amount / risk_per_unit

    def create_trade(self, df):
        df = self.add_indicators(df)

        if df.empty:
            return None

        last = df.iloc[-1]

        signal = self.signal(df)

        if signal == "HOLD":
            return None

        entry = float(last["Close"])
        atr = float(last["atr"])

        if pd.isna(atr) or atr <= 0:
            return None

        if signal == "BUY":
            stop_loss = entry - atr
            take_profit = entry + (atr * self.reward_ratio)

        else:
            stop_loss = entry + atr
            take_profit = entry - (atr * self.reward_ratio)

        size = self.calculate_position_size(
            entry,
            stop_loss
        )

        return {
            "signal": signal,
            "entry_price": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size": size,
            "risk_amount": self.balance * self.risk_per_trade,
        }