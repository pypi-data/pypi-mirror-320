class YoY_Calculator:
    def __init__(self):
        pass

    @classmethod
    def cal_growth(cls, target_value: float, past_value: float, delta: int):
        """
        計算成長率以及年化成長率
        target_value: float，這個時間的數值
        past_value: float，過去的這個時間數值
        delta: int，代表隔了幾年/季 delta > 1 時改以年化成長率計算
        """
        try:
            if (delta > 1):
                YoY = ((target_value / past_value)**(1 / delta)) - 1

            else:
                YoY = ((target_value - past_value) / past_value)

        except Exception as e:
            return None

        if (isinstance(YoY, complex)): # 年化成長率有複數問題
            return None

        return YoY