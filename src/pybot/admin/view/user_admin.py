from typing import ClassVar

from sqladmin import ModelView

from ...db.models import User


class UserAdmin(ModelView, model=User):
    """
    Admin interface for User model.
    """

    column_list: ClassVar[list] = [
        User.id,
        User.first_name,
        User.last_name,
        User.patronymic,
    ]
    column_searchable_list: ClassVar[list] = [User.first_name, User.last_name, User.patronymic]
    column_sortable_list: ClassVar[list] = [User.id, User.first_name, User.last_name, User.patronymic]
    can_create: ClassVar[bool] = True  # Разрешаем создание записей
    can_edit: ClassVar[bool] = True  # Разрешаем редактирование
    can_delete: ClassVar[bool] = True  # Разрешаем удаление
    can_view_details: ClassVar[bool] = True  # Разрешаем просмотр деталей
