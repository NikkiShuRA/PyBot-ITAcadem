from pybot.presentation import web as web_presentation
from pybot.presentation.web.health import main as health_main
from pybot.presentation.web.health.routers.health import health as canonical_health_endpoint
from pybot.presentation.web.health.routers.readiness import ready as canonical_ready_endpoint


def test_web_public_api_reexports_health_contract() -> None:
    assert web_presentation.app is health_main.app
    assert web_presentation.create_app is health_main.create_app
    assert web_presentation.lifespan is health_main.lifespan
    assert web_presentation.main is health_main
    assert web_presentation.health_endpoint is canonical_health_endpoint
    assert web_presentation.ready_endpoint is canonical_ready_endpoint
