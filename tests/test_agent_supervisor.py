import asyncio

from podcast_generator.agent_supervisor import (
    AgentSupervisor,
    AgentType,
    SpecializedAgent,
    Task,
    TaskStatus,
)


class EchoAgent(SpecializedAgent):
    async def _handle_task(self, task: Task):
        return {"task_name": task.task_name, "payload": task.payload}


def test_supervisor_registers_the_core_learning_agents():
    supervisor = AgentSupervisor()

    assert set(supervisor.agents) == {
        AgentType.CONTENT_FETCHER,
        AgentType.QUALITY_ASSESSOR,
        AgentType.CONTENT_PROCESSOR,
        AgentType.AUDIO_GENERATOR,
    }


def test_supervisor_submits_executes_and_notifies_observers():
    async def scenario():
        events = []
        supervisor = AgentSupervisor()
        supervisor.agents[AgentType.CONTENT_FETCHER] = EchoAgent(
            AgentType.CONTENT_FETCHER,
            "echo-fetcher",
        )
        supervisor.add_observer(lambda event, task: events.append((event, task.task_name)))

        task_id = await supervisor.submit_task(
            AgentType.CONTENT_FETCHER,
            "fetch_articles",
            {"limit": 3},
        )
        completed_task = await supervisor.execute_task(task_id)

        assert completed_task.status == TaskStatus.COMPLETED.value
        assert completed_task.result == {
            "task_name": "fetch_articles",
            "payload": {"limit": 3},
        }
        assert supervisor.active_tasks == {}
        assert len(supervisor.completed_tasks) == 1
        assert events == [
            ("task_submitted", "fetch_articles"),
            ("task_started", "fetch_articles"),
            ("task_completed", "fetch_articles"),
        ]

    asyncio.run(scenario())
