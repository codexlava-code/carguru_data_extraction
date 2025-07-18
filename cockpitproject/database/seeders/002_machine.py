from apps.db_model.models import Machine, seed


def seed_items():
    seed(
        Machine,
        [
            {
                "machine_name": "vasius",
                "equipment_id": "GENV21G022",
                "company_name": "bobst ltd",
            },
            {
                "machine_name": "volta",
                "equipment_id": "GENV17G017",
                "company_name": "bobst R&D",
            },
        ],
    )
