from datetime import datetime
import pandas as pd

from apps.db_model.models import Category, SubCategory, seed


def seed_items():
    df_classify = pd.read_csv("datasets/variable_classification.csv")
    df_categories = df_classify.loc[:,"category"].drop_duplicates()
    seed(
        Category,
        [
            {
                "name": item,
                "created_at": datetime.now(),
            } for item in df_categories
        ],
    )
    seed(
        SubCategory,
        [
            {
                "category_id":item["category_id"],
                "name": item["name"],
                "variable_name": item["sub_cat"],
                "unit":item["unit"],
                "mini_limit":item["min"],
                "maxi_limit":item["max"],
                "created_at": datetime.now(),
            } for index, item in df_classify.iterrows()
        ],
    )
