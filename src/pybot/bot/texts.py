import textwrap

HELP_PRIVATE = textwrap.dedent(
    """
    Доступные команды (личный чат):
    /start — запуск бота и старт/перезапуск регистрации
    /profile — показать профиль
    /role_request <Student|Mentor|Admin> — запросить роль (для роли Student)
    /help — показать это сообщение
    /info — информация о проекте
    /ping — проверка доступности бота (Student/Admin)

    Команды администратора:
    /broadcast @all <текст> — рассылка всем
    /broadcast <Student|Mentor|Admin> <текст> — рассылка по роли
    /academic_points @user <число> "причина" — изменить академические баллы
    /reputation_points @user <число> "причина" — изменить репутационные баллы
    /addrole @user <Student|Mentor|Admin> "причина" — добавить роль
    /removerole @user <Student|Mentor|Admin> "причина" — снять роль
    """
).strip()

HELP_GROUP = textwrap.dedent(
    """
    Доступные команды (групповой чат):
    /start — приветствие
    /help — показать это сообщение
    /info — информация о проекте
    /ping — проверка доступности бота (Student/Admin)

    Команды администратора:
    /academic_points @user <число> "причина" — изменить академические баллы
    /reputation_points @user <число> "причина" — изменить репутационные баллы
    /addrole @user <Student|Mentor|Admin> "причина" — добавить роль
    /removerole @user <Student|Mentor|Admin> "причина" — снять роль

    Примечание:
    /broadcast доступна только в личном чате с ботом.
    """
).strip()

INFO_GLOBAL = textwrap.dedent(
    """
    Привет!
    Я бот платформы ITAcadem.

    Что уже доступно:
    • регистрация и профиль пользователя;
    • система академических и репутационных баллов;
    • роли и запрос роли у администратора;
    • администраторские рассылки.

    Репозиторий проекта:
    https://github.com/NikkiShuRA/PyBot-ITAcadem.git
    """
).strip()
