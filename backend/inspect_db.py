import sys
import os
sys.path.append(os.getcwd())

try:
    import app.db.database as db_mod
    print(f"Module found: {db_mod.__file__}")
    print(f"Attributes: {dir(db_mod)}")
    if hasattr(db_mod, 'get_db'):
        print("get_db FOUND in app.db.database")
    else:
        print("get_db NOT FOUND in app.db.database")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
