# vending-machine

## Quickstart

1. Set up a Python virtual environment and install the required Python dependencies:
``pip install pipenv && pipenv install``

   
2. Create `.env` configuration file based on `env.sample`

3.  Run the server:
`` pipenv run python manage.py runserver ``
    

## Available API endpoints

1.   http://127.0.0.1:8000/buy-product 
```
Method: POST
Sample Body:
{
    "product_slot": "slot1",
    "coins": [
        {"code": "5c", "quantity": 15},
        {"code": "10c", "quantity": 8},
        {"code": "25c", "quantity": 6},
        {"code": "50c", "quantity": 6}
    ]
}
```

2.  http://127.0.0.1:8000/list-products
```
Method: GET
```

3.  http://127.0.0.1:8000/list-coins
```
Method: GET
```

4.  http://127.0.0.1:8000/adjust-coin-quantity
```
Method: POST
Sample Body:
{
    "code": "50cs",
    "quantity": 10
}
```

5.  http://127.0.0.1:8000/adjust-product-quantity
```
Method: POST
Sample Body:
{
    "product_slot": "slot1",
    "quantity": 10
}
```

6.  http://127.0.0.1:8000/adjust-product-price
```
Method: POST
Sample Body:
{
    "product_slot": "slot1",
    "price": 10
}
```

# Postman collection 
[Vending machine apis](vending-machine.postman_collection.json)
