import asyncio

import pytest

from podcast_generator.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
)


def test_circuit_breaker_returns_successful_result_and_stays_closed():
    async def scenario():
        breaker = CircuitBreaker(CircuitBreakerConfig(timeout=1))

        async def operation():
            return "ok"

        assert await breaker.call(operation) == "ok"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.get_state()["failure_count"] == 0

    asyncio.run(scenario())


def test_circuit_breaker_opens_after_failure_threshold():
    async def scenario():
        breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=1,
                recovery_timeout=60,
                timeout=1,
                expected_exception=RuntimeError,
            )
        )

        async def failing_operation():
            raise RuntimeError("service down")

        with pytest.raises(RuntimeError, match="service down"):
            await breaker.call(failing_operation)

        assert breaker.state == CircuitState.OPEN

        with pytest.raises(CircuitBreakerError, match="OPEN"):
            await breaker.call(failing_operation)

    asyncio.run(scenario())
