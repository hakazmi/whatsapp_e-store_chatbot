# activate_products.py
import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()

sf = Salesforce(
    username=os.getenv("SALESFORCE_USERNAME"),
    password=os.getenv("SALESFORCE_PASSWORD"),
    security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
    domain=os.getenv("SALESFORCE_DOMAIN", "test")
)

print("✅ Connected to Salesforce")

# Get all product IDs
res = sf.query("SELECT Id, Name, IsActive FROM Product2")
for r in res["records"]:
    if not r["IsActive"]:
        sf.Product2.update(r["Id"], {"IsActive": True})
        print(f"🔹 Activated: {r['Name']}")

print("\n🎉 All products are now active!")
