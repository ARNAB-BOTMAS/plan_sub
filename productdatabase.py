import json
import stripe
import sqlite3

# Set your Stripe secret key
stripe.api_key = "sk_test_51Nf1FtSE3pf7X1MUw59X8fewN1ZPnydPybisfVVzbkhZx5tPJKGlGDn7zcnOWROjTTSn4qxcEdsa6pEDfHSSnMFt002nAMKENf"

def create_database():
    connection = sqlite3.connect("subscription_data.db")
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_subscriptions (
            id INTEGER PRIMARY KEY,
            product_id TEXT,
            product_name TEXT,
            product_quality TEXT,
            product_rag TEXT,
            product_device TEXT,
            price_id TEXT,
            price_amount INTEGER,
            subscription_type TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS yearly_subscriptions (
            id INTEGER PRIMARY KEY,
            product_id TEXT,
            product_name TEXT,
            product_quality TEXT,
            product_rag TEXT,
            product_device TEXT,
            price_id TEXT,
            price_amount INTEGER,
            subscription_type TEXT
        )
    ''')

    connection.commit()
    connection.close()

def convert_price_smallest_unit_to_rupees(price_amount, currency):
    if currency == "inr":
        return price_amount / 100  # Convert paise to rupees
    else:
        return price_amount  # For other currencies, no conversion

def product_quality(product_name):
    if product_name == "Basic":
        quality = ["Good", "480p", "Phone"]
        return quality
    elif product_name == "Standard":
        quality = ["Good", "720p", "Phone+Tablet"]
        return quality
    elif product_name == "Premium":
        quality = ["Better", "1080p", "Phone+Tablet+Computer"]
        return quality
    elif product_name == "Regular":
        quality = ["Best", "4K+HDR", "Phone+Tablet+TV"]
        return quality

def insert_subscription_data(table_name, product_id, product_name, product_qua, product_rag, product_device, price_id, price_amount, subscription_type):
    connection = sqlite3.connect("user.db")
    cursor = connection.cursor()

    cursor.execute(
        f"INSERT INTO {table_name} (product_id, product_name, product_quality, product_rag, product_device, price_id, price_amount, subscription_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (product_id, product_name, product_qua, product_rag, product_device, price_id, price_amount, subscription_type)
    )

    connection.commit()
    connection.close()

def get_all_products_with_prices_and_subscriptions():
    try:
        products = stripe.Product.list(limit=10)  # Retrieve the first 10 products

        for product in products.auto_paging_iter():
            prices = get_all_prices(product.id)

            for price in prices:
                subscription_type = get_price_subscription_type(price.id)
                product_qua = product_quality(product.name)[0]
                product_rag = product_quality(product.name)[1]
                product_device = product_quality(product.name)[2]
                price_amount_rupees = convert_price_smallest_unit_to_rupees(price.unit_amount, price.currency)
                if subscription_type == "monthly":
                    insert_subscription_data(
                        "monthly_subscriptions",
                        product.id,
                        product.name,
                        product_qua,
                        product_rag,
                        product_device,
                        price.id,
                        price_amount_rupees,
                        subscription_type
                    )
                elif subscription_type == "yearly":
                    insert_subscription_data(
                        "yearly_subscriptions",
                        product.id,
                        product.name,
                        product_qua,
                        product_rag,
                        product_device,
                        price.id,
                        price_amount_rupees,
                        subscription_type
                    )

        print("Data saved to database.")
    except stripe.error.StripeError as e:
        print("Error:", str(e))

def get_all_prices(product_id):
    try:
        prices = stripe.Price.list(product=product_id)
        return prices.data
    except stripe.error.StripeError as e:
        return []

def get_price_subscription_type(price_id):
    try:
        price = stripe.Price.retrieve(price_id)
        if price.recurring.interval == "month":
            subscription_type = "monthly"
        elif price.recurring.interval == "year":
            subscription_type = "yearly"
        else:
            subscription_type = "unknown"
        return subscription_type
    except stripe.error.StripeError as e:
        return "error"

if __name__ == "__main__":
    create_database()
    get_all_products_with_prices_and_subscriptions()
