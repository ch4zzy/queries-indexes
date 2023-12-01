from faker import Faker
import random
import json
import faker_commerce
from apps.queries.models import Category, Product, Order
from .decorators import timing_decorator

fake = Faker()


def fake_category(n):
    fake.add_provider(faker_commerce.Provider)
    for _ in range(n):
        name = fake.unique.ecommerce_category()
        Category.objects.create(
            name = name,
            description = fake.text(),
            slug = fake.slug(name),
    )


def fake_product(n):
    fake.add_provider(faker_commerce.Provider)
    for _ in range(n):
        category = random.choice(Category.objects.all())
        if Product.objects.last() is None:
            name = fake.ecommerce_name() + "-" + str(0)
        else:
            name = fake.ecommerce_name() + "-" + str(Product.objects.last().id)

        Product.objects.create(
            category = category,
            name = name,
            slug = fake.slug(name),
            description = fake.text(),
            price = fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            available = random.choice([True, False]),
        )
        print(_)
        

status_type = ["paid", "unpaid", "delivered"]

def fake_status():
    return {
        random.choice(status_type): fake.date_time_this_year(
            before_now=True, after_now=False, tzinfo=None
        ).strftime('%Y-%m-%d %H:%M:%S')
    }


def fake_order_json():
    product = Product.objects.get(
        id=random.randint(1, Product.objects.count())
    )
    order_json = {
        "products": [
            {
                "product": product.name,
                "quantity": random.randint(1, 10),
                "price": float(product.price),
            } for _ in range(random.randint(3, 7))
        ],
        "total_price": 0,  
    }
    
    order_json["total_price"] = sum(
        item["quantity"] * item["price"] for item in order_json["products"]
    )
    return order_json


@timing_decorator
def fake_order(n):
    for _ in range(n):
        status = fake_status()
        order = Order.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            address=fake.address(),
            postal_code=fake.postcode(),
            city=fake.city(),
            order_json=fake_order_json(),
            status=[status],
            paid=True if next(
                iter(status.keys())
            ) in ["paid", "delivered"] else False,
        )
