import json
import stripe

# Set your Stripe secret key
stripe.api_key = "sk_test_51Nf1FtSE3pf7X1MUw59X8fewN1ZPnydPybisfVVzbkhZx5tPJKGlGDn7zcnOWROjTTSn4qxcEdsa6pEDfHSSnMFt002nAMKENf"

def convert_price_smallest_unit_to_rupees(price_amount, currency):
    if currency == "inr":
        return price_amount / 100  # Convert paise to rupees
    else:
        return price_amount  # For other currencies, no conversion

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

def get_all_products_with_prices_and_subscriptions():
    try:
        products = stripe.Product.list(limit=10)  # Retrieve the first 10 products
        product_data = []

        for product in products.auto_paging_iter():
            prices = get_all_prices(product.id)
            product_prices = []

            for price in prices:
                subscription_type = get_price_subscription_type(price.id)
                price_amount_rupees = convert_price_smallest_unit_to_rupees(price.unit_amount, price.currency)
                product_prices.append({
                    "price_id": price.id,
                    "price_amount": price_amount_rupees,
                    "subscription_type": subscription_type,
                })

            product_data.append({
                "product_name": product.name,
                "prices": product_prices,
            })

        return product_data
    except stripe.error.StripeError as e:
        return {"error": str(e)}

def get_all_prices(product_id):
    try:
        prices = stripe.Price.list(product=product_id)
        return prices.data
    except stripe.error.StripeError as e:
        return []

if __name__ == "__main__":
    product_data = get_all_products_with_prices_and_subscriptions()
    formatted_data = json.dumps(product_data, indent=4)
    print(formatted_data)
