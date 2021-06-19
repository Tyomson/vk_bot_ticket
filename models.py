from pony.orm import Database, Required, Json
try:
    from settings import DB_CONFIG
except ImportError:
    exit('DO cp settings.py.default settings.py and DB_CONFIG!')


db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Состояние пользователя внутри сценария."""
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class Registration(db.Entity):
    """Заявка на билет."""
    context = Required(Json)


# db.drop_table(UserState, if_exists=True)
db.generate_mapping(create_tables=True)
