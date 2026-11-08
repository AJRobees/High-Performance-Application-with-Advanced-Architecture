from pathlib import Path

project_dir = Path(__file__).parent


if (project_dir/"data").exists():
    db_data_dir = project_dir/"data"
else:
    (project_dir/"data").mkdir()
    db_data_dir = project_dir/"data"


PRODUCTS_DATABASE_URL = f"sqlite:///./{db_data_dir}/products.db"