import html
import re
import textwrap
from collections.abc import Sequence

from ..core.constants import PointsTypeEnum, RequestStatus, RoleEnum
from ..dto import CompetenceReadDTO, ProfileViewDTO
from ..dto.value_objects import Points

REPOSITORY_URL = "https://github.com/NikkiShuRA/PyBot-ITAcadem.git"
AVAILABLE_ROLES = ", ".join(role.value for role in RoleEnum)

BUTTON_CONTINUE = "Продолжить"
BUTTON_CANCEL = "Отмена"
BUTTON_BACK = "Назад"
BUTTON_SKIP = "Пропустить"
BUTTON_FINISH_REGISTRATION = "Завершить регистрацию"
BUTTON_SEND_CONTACT = "Поделиться номером"
BUTTON_APPROVE = "Одобрить"
BUTTON_REJECT = "Отклонить"

HELP_PRIVATE = textwrap.dedent(
    """
    Доступные команды в личном чате:
    /start - открыть приветствие и регистрацию
    /profile - показать ваш профиль
    /role_request <Student|Mentor|Admin> - отправить запрос на роль
    /help - показать эту подсказку
    /info - рассказать о проекте
    /ping - проверить, что бот работает
    /competences - показать все компетенции в системе
    /showcompetences [@user|id|reply] - показать компетенции пользователя

    Команды для администраторов:

    Рассылка:
    /broadcast @all <текст> - рассылка всем пользователям
    /broadcast <Student|Mentor|Admin> <текст> - рассылка по роли
    /broadcast <Competence> <текст> - рассылка по компетенции

    Работа с баллами:
    /academic_points @user <число> "причина" - изменить академические баллы
    /reputation_points @user <число> "причина" - изменить репутационные баллы

    Работа с ролями:
    /addrole @user <Student|Mentor|Admin> "причина" - выдать роль
    /removerole @user <Student|Mentor|Admin> "причина" - снять роль

    Работа с компетенциями:
    /addcompetence @user Python,SQL - добавить компетенции
    /removecompetence @user Python,SQL - удалить компетенции
    """
).strip()

HELP_PRIVATE_PUBLIC = textwrap.dedent(
    """
    Доступные команды в личном чате:
    /start - открыть приветствие и регистрацию
    /profile - показать ваш профиль
    /role_request <Student|Mentor|Admin> - отправить запрос на роль
    /help - показать эту подсказку
    /info - рассказать о проекте
    /ping - проверить, что бот работает
    /competences - показать все компетенции в системе
    /showcompetences [@user|id|reply] - показать компетенции пользователя
    """
).strip()


HELP_GROUP = textwrap.dedent(
    """
    Доступные команды в группе:
    /start - короткое приветствие
    /help - показать эту подсказку
    /info - рассказать о проекте
    /ping - проверить, что бот работает
    /competences - показать все компетенции в системе
    /showcompetences [@user|id|reply] - показать компетенции пользователя

    Важно:
    /broadcast доступна только в личном чате с ботом.
    """
).strip()

INFO_GLOBAL = textwrap.dedent(
    f"""
    Привет! Я бот платформы ITAcadem.

    Уже сейчас я умею:
    - помогать с регистрацией и профилем;
    - показывать академические и репутационные баллы;
    - принимать запросы на роли;
    - поддерживать администраторские рассылки.

    Репозиторий проекта:
    {REPOSITORY_URL}
    """
).strip()

REGISTRATION_WELCOME = textwrap.dedent(
    """
    Привет! Я помогу вам зарегистрироваться в ITAcadem.

    После регистрации вы сможете пользоваться возможностями платформы прямо в Telegram.

    Нажмите «Продолжить», и я попрошу ваш номер телефона.
    """
).strip()

REGISTRATION_CONTACT_PROMPT = "Чтобы продолжить регистрацию, поделитесь номером телефона с помощью кнопки ниже."
REGISTRATION_CONTACT_STEP = "Шаг 1/5. 📱 Поделитесь номером телефона"
REGISTRATION_FIRST_NAME_STEP = "Шаг 2/5. Введите имя"
REGISTRATION_LAST_NAME_STEP = "Шаг 3/5. Введите фамилию"
REGISTRATION_PATRONYMIC_STEP = "Шаг 4/5. Введите отчество"
REGISTRATION_COMPETENCE_STEP = textwrap.dedent(
    """
    Шаг 5/5. Выберите компетенции, которые вам уже знакомы или интересны.

    Этот шаг можно пропустить: потом вы сможете изменить компетенции в профиле.
    """
).strip()
REGISTRATION_VALUE_INVALID = (
    "Не удалось обработать это сообщение.\nОтправьте значение, которое запрашивается на текущем шаге регистрации."
)
REGISTRATION_CONTACT_EMPTY = (
    "Не удалось получить номер телефона.\nНажмите кнопку ниже и отправьте именно контакт, а не обычное сообщение."
)
REGISTRATION_CONTACT_ACCEPTED = "Номер получен. Продолжаем регистрацию."
REGISTRATION_ALREADY_EXISTS = "Похоже, вы уже зарегистрированы.\nОткройте профиль командой /profile."
REGISTRATION_INTERNAL_ERROR = "Не удалось завершить регистрацию.\nНачните её заново с команды /start."
REGISTRATION_PROFILE_CREATED = "✅ Профиль создан. Добро пожаловать, {first_name}!"
REGISTRATION_NAME_EMPTY = "Поле осталось пустым.\nВведите значение текстом."
REGISTRATION_NAME_INVALID_SYMBOLS = "Не удалось принять это значение.\nИспользуйте только русские буквы и пробелы."
REGISTRATION_NAME_TOO_SHORT = "Значение получилось слишком коротким.\nВведите полное имя без сокращений."
REGISTRATION_NAME_TOO_LONG = "Значение получилось слишком длинным.\nСократите ввод до {max_length} символов."

START_USER_ERROR = "Не удалось определить пользователя.\nПопробуйте ещё раз или начните заново с команды /start."
START_GROUP_GREETING = "👋 Бот на связи. Напишите мне в личные сообщения, чтобы зарегистрироваться или открыть профиль."
STALE_DIALOG_MESSAGE = "Это действие уже неактуально.\nНажмите /start и начните сценарий заново."

PING_ANONYMOUS = "Не удалось определить ваш профиль.\nНажмите /start, чтобы бот заново нашёл или создал ваш профиль."
PING_STATUS = "🏓 Бот работает. Рад вас видеть, {first_name}!{role_hint}"

ROLE_AUTH_ERROR = "Не удалось проверить ваши права.\nНажмите /start, чтобы бот заново определил ваш профиль."
ROLE_ACCESS_DENIED = (
    "⛔ Не удалось выполнить это действие: у вас недостаточно прав.\n"
    "Используйте аккаунт с нужной ролью или обратитесь к администратору."
)

BROADCAST_USAGE = (
    "Не удалось определить получателя и текст рассылки.\n"
    "Используйте формат: /broadcast @all|Role|Competence <сообщение>"
)
BROADCAST_MESSAGE_REQUIRED = (
    "Не удалось отправить рассылку без текста.\n"
    "Добавьте сообщение после получателя: /broadcast @all|Role|Competence <сообщение>"
)
BROADCAST_UNKNOWN_TARGET = (
    "Не удалось распознать получателя рассылки.\n"
    "Используйте @all, одну из ролей или существующую компетенцию.\n"
    "Доступные роли: {roles}\n"
    "Доступные компетенции: {competencies}\n"
    "Формат: /broadcast @all|Role|Competence <сообщение>"
)

TARGET_SELECTED_REPLY = "👤 Пользователь выбран: {target}."
TARGET_SELECTED_MENTION = "👤 Пользователь выбран: {target}."
TARGET_NOT_FOUND = (
    "Не удалось найти пользователя.\n"
    "Проверьте @mention или Telegram ID, либо ответьте на сообщение нужного пользователя."
)
TARGET_REQUIRED = (
    "Не удалось определить пользователя для команды.\nОтветьте на сообщение, укажите @mention или Telegram ID."
)

ROLE_COMMAND_INVALID_FORMAT = "Не удалось разобрать команду.\nПроверьте формат команды и попробуйте ещё раз."
ROLE_REASON_QUOTES_REQUIRED = "Не удалось распознать причину.\nУкажите её в кавычках: \"причина\" или 'причина'."
ROLE_NOT_SPECIFIED = "Не удалось определить роль.\nУкажите одну из ролей: {roles}."
ROLE_UNKNOWN = "Не удалось распознать роль.\nИспользуйте одну из доступных ролей: {roles}."
ROLE_TARGET_REQUIRED = (
    "Не удалось определить пользователя для команды.\n"
    'Укажите пользователя через reply или @mention.\nФормат: /{command} @user <Student|Mentor|Admin> "причина"'
)
ROLE_ADD_SUCCESS = "✅ Роль {role} выдана пользователю {first_name}.\nПричина: {reason}"
ROLE_REMOVE_SUCCESS = "✅ Роль {role} снята у пользователя {first_name}.\nПричина: {reason}"
ROLE_REASON_FALLBACK = "не указана"
ROLE_UNEXPECTED_ERROR = "Не удалось изменить роль.\nПопробуйте ещё раз позже."

ROLE_REQUEST_USAGE = (
    "Не удалось определить роль для запроса.\nИспользуйте формат: /role_request <Student|Mentor|Admin>."
)
ROLE_REQUEST_REJECTED_RECENTLY = (
    "Не удалось отправить новый запрос: предыдущий отклонили совсем недавно.\n"
    "Подождите немного и попробуйте ещё раз позже."
)
ROLE_REQUEST_ALREADY_EXISTS = (
    "Не удалось создать новый запрос: у вас уже есть активная заявка на эту роль.\nДождитесь решения администратора."
)
ROLE_REQUEST_ALREADY_ASSIGNED = (
    "Не удалось создать запрос: эта роль у вас уже есть.\nВыберите другую роль, если это нужно."
)
ROLE_REQUEST_UNEXPECTED_ERROR = "Не удалось обработать запрос на роль.\nПопробуйте ещё раз позже."
ROLE_REQUEST_CREATED = "⏳ Запрос на роль {role} отправлен администратору."
ROLE_REQUEST_ADMIN_APPROVED = "✅ Запрос одобрен"
ROLE_REQUEST_ADMIN_REJECTED = "❌ Запрос отклонён"
ROLE_REQUEST_ADMIN_ALREADY_PROCESSED = "Запрос уже обработан.\nОбновите список заявок, чтобы увидеть актуальный статус."
ROLE_REQUEST_ADMIN_NOT_FOUND = "Не удалось найти запрос.\nОбновите список заявок и попробуйте ещё раз."
ROLE_REQUEST_ADMIN_ROLE_NOT_FOUND = (
    "Не удалось обработать запрос: роль не найдена.\n"
    "Проверьте доступные роли и попросите пользователя создать новый запрос."
)
ROLE_REQUEST_ADMIN_USER_NOT_FOUND = (
    "Не удалось обработать запрос: пользователь не найден.\n"
    "Попросите пользователя пройти /start и отправить запрос заново."
)
ROLE_REQUEST_ADMIN_ALREADY_ASSIGNED = (
    "Не удалось обработать запрос: роль уже назначена.\nОбновите список заявок, чтобы увидеть актуальный статус."
)
ROLE_REQUEST_USER_STATUS = "Ваша заявка на роль {role} была {status}."
ROLE_REQUEST_ADMIN_NOTIFICATION = "🛡️ Новый запрос на роль\n\nРоль: {role_name}\nПользователь: {mention}"
ROLE_REQUEST_NOTIFY_APPROVED = "✅ Запрос на роль одобрен."
ROLE_REQUEST_NOTIFY_REJECTED = "❌ Запрос на роль отклонён."
ROLE_REQUEST_NOTIFY_ALREADY_PROCESSED = (
    "Запрос на роль уже обработан.\nОбновите список заявок, чтобы увидеть актуальный статус."
)
ROLE_REQUEST_NOTIFY_NOT_FOUND = "Не удалось найти запрос на роль.\nОбновите список заявок и попробуйте ещё раз."
ROLE_REQUEST_NOTIFY_ROLE_NOT_FOUND = (
    "Не удалось найти запрошенную роль.\nПроверьте доступные роли и попросите пользователя создать новый запрос."
)
ROLE_REQUEST_NOTIFY_USER_NOT_FOUND = (
    "Не удалось найти пользователя.\nПопросите его пройти /start и отправить запрос заново."
)
ROLE_REQUEST_NOTIFY_ALREADY_ASSIGNED = (
    "У пользователя уже есть эта роль.\nОбновите список заявок, чтобы увидеть актуальный статус."
)
ROLE_REQUEST_NOTIFY_UNEXPECTED = "Не удалось обработать запрос.\nПопробуйте ещё раз позже."
ROLE_REQUEST_COOLDOWN_UNTIL = "Ваш предыдущий запрос недавно отклонили. Повторно отправить запрос можно {available_at}."

COMPETENCE_TARGET_REQUIRED = (
    "Не удалось определить пользователя для команды.\n"
    "Укажите пользователя через reply, text_mention или Telegram ID.\n"
    "Формат: /{command} <tg_id|@mention> Python,SQL"
)
COMPETENCE_LIST_REQUIRED = (
    "Не удалось определить список компетенций.\nУкажите их через запятую, например: /{command} 12345 Python,SQL"
)
COMPETENCE_ADD_SUCCESS = "✅ Пользователю {first_name} добавлены компетенции: {competencies}"
COMPETENCE_REMOVE_SUCCESS = "✅ У пользователя {first_name} удалены компетенции: {competencies}"
COMPETENCE_NONE = "У пользователя {first_name} пока нет компетенций."
COMPETENCE_LIST = "🧩 Компетенции пользователя {first_name}:\n{competence_lines}"
COMPETENCE_CATALOG_EMPTY = "<b>Компетенции:</b>\n\nПока в системе нет доступных компетенций."
COMPETENCE_CATALOG = "<b>Компетенции:</b>\n\n{competence_lines}"
COMPETENCE_DESCRIPTION_FALLBACK = "Описание не указано"
COMPETENCE_VALIDATION_ERROR = (
    "Не удалось обработать список компетенций.\nИспользуйте существующие названия через запятую, например: Python, SQL."
)
COMPETENCE_MISSING_NAMES_ERROR = (
    "Не удалось найти компетенции: {names}.\n"
    "Проверьте названия и укажите существующие компетенции через запятую, например: Python, SQL."
)
COMPETENCE_UNEXPECTED_ERROR = "Не удалось обработать компетенции.\nПопробуйте ещё раз позже."

POINTS_COMMAND_INVALID_FORMAT = (
    "Не удалось разобрать команду изменения баллов.\n"
    'Используйте формат: /academic_points @user <число> "причина" или /reputation_points @user <число> "причина".'
)
POINTS_AMOUNT_REQUIRED = "Не удалось определить количество баллов.\nУкажите целое число после пользователя."
POINTS_REASON_QUOTES_REQUIRED = (
    "Не удалось распознать причину изменения баллов.\nУкажите её в кавычках: \"причина\" или 'причина'."
)
POINTS_OPERATION_FAILED = "Не удалось изменить баллы.\nПопробуйте ещё раз позже."
POINTS_UNEXPECTED_ERROR = "Произошла непредвиденная ошибка.\nПопробуйте ещё раз позже."
POINTS_INVALID_VALUE = "Не удалось изменить баллы: значение {value} некорректно.\nУкажите целое число, отличное от 0."
POINTS_CHANGE_SUCCESS = "✅ Баллы обновлены для {target_name}: {points}.{reason_text}"
POINTS_NOTIFICATION = "📈 Пользователь {giver_name} {action} вам {points_amount} {points_label} баллов.{reason_text}"
POINTS_REASON_LINE = "\nПричина: {reason}"


def button_cancel() -> str:
    return BUTTON_CANCEL


def button_back() -> str:
    return BUTTON_BACK


def button_skip() -> str:
    return BUTTON_SKIP


def registration_existing_profile(_user_id: int) -> str:
    return REGISTRATION_ALREADY_EXISTS


def registration_profile_created(first_name: str) -> str:
    return REGISTRATION_PROFILE_CREATED.format(first_name=first_name)


def registration_name_too_long(max_length: int) -> str:
    return REGISTRATION_NAME_TOO_LONG.format(max_length=max_length)


def ping_status(first_name: str, is_admin: bool) -> str:
    role_hint = " У вас есть доступ к командам администратора." if is_admin else ""
    return PING_STATUS.format(first_name=first_name, role_hint=role_hint)


def target_selected_reply(target: str) -> str:
    return TARGET_SELECTED_REPLY.format(target=target)


def target_selected_mention(target: str) -> str:
    return TARGET_SELECTED_MENTION.format(target=target)


def role_not_specified() -> str:
    return ROLE_NOT_SPECIFIED.format(roles=AVAILABLE_ROLES)


def role_unknown() -> str:
    return ROLE_UNKNOWN.format(roles=AVAILABLE_ROLES)


def role_target_required(command_name: str) -> str:
    return ROLE_TARGET_REQUIRED.format(command=command_name)


def role_add_success(first_name: str, role_name: str, reason: str | None) -> str:
    return ROLE_ADD_SUCCESS.format(first_name=first_name, role=role_name, reason=reason or ROLE_REASON_FALLBACK)


def role_remove_success(first_name: str, role_name: str, reason: str | None) -> str:
    return ROLE_REMOVE_SUCCESS.format(first_name=first_name, role=role_name, reason=reason or ROLE_REASON_FALLBACK)


def role_request_created(role_name: str) -> str:
    return ROLE_REQUEST_CREATED.format(role=role_name)


def role_request_cooldown_until(available_at: str) -> str:
    return ROLE_REQUEST_COOLDOWN_UNTIL.format(available_at=available_at)


def role_request_user_status(role_name: str, status: RequestStatus) -> str:
    status_text_map = {
        RequestStatus.APPROVED: "одобрена",
        RequestStatus.REJECTED: "отклонена",
        RequestStatus.PENDING: "принята в работу",
        RequestStatus.CANCELED: "отменена",
    }
    return ROLE_REQUEST_USER_STATUS.format(role=role_name, status=status_text_map.get(status, status.value))


def role_request_admin_notification(request_id: int, role_name: str, mention: str) -> str:
    return ROLE_REQUEST_ADMIN_NOTIFICATION.format(request_id=request_id, role_name=role_name, mention=mention)


def role_request_admin_notification_with_status(message_text: str | None, status_text: str) -> str:
    base_text = (message_text or "").strip()
    status_block_pattern = re.compile(r"\n\n<b>Статус:</b> .+\Z", re.DOTALL)
    clean_text = status_block_pattern.sub("", base_text).strip()
    status_block = f"<b>Статус:</b> {html.escape(status_text)}"

    if not clean_text:
        return status_block
    return f"{clean_text}\n\n{status_block}"


def competence_target_required(command_name: str) -> str:
    return COMPETENCE_TARGET_REQUIRED.format(command=command_name)


def competence_list_required(command_name: str) -> str:
    return COMPETENCE_LIST_REQUIRED.format(command=command_name)


def competence_add_success(first_name: str, competence_names: Sequence[str]) -> str:
    return COMPETENCE_ADD_SUCCESS.format(first_name=first_name, competencies=", ".join(competence_names))


def competence_remove_success(first_name: str, competence_names: Sequence[str]) -> str:
    return COMPETENCE_REMOVE_SUCCESS.format(first_name=first_name, competencies=", ".join(competence_names))


def competence_none(first_name: str) -> str:
    return COMPETENCE_NONE.format(first_name=first_name)


def competence_list(first_name: str, competencies: Sequence[CompetenceReadDTO]) -> str:
    competence_lines = "\n".join(f"- {competence.name}" for competence in competencies)
    return COMPETENCE_LIST.format(first_name=first_name, competence_lines=competence_lines)


def competence_catalog(competencies: Sequence[CompetenceReadDTO]) -> str:
    if not competencies:
        return COMPETENCE_CATALOG_EMPTY

    competence_lines = "\n".join(_format_competence_catalog_line(competence) for competence in competencies)
    return COMPETENCE_CATALOG.format(competence_lines=competence_lines)


def competence_validation_error() -> str:
    return COMPETENCE_VALIDATION_ERROR


def competence_missing_names_error(missing_names: Sequence[str]) -> str:
    return COMPETENCE_MISSING_NAMES_ERROR.format(names=", ".join(missing_names))


def broadcast_unknown_target(competencies: Sequence[CompetenceReadDTO]) -> str:
    competences_list = ", ".join(competence.name for competence in competencies) or "нет доступных"
    return BROADCAST_UNKNOWN_TARGET.format(roles=AVAILABLE_ROLES, competencies=competences_list)


def points_label(points_type: PointsTypeEnum) -> str:
    match points_type:
        case PointsTypeEnum.ACADEMIC:
            return "академических"
        case PointsTypeEnum.REPUTATION:
            return "репутационных"
        case _:
            return "учебных"


def points_reason_line(reason: str | None) -> str:
    if not reason:
        return ""
    return POINTS_REASON_LINE.format(reason=reason)


def points_notification(points: Points, points_type: PointsTypeEnum, giver_name: str, reason: str | None) -> str:
    action = "начислил" if points.is_positive() else "снял"
    return POINTS_NOTIFICATION.format(
        giver_name=giver_name,
        action=action,
        points_amount=abs(points.value),
        points_label=points_label(points_type),
        reason_text=points_reason_line(reason),
    )


def points_change_success(target_name: str, points: Points, reason: str | None) -> str:
    reason_text = f" Причина: {reason}" if reason else ""
    return POINTS_CHANGE_SUCCESS.format(target_name=target_name, points=points.value, reason_text=reason_text)


def points_invalid_value(value: object) -> str:
    return POINTS_INVALID_VALUE.format(value=value)


def profile_point_section(title: str, level_name: str, progress_bar: str, points: Points) -> str:
    return "\n".join([title, level_name, progress_bar, f"Всего баллов: {points.value}"])


def profile_empty_section(title: str) -> str:
    return "\n".join([title, "Пока не указаны"])


def profile_competence_section(title: str, competencies: Sequence[CompetenceReadDTO]) -> str:
    competence_lines = "\n".join(_format_competence_catalog_line(competence) for competence in competencies)
    return "\n".join([title, competence_lines])


def profile_roles_section(title: str, roles: Sequence[str]) -> str:
    role_lines = "\n".join(f"- {role}" for role in roles)
    return "\n".join([title, role_lines])


def profile_message(
    first_name: str, academic_section: str, reputation_section: str, roles_section: str, competencies_section: str
) -> str:
    return "\n\n".join(
        [
            f"👋 Здравствуйте, {first_name}!",
            academic_section,
            reputation_section,
            roles_section,
            competencies_section,
            "Обновить профиль: /profile\nПосмотреть команды: /help",
        ]
    )


def render_profile_message(user_profile_data: ProfileViewDTO) -> str:
    academic_section = profile_point_section(
        title="<b>📘 Академический уровень</b>",
        level_name=user_profile_data.academic_level.current_level.name,
        progress_bar=user_profile_data.academic_progress_bar,
        points=user_profile_data.academic_progress,
    )
    reputation_section = profile_point_section(
        title="<b>⭐ Репутационный уровень</b>",
        level_name=user_profile_data.reputation_level.current_level.name,
        progress_bar=user_profile_data.reputation_progress_bar,
        points=user_profile_data.reputation_progress,
    )
    roles_section = (
        profile_roles_section(
            title="<b>🎭 Роли</b>",
            roles=user_profile_data.roles_data,
        )
        if user_profile_data.roles_data != []
        else profile_empty_section("<b>🎭 Роли</b>")
    )
    competencies_section = (
        profile_competence_section(
            title="<b>🧩 Компетенции</b>",
            competencies=user_profile_data.competences,
        )
        if user_profile_data.competences != []
        else profile_empty_section("<b>🧩 Компетенции</b>")
    )
    return profile_message(
        first_name=user_profile_data.user.first_name,
        academic_section=academic_section,
        reputation_section=reputation_section,
        roles_section=roles_section,
        competencies_section=competencies_section,
    )


def _format_competence_catalog_line(competence: CompetenceReadDTO) -> str:
    description = competence.description or COMPETENCE_DESCRIPTION_FALLBACK
    return f"<b>{html.escape(competence.name)}</b>: {html.escape(description)}."
