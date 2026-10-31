"""  
Описание запроса создания горячего кофе  
---------------------------------------  
Метод и URL:   POST https://api.sampleapis.com/coffee/hot  
Заголовки:     Content-Type: application/json (requests ставит сам при json=...)  
  
Тело запроса (JSON-объект):  
  title        строка         обязательное  название напитка   
  description  строка         обязательное  описание  
  ingredients  список строк   обязательное  состав  
  image        строка         обязательное  ссылка на картинку (может быть пустой)  
  id           не передаём: его создаёт сервер  
  
Ответ: 201 Created, JSON-объект с теми же полями и новым id (его надо сохранить).  
  
Подтверждено запросами к API: без любого из четырёх полей сервер отвечает 400;  
без Content-Type: application/json тело не разбирается (400); лишние поля сохраняются.  
Только в клиенте (сервер не проверяет): типы значений, непустые строки.  
"""  
  
import requests  
  
from app.exceptions import CoffeeApiError, CoffeeNotFoundError  
  
JsonObject = dict[str, object]  
  
  
class SampleApisCoffeeClient:  
    def __init__(  
        self,  
        base_url: str = "https://api.sampleapis.com/coffee/hot",  
        timeout: float = 10.0,  
    ) -> None:  
        self._base_url = base_url.rstrip("/")  
        self._timeout = timeout  
  
    def list_drinks(self) -> list[JsonObject]:  
        return self._request_json("GET")  
  
    def get_drink(self, drink_id: int) -> JsonObject:  
        return self._request_json("GET", f"/{drink_id}")  
  
    def create_drink(self, payload: JsonObject) -> JsonObject:  
        return self._request_json("POST", "", payload)  
  
    def replace_drink(self, drink_id: int, payload: JsonObject) -> JsonObject:  
        return self._request_json("PUT", f"/{drink_id}", payload)  
  
    def update_drink(self, drink_id: int, changes: JsonObject) -> JsonObject:  
        return self._request_json("PATCH", f"/{drink_id}", changes)  
  
    def delete_drink(self, drink_id: int) -> None:  
        # Тело ответа на DELETE не разбираем: достаточно проверить статус.  
        self._request("DELETE", f"/{drink_id}")  
  
    def _request_json(self, method, path="", payload=None):  
        response = self._request(method, path, payload)  
        if "application/json" not in response.headers.get("Content-Type", ""):  
            raise CoffeeApiError("Ответ не JSON")  
        try:  
            return response.json()  
        except ValueError as error:  
            raise CoffeeApiError(f"Некорректный JSON: {error}") from error  
  
    def _request(  
        self,  
        method: str,  
        path: str = "",  
        payload: JsonObject | None = None,  
    ) -> requests.Response:  
        url = f"{self._base_url}{path}"  
        try:  
            response = requests.request(  
                method, url, json=payload, timeout=self._timeout  
            )  
        except requests.RequestException as error:  
            raise CoffeeApiError(f"Ошибка запроса {method} {url}: {error}") from error  
        if response.status_code == 404:  
            raise CoffeeNotFoundError(f"Не найдено: {method} {url}")  
        if not 200 <= response.status_code < 300:  
            raise CoffeeApiError(f"{method} {url} вернул {response.status_code}")  
        return response 