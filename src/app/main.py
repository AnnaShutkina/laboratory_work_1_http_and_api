from uuid import uuid4

from app.client import SampleApisCoffeeClient
from app.exceptions import CoffeeApiError, CoffeeNotFoundError

def main() -> int:
    client = SampleApisCoffeeClient(base_url="http://127.0.0.1:8000/coffee/hot")
    marker = uuid4().hex[:8]
    created_id = None
    try:
        print("1. GET список напитков")
        drinks = client.list_drinks()
        print(f"   получено напитков: {len(drinks)}")

        print("2. POST создаём напиток")
        payload = {
            "title": f"Group coffee {marker}",
            "description": "Hot drink",
            "ingredients": ["Water", "Coffee"],
            "image": "https://example.com/coffee.jpg",
        }
        created = client.create_drink(payload)
        created_id = created["id"]  # сразу запоминаем id, чтобы удалить в finally
        print(f"   создан id={created_id}")

        print("3. GET по id и сравнение полей")
        got = client.get_drink(created_id)
        for key, value in payload.items():
            if got.get(key) != value:
                raise ValueError(f"После POST поле {key!r}: {got.get(key)!r} != {value!r}")
        print("   поля совпадают")

        print("4. PUT полная замена")
        replaced = {
            "title": f"Replaced coffee {marker}",
            "description": "Replaced description",
            "ingredients": ["Espresso"],
            "image": "https://example.com/replaced.jpg",
        }
        client.replace_drink(created_id, replaced)
        got = client.get_drink(created_id)
        for key, value in replaced.items():
            if got.get(key) != value:
                raise ValueError(f"После PUT поле {key!r}: {got.get(key)!r} != {value!r}")
        print("   все поля заменены")

        print("5. PATCH частичное изменение")
        client.update_drink(created_id, {"description": "Patched description"})
        got = client.get_drink(created_id)
        if got.get("description") != "Patched description":
            raise ValueError("PATCH не изменил description")
        for key in ("title", "ingredients", "image"):
            if got.get(key) != replaced[key]:
                raise ValueError(f"PATCH испортил поле {key!r}")
        print("   description изменено, остальные поля сохранились")

        print("6. DELETE и проверка 404")
        client.delete_drink(created_id)
        try:
            client.get_drink(created_id)
        except CoffeeNotFoundError:
            print("   получен ожидаемый 404, запись удалена")
            created_id = None
        else:
            raise ValueError("После DELETE запись всё ещё доступна")
    except (CoffeeApiError, ValueError) as error:
        print(f"Ошибка: {error}. Метка группы: {marker}")
        return 1
    finally:
        if created_id is not None:
            try:
                client.delete_drink(created_id)
            except CoffeeNotFoundError:
                pass
            except CoffeeApiError as error:
                print(f"Не удалось удалить id={created_id}: {error}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())