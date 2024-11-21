from public_api.shared_schemas import (
    Task, TaskCreate, TaskUpdate, TaskWithAssignee, TaskFilter, TaskStatistics,
    UserTaskSummary, TaskComment, TaskCommentCreate
)
from public_api.api.client import APIClient


class TasksAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_task(self, task: TaskCreate) -> Task:
        response = self.client.post("/tasks/", json=task.model_dump())
        return Task.model_validate(response)

    def get_tasks(self,
                  skip: int = 0, limit: int = 100,
                  filter_params: TaskFilter | None = None) -> list[TaskWithAssignee]:
        params = {"skip": skip, "limit": limit}
        if filter_params:
            params.update(filter_params.model_dump(exclude_none=True))
        response = self.client.get("/tasks/", params=params)
        return [TaskWithAssignee.model_validate(item) for item in response]

    def get_task_statistics(self) -> TaskStatistics:
        response = self.client.get("/tasks/statistics")
        return TaskStatistics.model_validate(response)

    def get_user_task_summary(self) -> list[UserTaskSummary]:
        response = self.client.get("/tasks/user_summary")
        return [UserTaskSummary.model_validate(item) for item in response]

    def get_overdue_tasks(self, skip: int = 0, limit: int = 100) -> list[TaskWithAssignee]:
        params = {"skip": skip, "limit": limit}
        response = self.client.get("/tasks/overdue", params=params)
        return [TaskWithAssignee.model_validate(item) for item in response]

    def create_batch_tasks(self, tasks: list[TaskCreate]) -> list[Task]:
        response = self.client.post("/tasks/batch_create", json=[task.model_dump() for task in tasks])
        return [Task.model_validate(item) for item in response]

    def get_my_tasks(self, skip: int = 0, limit: int = 100) -> list[Task]:
        params = {"skip": skip, "limit": limit}
        response = self.client.get("/tasks/my_tasks", params=params)
        return [Task.model_validate(item) for item in response]

    def get_task(self, task_id: int) -> TaskWithAssignee:
        response = self.client.get(f"/tasks/{task_id}")
        return TaskWithAssignee.model_validate(response)

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task:
        response = self.client.put(f"/tasks/{task_id}", json=task_update.model_dump(exclude_unset=True))
        return Task.model_validate(response)

    def delete_task(self, task_id: int) -> None:
        self.client.delete(f"/tasks/{task_id}")

    def complete_task(self, task_id: int) -> Task:
        response = self.client.post(f"/tasks/{task_id}/complete")
        return Task.model_validate(response)

    def add_task_comment(self, task_id: int, comment: TaskCommentCreate) -> TaskComment:
        response = self.client.post(f"/tasks/{task_id}/comment", json=comment.model_dump())
        return TaskComment.model_validate(response)

    def get_task_comments(self, task_id: int, skip: int = 0, limit: int = 100) -> list[TaskComment]:
        params = {"skip": skip, "limit": limit}
        response = self.client.get(f"/tasks/{task_id}/comments", params=params)
        return [TaskComment.model_validate(item) for item in response]
