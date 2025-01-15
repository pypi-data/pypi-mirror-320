from __future__ import annotations

from dataclasses import dataclass
from random import random
from enum import Enum
from time import sleep
import openfoodfacts
from requests import ConnectionError, Timeout


class AbstractSDK:
    @property
    def product(self):
        raise NotImplementedError()


@dataclass(frozen=True)
class Product:
    name: str
    energy: str
    protein: str
    fiber: str
    fat: str
    nutriscore: str


class SDKVersion(Enum):
    v1 = "v1"
    v2 = "v2"
    v3 = "v3"
    v4 = "v4"
    v5 = "v5"
    v6 = "v6"


class SDKBuilder:
    def __init__(self):
        self.acknowledged = False

    def acknowledge(self) -> SDKBuilder:
        self.acknowledged = True
        return self

    def build(self, version: SDKVersion) -> AbstractSDK:
        version_to_instance = {SDKVersion.v1: SDKV1, SDKVersion.v2: SDKV2, SDKVersion.v3: SDKV3, SDKVersion.v4: SDKV3, SDKVersion.v5: SDKV5, SDKVersion.v6: SDKV6}
        
        if version == SDKVersion.v4 and not self.acknowledged:
            raise Exception("In this version, the Client will not be modified, but you need to implement a new feature : the calculus and display of the fullness factor" 
                            "You can use the provided function fullness_factor in the dependency_sdk package" 
                            "Call the acknowledge method of the SDKBuilder to stop raising this exception")

        return version_to_instance[version]()

def gram_to_kilogram(number: str):
    try:
        return float(number)*0.001
    except ValueError:
        return number

class ProductOperationV1:
    def get(self, barcode: str) -> Product:
        api = openfoodfacts.API(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            version=openfoodfacts.APIVersion.v3,
            timeout=100,
        )
        # raise Exception(api.product.text_search("nutella"))
        json_info = api.product.get(barcode)

        name = json_info["product_name"]
        energy = str(gram_to_kilogram(json_info["nutriments"]["energy-kcal_100g"]))
        protein = str(gram_to_kilogram(json_info["nutriments"]["proteins_100g"]))
        fiber = str(gram_to_kilogram(json_info["nutriments"].get("fiber_100g", "-")))
        fat = str(gram_to_kilogram(json_info["nutriments"]["fat_100g"]))
        nutriscore = json_info["nutriscore"]["2023"]["grade"]
        return Product(name, energy, protein, fiber, fat, nutriscore)


class SDKV1:
    @property
    def product(self):
        return ProductOperationV1()


class ProductOperationV2:
    def get(self, barcode: str) -> Product:
        api = openfoodfacts.API(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            version=openfoodfacts.APIVersion.v3,
            timeout=100,
        )
        # raise Exception(api.product.text_search("nutella"))
        json_info = api.product.get(barcode)

        name = json_info["product_name"]
        energy = gram_to_kilogram(json_info["nutriments"]["energy-kcal_100g"])
        protein = gram_to_kilogram(json_info["nutriments"]["proteins_100g"])
        fiber = gram_to_kilogram(json_info["nutriments"].get("fiber_100g", "-"))
        fat = gram_to_kilogram(json_info["nutriments"]["fat_100g"])
        nutriscore = json_info["nutriscore"]["2023"]["grade"]
        return Product(name, energy, protein, fiber, fat, nutriscore)


class SDKV2:
    @property
    def product(self):
        return ProductOperationV2()


class ProductOperationV3:
    def get(self, barcode: str) -> Product:
        api = openfoodfacts.API(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            version=openfoodfacts.APIVersion.v3,
            timeout=100,
        )
        json_info = api.product.get(barcode)

        name = json_info["product_name"]
        energy = json_info["nutriments"]["energy-kcal_100g"]
        protein = json_info["nutriments"]["proteins_100g"]
        fiber = json_info["nutriments"].get("fiber_100g", "-")
        fat = json_info["nutriments"]["fat_100g"]
        nutriscore = json_info["nutriscore"]["2023"]["grade"]
        return Product(name, energy, protein, fiber, fat, nutriscore)


class SDKV3:
    @property
    def product(self):
        return ProductOperationV3()


class ProductOperationV5:
    def get(self, barcode: str, timeout: int = 1) -> Product:
        time_to_wait = random()*10
        if time_to_wait < 1.2:
            time_to_wait = 60*60*24
        time_waited = 0
        for _ in range(int(time_to_wait)):
            time_waited +=1
            sleep(1)
            if timeout < time_waited:
                raise Timeout()
        
        api = openfoodfacts.API(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            version=openfoodfacts.APIVersion.v3,
            timeout=timeout,
        )
        # raise Exception(api.product.text_search("nutella"))
        json_info = api.product.get(barcode)

        name = json_info["product_name"]
        energy = json_info["nutriments"]["energy-kcal_100g"]
        protein = json_info["nutriments"]["proteins_100g"]
        fiber = json_info["nutriments"].get("fiber_100g", "-")
        fat = json_info["nutriments"]["fat_100g"]
        nutriscore = json_info["nutriscore"]["2023"]["grade"]
        return Product(name, energy, protein, fiber, fat, nutriscore)


class SDKV5:
    @property
    def product(self):
        return ProductOperationV5()


class ProductOperationV6:
    def get(self, barcode: str, timeout: int = 1) -> Product:
        time_to_wait = random()*10
        if time_to_wait < 2:
            time_to_wait = 60*60*24
        time_waited = 0
        for _ in range(int(time_to_wait)):
            time_waited +=1
            sleep(1)
            if timeout < time_waited:
                raise Timeout()

        api = openfoodfacts.API(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            version=openfoodfacts.APIVersion.v3,
            timeout=timeout,
        )
        # raise Exception(api.product.text_search("nutella"))
        json_info = api.product.get(barcode)

        name = json_info["product_name"]
        energy = json_info["nutriments"]["energy-kcal_100g"]
        protein = json_info["nutriments"]["proteins_100g"]
        fiber = json_info["nutriments"].get("fiber_100g", "-")
        fat = json_info["nutriments"]["fat_100g"]
        nutriscore = json_info["nutriscore"]["2023"]["grade"]
        return Product(name, energy, protein, fiber, fat, nutriscore)


class SDKV6:
    @property
    def product(self):
        return ProductOperationV6()
