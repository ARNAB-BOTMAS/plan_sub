import sqlite3

def retrieve_data_from_table(table_name):
    connection = sqlite3.connect("subscription_data.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()

    connection.close()
    return data

def display_subscription_data(data):
    for row in data:
        print("Product ID:", row[1])
        print("Product Name:", row[2])
        print("Product Name:", row[3])
        print("Product Name:", row[4])
        print("Product Name:", row[5])
        print("Price ID:", row[6])
        print("Price:", row[7])
        print("Subscription Type:", row[8])
        print()

if __name__ == "__main__":
    monthly_data = retrieve_data_from_table("monthly_subscriptions")
    yearly_data = retrieve_data_from_table("yearly_subscriptions")

    print("Monthly Subscriptions:")
    display_subscription_data(monthly_data)

    print("Yearly Subscriptions:")
    display_subscription_data(yearly_data)
