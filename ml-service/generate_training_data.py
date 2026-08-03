"""
Generates a labeled training dataset for the expense categorization model.
Synthetic data (no real user transactions exist yet), built from realistic
merchant names + bank-statement-style formatting patterns.
"""
import csv
import random

random.seed(42)

MERCHANTS = {
    "Food & Dining": [
        "Starbucks", "McDonald's", "Chipotle", "Trader Joe's", "Whole Foods Market",
        "DoorDash", "Uber Eats", "Pizza Hut", "Subway", "Panera Bread", "Kroger",
        "Safeway", "Chick-fil-A", "Domino's Pizza", "Olive Garden", "Local Diner",
        "Chai Coffee House", "Blue Bottle Coffee", "Cheesecake Factory", "Taco Bell",
    ],
    "Transport": [
        "Uber", "Lyft", "Shell Gas Station", "Chevron", "BP Gas Station",
        "Metro Transit", "Downtown Parking Garage", "Delta Airlines", "United Airlines",
        "Enterprise Rent-A-Car", "Toll Road Authority", "Transit Card Reload",
        "Circle K Fuel", "76 Gas Station", "Amtrak",
    ],
    "Housing & Rent": [
        "Rent Payment", "Zillow Rent Payment", "Greenwood Property Management",
        "Mortgage Payment", "HOA Monthly Fee", "Parkview Apartments", "Sunset Realty Co",
        "Home Warranty Plan", "Renters Insurance",
    ],
    "Utilities": [
        "Pacific Electric Co", "PG&E", "City Water Utility", "Comcast Internet",
        "AT&T Wireless", "Verizon Wireless", "National Gas Utility",
        "Waste Management Trash Service", "Xfinity Cable",
    ],
    "Shopping": [
        "Amazon", "Target", "Walmart", "Best Buy", "Nike", "Nordstrom", "IKEA",
        "Home Depot", "Etsy", "eBay", "Apple Store", "Zara", "H&M", "Costco",
        "Sephora",
    ],
    "Entertainment": [
        "Netflix", "Spotify", "AMC Theatres", "Steam Games", "Disney Plus",
        "HBO Max", "Live Nation Tickets", "Bowling Alley", "PlayStation Store",
        "Xbox Game Pass", "Local Cinema",
    ],
    "Health": [
        "CVS Pharmacy", "Walgreens", "Bright Smile Dental", "Planet Fitness",
        "LA Fitness", "Family Doctor Copay", "Vision Center", "Urgent Care Clinic",
        "Rite Aid Pharmacy", "MyFitness Gym",
    ],
    "Income": [
        "Payroll Deposit", "Direct Deposit Salary", "Acme Corp Payroll",
        "Freelance Client Payment", "Venmo Received", "Tax Refund IRS",
        "Employer Direct Deposit", "Consulting Payment",
    ],
    "Other": [
        "ATM Withdrawal", "Bank Service Fee", "Account Transfer", "Miscellaneous Charge",
        "Check Deposit", "Cash Withdrawal", "Wire Transfer Fee", "Unknown Merchant",
    ],
}

PATTERNS = [
    "{m}", "POS DEBIT {m}", "{m} #{n}", "PAYMENT {m}", "{m} ONLINE",
    "AUTOPAY {m}", "{m} *{n}", "PURCHASE {m}", "{m} - RECURRING", "{m} {city}",
]

CITIES = ["NYC", "SF", "LA", "CHI", "AUSTIN", "SEATTLE", "BOSTON"]


def generate_rows(samples_per_category: int = 45) -> list[tuple[str, str]]:
    rows = []
    for category, merchants in MERCHANTS.items():
        for _ in range(samples_per_category):
            merchant = random.choice(merchants)
            pattern = random.choice(PATTERNS)
            description = pattern.format(
                m=merchant, n=random.randint(1000, 9999), city=random.choice(CITIES)
            )
            if random.random() < 0.3:
                description = description.upper()
            rows.append((description, category))
    random.shuffle(rows)
    return rows


if __name__ == "__main__":
    rows = generate_rows()
    with open("data/training_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["description", "category"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to data/training_data.csv")