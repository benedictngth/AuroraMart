import os
import django
import csv
from decimal import Decimal

# --- 1. Django Setup ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auroramartproj.settings')
django.setup()

from onlinestore.models import Product, Category, Subcategory

# --- Configuration ---
CSV_FILE_PATH = '/Users/zeevierrrr/Downloads/IS2108 - AY2526S1 - Pair Project/data/b2c_products_500.csv'

def load_raw_data(file_path):
    """Loads CSV data into a list of dictionaries using the built-in csv module."""
    raw_data = []
    try:
        # Open file and use DictReader to map columns to dictionary keys
        with open(file_path, mode='r', encoding='cp1252') as file:
            reader = csv.DictReader(file)
            for row in reader:
                raw_data.append(row)
        return raw_data
    except FileNotFoundError:
        print(f"Error: CSV file not found at {file_path}")
        return None


def import_ecom_data():
    raw_data = load_raw_data(CSV_FILE_PATH)
    if raw_data is None:
        return

    print(f"Loaded {len(raw_data)} rows from CSV.")
    
    # Dictionaries to hold mappings (Name -> ID)
    category_map = {}
    subcategory_map = {}

    # --- STAGE 1: Import Categories ---
    
    unique_categories = set()
    for row in raw_data:
        unique_categories.add(row['Product Category'])
    
    categories_to_create = [
        Category(category_name=name) for name in unique_categories
    ]
    # Use bulk_create with ignore_conflicts for efficiency and safety
    Category.objects.bulk_create(categories_to_create, ignore_conflicts=True)
    
    # Populate map for lookups
    category_map = {c.category_name: c for c in Category.objects.all()}
    print(f"Stage 1: Processed {len(category_map)} Categories.")

    # --- STAGE 2: Import Subcategories ---
    
    unique_subcategories = set()
    for row in raw_data:
        category_name = row['Product Category']
        subcategory_name = row['Product Subcategory']
        # Store as a tuple (Category Name, Subcategory Name)
        unique_subcategories.add((category_name, subcategory_name))

    subcategories_to_create = []
    for cat_name, subcat_name in unique_subcategories:
        parent_category = category_map.get(cat_name)
        if parent_category:
            subcategories_to_create.append(
                Subcategory(
                    category=parent_category, 
                    subcategory_name=subcat_name
                )
            )
    
    Subcategory.objects.bulk_create(subcategories_to_create, ignore_conflicts=True)
    
    # Populate map for lookups
    # Map key will be (Category ID, Subcategory Name) -> Subcategory ID for uniqueness
    subcategory_map = {
        (s.category_id, s.subcategory_name): s.id 
        for s in Subcategory.objects.all()
    }
    print(f"Stage 2: Processed {len(subcategory_map)} Subcategories.")

    # --- STAGE 3: Import Products ---
    
    products_to_create = []
    
    for row in raw_data:
        try:
            category_obj = category_map.get(row['Product Category'])
            if not category_obj: continue 

            # Use the Category ID and Subcategory Name to look up the Subcategory ID
            subcat_id = subcategory_map.get(
                (category_obj.id, row['Product Subcategory'])
            )
            if not subcat_id: continue

            # Clean and prepare values
            rating_str = row.get('Product rating')
            rating = float(rating_str) if rating_str else None

            product = Product(
                sku_code=row['SKU code'],
                product_name=row['Product name'],
                product_description=row['Product description'],
                unit_price=Decimal(row['Unit price']),
                product_rating=rating,
                quantity_on_hand=int(row['Quantity on hand']),
                reorder_quantity=int(row['Reorder Quantity']),
                
                # Link Foreign Keys using IDs
                category_id=category_obj.id,
                subcategory_id=subcat_id
            )
            products_to_create.append(product)
            
        except Exception as e:
            print(f"Skipping row due to error: {e} in row {row.get('Product name')}")

    # Final bulk creation
    new_products = Product.objects.bulk_create(products_to_create, ignore_conflicts=True)
    print(f"Stage 3: Successfully imported {len(new_products)} new Products.")


if __name__ == "__main__":
    import_ecom_data()