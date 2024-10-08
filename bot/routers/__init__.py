__all__ = ("router",)

from aiogram import Router

from .common_handlers import router as common_router
from .group_handlers import router as group_router
from .schedule_handlers import router as schedule_router
from .settings_handlers import router as settings_router

router = Router(name=__name__)

router.include_routers(
    group_router,
    settings_router,
    schedule_router,
    # end
    common_router,
)
