import stripe
from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def create_stripe_product(course):
    return stripe.Product.create(name=course)


def create_stripe_price(amount, pay_course):

    return stripe.Price.create(
        currency="rub",
        unit_amount=int(amount * 100),
        product_data={"name": pay_course['id']},
    )


def create_stripe_session(price):
    session = stripe.checkout.Session.create(
        success_url="http://localhost:8000/success",
        line_items=[{"price": price.get('id'), "quantity": 1}],
        mode="payment",
    )
    return session

