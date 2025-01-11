import requests

session = requests.Session()

class Balance:
    url = "http://137.82.65.246:8000/backend_control/deck.balance"
    def dose_solid(self, amount_in_mg: float):
        """this function is used to dose solid"""
        session.post(self.url, data={"hidden_name": "dose_solid", "amount_in_mg": amount_in_mg})

    def weigh_sample(self):
        session.post(self.url, data={"hidden_name": "weigh_sample"})


class Pump:
    url = "http://137.82.65.246:8000/backend_control/deck.pump"
    def dose_liquid(self, amount_in_ml: float, rate_ml_per_minute: float):
        session.post(self.url, data={"hidden_name": "dose_liquid", "amount_in_ml": amount_in_ml, "rate_ml_per_minute": rate_ml_per_minute})


class Sdl:
    url = "http://137.82.65.246:8000/backend_control/deck.sdl"
    def analyze(self):
        session.post(self.url, data={"hidden_name": "analyze"})

    def dose_solid(self, amount_in_mg: float = 5, bring_in: bool = False):
        """dose current chemical"""
        session.post(self.url, data={"hidden_name": "dose_solid", "amount_in_mg": amount_in_mg, "bring_in": bring_in})

    def dose_solvent(self, name: str, amount_in_ml: float = 5, rate_ml_per_minute: float = 1):
        session.post(self.url, data={"hidden_name": "dose_solvent", "name": name, "amount_in_ml": amount_in_ml, "rate_ml_per_minute": rate_ml_per_minute})

    def equilibrate(self, temp: float, duration: float):
        session.post(self.url, data={"hidden_name": "equilibrate", "temp": temp, "duration": duration})

    def filtration(self):
        session.post(self.url, data={"hidden_name": "filtration"})


balance = Balance()
pump = Pump()
sdl = Sdl()
