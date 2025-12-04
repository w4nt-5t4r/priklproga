import json

class VehicleError(Exception):
    pass

class Vehicle:
    def __init__(self, vid, brand, model):
        if not vid or not brand or not model:
            raise VehicleError("Поля не могут быть пустыми")
        self.vid = vid
        self.brand = brand
        self.model = model

class Car(Vehicle):
    def __init__(self, vid, brand, model):
        super().__init__(vid, brand, model)

class Truck(Vehicle):
    def __init__(self, vid, brand, model):
        super().__init__(vid, brand, model)

class Motorcycle(Vehicle):
    def __init__(self, vid, brand, model):
        super().__init__(vid, brand, model)

class Fleet:
    def __init__(self):
        self.vehicles = []

    def add(self, v):
        for existing in self.vehicles:
            if existing.vid == v.vid:
                raise VehicleError("ТС с таким ID уже есть")
        self.vehicles.append(v)

    def remove(self, vid):
        for v in self.vehicles:
            if v.vid == vid:
                self.vehicles.remove(v)
                return
        raise VehicleError("ТС не найдено")

    def list_all(self):
        return self.vehicles

    def save(self, filename):
        data = []
        for v in self.vehicles:
            data.append({
                "type": v.__class__.__name__,
                "vid": v.vid,
                "brand": v.brand,
                "model": v.model
            })
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.vehicles = []
            for item in data:
                cls_name = item["type"]
                if cls_name == "Car":
                    self.vehicles.append(Car(item["vid"], item["brand"], item["model"]))
                elif cls_name == "Truck":
                    self.vehicles.append(Truck(item["vid"], item["brand"], item["model"]))
                elif cls_name == "Motorcycle":
                    self.vehicles.append(Motorcycle(item["vid"], item["brand"], item["model"]))
                else:
                    raise VehicleError("Неизвестный тип ТС")
        except FileNotFoundError:
            raise VehicleError("Файл не найден")
        except json.JSONDecodeError:
            raise VehicleError("Ошибка чтения JSON")

if __name__ == "__main__":
    try:
        fleet = Fleet()
        fleet.add(Car("1", "Lada", "Granta"))
        fleet.add(Truck("2", "KAMAZ", "6520"))
        fleet.add(Motorcycle("3", "Ural", "Gear Up"))
        fleet.save("data.json")

        new_fleet = Fleet()
        new_fleet.load("data.json")
        for v in new_fleet.list_all():
            print(v.brand, v.model)

        new_fleet.remove("1")
        print("После удаления:")
        for v in new_fleet.list_all():
            print(v.brand, v.model)

    except VehicleError as e:
        print("Ошибка:", e)
    except Exception as e:
        print("Системная ошибка:", e)