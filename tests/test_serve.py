from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gardena_smartsystem_prometheus_exporter.serve import app


@pytest.mark.asyncio
async def test_lifespan_startup_creates_task():
    messages = [{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}]
    receive = AsyncMock(side_effect=messages)
    send = AsyncMock()

    with patch("gardena_smartsystem_prometheus_exporter.serve.asyncio.create_task") as mock_create_task:
        mock_task = MagicMock()
        mock_create_task.return_value = mock_task

        await app({"type": "lifespan"}, receive, send)

    mock_create_task.assert_called_once()
    send.assert_any_await({"type": "lifespan.startup.complete"})
    send.assert_any_await({"type": "lifespan.shutdown.complete"})


@pytest.mark.asyncio
async def test_lifespan_shutdown_cancels_task():
    messages = [{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}]
    receive = AsyncMock(side_effect=messages)
    send = AsyncMock()

    with patch("gardena_smartsystem_prometheus_exporter.serve.asyncio.create_task") as mock_create_task:
        mock_task = MagicMock()
        mock_create_task.return_value = mock_task

        await app({"type": "lifespan"}, receive, send)

    mock_task.cancel.assert_called_once()


@pytest.mark.asyncio
async def test_http_request_delegated_to_prometheus_app():
    scope = {"type": "http"}
    receive = AsyncMock()
    send = AsyncMock()
    mock_prometheus = AsyncMock()

    with patch("gardena_smartsystem_prometheus_exporter.serve._prometheus_app", mock_prometheus):
        await app(scope, receive, send)

    mock_prometheus.assert_awaited_once_with(scope, receive, send)
