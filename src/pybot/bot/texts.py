import html
import textwrap
from collections.abc import Sequence

from ..core.constants import PointsTypeEnum, RequestStatus, RoleEnum
from ..dto import CompetenceReadDTO
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
    /broadcast @all <текст> - рассылка всем пользователям
    /broadcast <Student|Mentor|Admin> <текст> - рассылка по роли
    /broadcast <Competence> <текст> - рассылка по компетенции
    /academic_points @user <число> "причина" - изменить академические баллы
    /reputation_points @user <число> "причина" - изменить репутационные баллы
    /addrole @user <Student|Mentor|Admin> "причина" - выдать роль
    /removerole @user <Student|Mentor|Admin> "причина" - снять роль
    /addcompetence @user Python,SQL - добавить компетенции
    /removecompetence @user Python,SQL - удалить компетенции
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
REGISTRATION_CONTACT_STEP = "📱 Поделитесь номером телефона"
REGISTRATION_FIRST_NAME_STEP = "Введите имя"
REGISTRATION_LAST_NAME_STEP = "Введите фамилию"
REGISTRATION_PATRONYMIC_STEP = "Введите отчество"
REGISTRATION_COMPETENCE_STEP = textwrap.dedent(
    """
    Выберите компетенции, которые вам уже знакомы или интересны.

    Этот шаг можно пропустить: потом вы сможете изменить компетенции в профиле.
    """
).strip()
REGISTRATION_VALUE_INVALID = "Пожалуйста, отправьте корректное значение."
REGISTRATION_CONTACT_EMPTY = "Не удалось получить номер телефона. Попробуйте ещё раз через кнопку ниже."
REGISTRATION_CONTACT_ACCEPTED = "Номер получен. Продолжаем регистрацию."
REGISTRATION_ALREADY_EXISTS = "Похоже, профиль уже существует. Ваш ID: {user_id}."
REGISTRATION_INTERNAL_ERROR = "Не удалось завершить регистрацию. Пожалуйста, начните заново с команды /start."
REGISTRATION_PROFILE_CREATED = "✅ Профиль создан. Добро пожаловать, {first_name}!"
REGISTRATION_NAME_EMPTY = "Значение не может быть пустым. Попробуйте ещё раз."
REGISTRATION_NAME_INVALID_SYMBOLS = "Можно использовать только русские буквы и пробелы."
REGISTRATION_NAME_TOO_SHORT = "Значение слишком короткое."
REGISTRATION_NAME_TOO_LONG = "Значение слишком длинное. Максимум {max_length} символов."

START_USER_ERROR = "Не удалось определить пользователя. Пожалуйста, попробуйте ещё раз."
START_GROUP_GREETING = "👋 Бот на связи. Напишите мне в личные сообщения, чтобы зарегистрироваться или открыть профиль."
STALE_DIALOG_MESSAGE = "Это действие уже неактуально. Нажмите /start и попробуйте ещё раз."

PING_ANONYMOUS = "Не удалось определить ваш профиль. Нажмите /start и попробуйте ещё раз."
PING_STATUS = "🏓 Бот работает. {first_name}, ваш статус администратора: {admin_status}."

ROLE_AUTH_ERROR = "Не удалось проверить права. Пожалуйста, начните с команды /start."
ROLE_ACCESS_DENIED = "⛔ У вас недостаточно прав для этого действия."

BROADCAST_USAGE = "Укажите получателя и текст сообщения. Формат: /broadcast @all|Role|Competence <сообщение>"
BROADCAST_MESSAGE_REQUIRED = "Добавьте текст рассылки. Формат: /broadcast @all|Role|Competence <сообщение>"
BROADCAST_UNKNOWN_TARGET = (
    "Не удалось распознать получателя рассылки.\n"
    "Доступные роли: {roles}\n"
    "Доступные компетенции: {competencies}\n"
    "Формат: /broadcast @all|Role|Competence <сообщение>"
)

TARGET_SELECTED_REPLY = "👤 Вы выбрали пользователя через ответ: {target}."
TARGET_SELECTED_MENTION = "👤 Вы выбрали пользователя: {target}."
TARGET_NOT_FOUND = "Пользователь не найден."
TARGET_REQUIRED = "Не удалось определить пользователя. Ответьте на сообщение, укажите @mention или Telegram ID."

ROLE_COMMAND_INVALID_FORMAT = "Не удалось разобрать команду. Проверьте формат и попробуйте ещё раз."
ROLE_REASON_QUOTES_REQUIRED = "Причину нужно указать в кавычках: \"причина\" или 'причина'."
ROLE_NOT_SPECIFIED = "Укажите роль. Доступные роли: {roles}."
ROLE_UNKNOWN = "Такой роли нет. Доступные роли: {roles}."
ROLE_TARGET_REQUIRED = (
    'Укажите пользователя через reply или @mention.\nФормат: /{command} @user <Student|Mentor|Admin> "причина"'
)
ROLE_ADD_SUCCESS = "✅ Роль {role} выдана пользователю {first_name}.\nПричина: {reason}"
ROLE_REMOVE_SUCCESS = "✅ Роль {role} снята у пользователя {first_name}.\nПричина: {reason}"
ROLE_REASON_FALLBACK = "не указана"
ROLE_UNEXPECTED_ERROR = "Не удалось изменить роль. Попробуйте ещё раз позже."

ROLE_REQUEST_USAGE = "Укажите роль. Формат: /role_request <Student|Mentor|Admin>."
ROLE_REQUEST_REJECTED_RECENTLY = "Ваш предыдущий запрос недавно отклонили. Попробуйте немного позже."
ROLE_REQUEST_ALREADY_EXISTS = "У вас уже есть активный запрос на эту роль."
ROLE_REQUEST_ALREADY_ASSIGNED = "Эта роль у вас уже есть."
ROLE_REQUEST_UNEXPECTED_ERROR = "Не удалось обработать запрос на роль. Попробуйте ещё раз позже."
ROLE_REQUEST_CREATED = "⏳ Запрос на роль {role} отправлен администратору."
ROLE_REQUEST_ADMIN_APPROVED = "✅ Запрос одобрен"
ROLE_REQUEST_ADMIN_REJECTED = "❌ Запрос отклонён"
ROLE_REQUEST_ADMIN_ALREADY_PROCESSED = "Запрос уже обработан"
ROLE_REQUEST_ADMIN_NOT_FOUND = "Запрос не найден"
ROLE_REQUEST_ADMIN_ROLE_NOT_FOUND = "Роль не найдена"
ROLE_REQUEST_ADMIN_USER_NOT_FOUND = "Пользователь не найден"
ROLE_REQUEST_ADMIN_ALREADY_ASSIGNED = "Роль уже назначена"
ROLE_REQUEST_USER_STATUS = "Ваша заявка на роль {role} была {status}."
ROLE_REQUEST_ADMIN_NOTIFICATION = (
    "🛡️ Новый запрос на роль\n\nНомер запроса: {request_id}\nРоль: {role_name}\nПользователь: {mention}"
)
ROLE_REQUEST_NOTIFY_APPROVED = "✅ Запрос на роль одобрен."
ROLE_REQUEST_NOTIFY_REJECTED = "❌ Запрос на роль отклонён."
ROLE_REQUEST_NOTIFY_ALREADY_PROCESSED = "Запрос на роль уже обработан."
ROLE_REQUEST_NOTIFY_NOT_FOUND = "Запрос на роль не найден."
ROLE_REQUEST_NOTIFY_ROLE_NOT_FOUND = "Не удалось найти запрошенную роль."
ROLE_REQUEST_NOTIFY_USER_NOT_FOUND = "Не удалось найти пользователя."
ROLE_REQUEST_NOTIFY_ALREADY_ASSIGNED = "У пользователя уже есть эта роль."
ROLE_REQUEST_NOTIFY_UNEXPECTED = "Не удалось обработать запрос. Попробуйте ещё раз позже."
ROLE_REQUEST_COOLDOWN_UNTIL = "Ваш предыдущий запрос недавно отклонили. Повторно отправить запрос можно {available_at}."

COMPETENCE_TARGET_REQUIRED = (
    "Укажите пользователя через reply, text_mention или Telegram ID.\nФормат: /{command} <tg_id|@mention> Python,SQL"
)
COMPETENCE_LIST_REQUIRED = "Укажите список компетенций через запятую. Пример: /{command} 12345 Python,SQL"
COMPETENCE_ADD_SUCCESS = "✅ Пользователю {first_name} добавлены компетенции: {competencies}"
COMPETENCE_REMOVE_SUCCESS = "✅ У пользователя {first_name} удалены компетенции: {competencies}"
COMPETENCE_NONE = "У пользователя {first_name} пока нет компетенций."
COMPETENCE_LIST = "🧩 Компетенции пользователя {first_name}:\n{competence_lines}"
COMPETENCE_CATALOG_EMPTY = "<b>Компетенции:</b>\n\nПока в системе нет доступных компетенций."
COMPETENCE_CATALOG = "<b>Компетенции:</b>\n\n{competence_lines}"
COMPETENCE_DESCRIPTION_FALLBACK = "Описание не указано"
COMPETENCE_VALIDATION_ERROR = "Не удалось обработать список компетенций: {details}"
COMPETENCE_UNEXPECTED_ERROR = "Не удалось обработать компетенции. Попробуйте ещё раз позже."

POINTS_COMMAND_INVALID_FORMAT = "Не удалось разобрать команду. Проверьте формат и попробуйте ещё раз."
POINTS_AMOUNT_REQUIRED = "Укажите количество баллов числом."
POINTS_REASON_QUOTES_REQUIRED = "Причину нужно указать в кавычках: \"причина\" или 'причина'."
POINTS_OPERATION_FAILED = "Не удалось изменить баллы. Попробуйте ещё раз позже."
POINTS_UNEXPECTED_ERROR = "Произошла непредвиденная ошибка. Попробуйте ещё раз позже."
POINTS_INVALID_VALUE = "Некорректное значение баллов: {value}."
POINTS_CHANGE_SUCCESS = "✅ Баллы обновлены для пользователя {target_id}: {points}.{reason_text}"
POINTS_NOTIFICATION = "📈 Пользователь {giver_name} {action} вам {points_amount} {points_label} баллов.{reason_text}"
POINTS_REASON_LINE = "\nПричина: {reason}"


def button_cancel() -> str:
    return BUTTON_CANCEL


def button_back() -> str:
    return BUTTON_BACK


def button_skip() -> str:
    return BUTTON_SKIP


def registration_existing_profile(user_id: int) -> str:
    return REGISTRATION_ALREADY_EXISTS.format(user_id=user_id)


def registration_profile_created(first_name: str) -> str:
    return REGISTRATION_PROFILE_CREATED.format(first_name=first_name)


def registration_name_too_long(max_length: int) -> str:
    return REGISTRATION_NAME_TOO_LONG.format(max_length=max_length)


def ping_status(first_name: str, is_admin: bool) -> str:
    admin_status = "да" if is_admin else "нет"
    return PING_STATUS.format(first_name=first_name, admin_status=admin_status)


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


def competence_validation_error(details: str) -> str:
    return COMPETENCE_VALIDATION_ERROR.format(details=details)


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


def points_change_success(target_id: int, points: Points, reason: str | None) -> str:
    reason_text = f" Причина: {reason}" if reason else ""
    return POINTS_CHANGE_SUCCESS.format(target_id=target_id, points=points.value, reason_text=reason_text)


def points_invalid_value(value: object) -> str:
    return POINTS_INVALID_VALUE.format(value=value)


def profile_section(title: str, level_name: str, progress_bar: str, points: Points) -> str:
    return textwrap.dedent(
        f"""
        {title}
        {level_name}
        {progress_bar}
        Всего баллов: {points.value}
        """
    ).strip()


def profile_message(first_name: str, academic_section: str, reputation_section: str) -> str:
    return textwrap.dedent(
        f"""
        👋 Здравствуйте, {first_name}!

        {academic_section}

        {reputation_section}

        Обновить профиль: /profile
        Посмотреть команды: /help
        """
    ).strip()


def _format_competence_catalog_line(competence: CompetenceReadDTO) -> str:
    description = competence.description or COMPETENCE_DESCRIPTION_FALLBACK
    return f"<b>{html.escape(competence.name)}</b>: {html.escape(description)}."
