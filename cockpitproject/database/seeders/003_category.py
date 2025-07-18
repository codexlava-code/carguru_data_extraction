import csv
from datetime import datetime
from apps.db_model.models import Category, SubCategory, seed


def seed_items():
    with open("datasets/variable_classification.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        categories = set()
        subcategories = []

        for row in reader:
            category_name = row["category"]
            if category_name not in categories:
                categories.add(category_name)
                seed(Category, [{"name": category_name, "created_at": datetime.now()}])

            subcategories.append({
                "category_id": Category.get(Category.name == category_name).id,
                "name": row["sub_cat"],
                "variable_name": row["sub_cat"],
                "unit": row["unit"],
                "mini_limit": row["min"],
                "maxi_limit": row["max"],
                "created_at": datetime.now()
            })

        seed(SubCategory, subcategories)
