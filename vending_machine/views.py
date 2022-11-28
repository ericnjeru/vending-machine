from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class VendingMachine:
    def __init__(self, products, coins):
        self.products = products
        self.coins = coins

    def vend(self, product_slot, inserted_coins):
        """
        responsible for allowing users to buy products (vending)
        :param product_slot: identifies the type of product
        :param inserted_coins: list of dict that holds different coins inserted. Contain code, quantity
        """
        products = self.products
        coins = self.coins

        selected_product = products.get(product_slot)
        # validate product exist
        if not selected_product:
            raise ValidationError("Product slot does not exist")

        # validate product quantity
        if selected_product.get("quantity") == 0:
            raise ValidationError(detail="Product out of stock")

        selected_product_price = selected_product.get("price")
        # validate user money
        user_amount = 0
        for inserted_coin in inserted_coins:
            inserted_coin_code = inserted_coin.get("code")
            inserted_coin_quantity = inserted_coin.get("quantity")
            user_coin = coins.get(inserted_coin_code)
            if not user_coin:
                raise ValidationError(detail=f"The coin '{inserted_coin_code}' is not accepted")
            total_value = user_coin.get('value') * inserted_coin_quantity
            user_amount += total_value

        if user_amount < selected_product_price:
            raise ValidationError(detail="Not enough money to purchase selected product")

        # calculate the change
        change_total = user_amount - selected_product_price
        user_change = {}
        if change_total > 0:
            user_change = self.calculate_change(change_total)

        # update coins inventory
        for code, quantity in user_change.items():
            self.update_coin_quantity(code, quantity)

        # update product inventory
        self.update_product_quantity(product_slot, 1)

        # Transaction successful
        return {
            "Message": "Product purchased successfully",
            "Product": selected_product.get("name"),
            "change_value": round(change_total, 2),
            "change_coins": user_change
        }

    def calculate_change(self, change_total):
        """
        calculates change o be given for each type of coin
        :param change_total: the total amount of changes value
        :return: Dict of each type of coin and it's quantity
        """
        sorted_coins = sorted(self.coins.items(), key=lambda item: item[1].get("value"), reverse=True)
        coins = {key: value for key, value in sorted_coins}
        user_change = {}

        for code, coin in coins.items():
            coin_value = coin.get("value")
            coin_quantity = coin.get("quantity")
            if coin_quantity > 0:
                if change_total >= coin_value:
                    user_change[code] = round(change_total // coin_value)
                    coin_change_quantity = user_change.get(code)
                    if coin_change_quantity > coin_quantity:
                        raise ValidationError(detail="Not enough coins to give change. Transaction canceled")
                    change_total = round(change_total - (coin_change_quantity * coin_value), 2)

        return user_change

    def update_coin_quantity(self, code, quantity, restock=False):
        """
        updates quantity of a type of coins available
        :param code: unique identifier for type of coin
        :param quantity: the quantity to be added/subtracted
        :param restock: Boolean - determines if quantity is added/subtracted
        :return: Coin dict
        """
        coin = self.coins.get(code)
        if not coin:
            raise ValidationError(detail=f"'{code}' coin not found", code=status.HTTP_404_NOT_FOUND)
        current_quantity = coin.get("quantity")
        coin["quantity"] = quantity if restock else current_quantity - quantity
        self.coins[code] = coin
        return coin

    def update_product_quantity(self, slot, quantity, restock=False):
        """
        updates the quantity of a given product (increase or decrease)
        :param slot: unique identifier of product
        :param quantity: the quantity to be added/subtracted
        :param restock: Boolean - determines if quantity is added/subtracted
        :return: product dict
        """
        product = self.products.get(slot)
        if not product:
            raise ValidationError(detail=f"Product slot '{slot}' not found", code=status.HTTP_404_NOT_FOUND)
        current_quantity = product.get("quantity")
        product["quantity"] = quantity if restock else current_quantity - quantity
        self.products[slot] = product
        return product

    def update_product_price(self, slot, new_price):
        """
        Updates the price of a given product
        :param slot: unique product identifier
        :param new_price: the price to be set
        :return: product dict
        """
        product = self.products.get(slot)
        product["price"] = new_price
        self.products[slot] = product
        return product


# Initialize vending machine with products and coins
vending_machine = VendingMachine(
    products={
        "slot1": {"name": "candy", "quantity": 10, "price": 3},
        "slot2": {"name": "cookies", "quantity": 10, "price": 4},
        "slot3": {"name": "fresh fruit", "quantity": 10, "price": 2},
        "slot4": {"name": "milk", "quantity": 10, "price": 5},
        "slot5": {"name": "water", "quantity": 10, "price": 1},
        "slot6": {"name": "soda", "quantity": 30, "price": 5},
    },
    coins={
        "1c": {"quantity": 200, "value": 0.01},
        "5c": {"quantity": 100, "value": 0.05},
        "10c": {"quantity": 70, "value": 0.10},
        "25c": {"quantity": 50, "value": 0.25},
        "50c": {"quantity": 30, "value": 0.5},
    }
)


@api_view(["GET"])
def list_products(request):
    return Response(vending_machine.products)


@api_view(["POST"])
def buy_product(request):
    data = request.data
    product_slot = data.get("product_slot")
    coins = data.get("coins")

    response = vending_machine.vend(product_slot, coins)
    return Response(response)


@api_view(["POST"])
def update_product_quantity(request):
    data = request.data
    product_slot = data.get("product_slot")
    quantity = data.get("quantity")
    return Response(vending_machine.update_product_quantity(product_slot, quantity, True))


@api_view(["POST"])
def update_product_price(request):
    data = request.data
    product_slot = data.get("product_slot")
    price = data.get("price")
    return Response(vending_machine.update_product_price(product_slot, price))


@api_view(["GET"])
def list_coins(request):
    return Response(vending_machine.coins)


@api_view(["POST"])
def update_coin_quantity(request):
    data = request.data
    code = data.get("code")
    quantity = data.get("quantity")
    return Response(vending_machine.update_coin_quantity(code, quantity, True))
