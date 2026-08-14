import pytest

from config.credentials import ADMIN_INVITE_CODE, MANAGER_INVITE_CODE
from config.db import DB_PASSWORD

requires_admin = pytest.mark.skipif(
    not ADMIN_INVITE_CODE,
    reason="в .env нет инвайт-кода для админа, админские тесты пропускаем"
)

requires_manager = pytest.mark.skipif(
    not MANAGER_INVITE_CODE,
    reason="в .env нет инвайт-кода для менеджера, менеджерские тесты пропускаем"
)

requires_db = pytest.mark.skipif(
    not DB_PASSWORD,
    reason="в .env нет DB_PASSWORD - тесты с базой пропускаем",
)