import sys

import uuid

from typing import Any, Dict, Optional, Union

from ai.starlake.common import MissingEnvironmentVariable, TODAY

from ai.starlake.job import StarlakePreLoadStrategy, StarlakeSparkConfig, StarlakeExecutionEnvironment

from ai.starlake.airflow import StarlakeAirflowJob, StarlakeAirflowOptions

from airflow.models.baseoperator import BaseOperator

from airflow.providers.amazon.aws.operators.ecs import EcsCreateClusterOperator, EcsDeleteClusterOperator, EcsRegisterTaskDefinitionOperator, EcsRunTaskOperator

from airflow.utils.trigger_rule import TriggerRule

class StarlakeAirflowEcsCluster(StarlakeAirflowOptions):
    def __init__(self, cluster_name: str, pool: str, aws_conn_id: str, region_name: str, cpu: int, memory: int, options: dict, **kwargs):
        super().__init__(**kwargs)
        self.cluster_name = cluster_name
        self.pool = pool
        self.options = options
        self.aws_conn_id = aws_conn_id
        self.region_name = region_name
        self.cpu = cpu
        self.memory = memory
        try:
            cluster_arn = kwargs.get("cluster_arn", self.caller_globals.get("cluster_arn", __class__.get_context_var("cluster_arn", None, options)))
        except MissingEnvironmentVariable:
            cluster_arn = None
        self.cluster_id = cluster_arn.split("/")[-1] if cluster_arn else None

    @property
    def cluster_id(self) -> Optional[str]:
        return self._cluster_id

    @cluster_id.setter
    def cluster_id(self, cluster_id: Optional[str]) -> None:
        self._cluster_id = cluster_id

    def create_cluster(self, **kwargs) -> Optional[BaseOperator]:
        if self.cluster_id is not None:
            return None
        cluster_name = kwargs.get("cluster_name", f"{self.cluster_name.lower().replace('-', '_')}-{TODAY}")
        kwargs.pop("cluster_name", None)
        self.cluster_id = cluster_name
        task_id = kwargs.get("task_id", f"create_cluster_{cluster_name}")
        kwargs.pop("task_id", None)
        kwargs.update({
            'pool': kwargs.get('pool', self.pool),
            'trigger_rule': kwargs.get('trigger_rule', TriggerRule.ALL_SUCCESS),
            'wait_for_completion': True
        })
        return EcsCreateClusterOperator(
            task_id=task_id,
            cluster_name=cluster_name,
            aws_conn_id=self.aws_conn_id,
            region_name=self.region_name,
            **kwargs
        )

    def register_task_definition(self, **kwargs):
        id = uuid.uuid4()[:8]
        family = kwargs.get("family", f"starlake_{self.cluster_id}")
        task_id = kwargs.get("task_id", f"register_task_definition_{self.cluster_id}")
        kwargs.pop("task_id", None)
        kwargs.update({
            'pool': kwargs.get('pool', self.pool),
            'trigger_rule': kwargs.get('trigger_rule', TriggerRule.ALL_SUCCESS),
            'wait_for_completion': True
        })
        register_task_kwargs = {
            "cpu": f"{self.cpu}",
            "memory": f"{self.memory}",
            "networkMode": "awsvpc",
        }
        return EcsRegisterTaskDefinitionOperator(
            task_id=task_id,
            family=family,
            register_task_kwargs=register_task_kwargs,
            aws_conn_id=self.aws_conn_id,
            region_name=self.region_name,
            **kwargs
        )

    def run_task(self, overrides: dict, **kwargs):
        #
        #image = "starlakeai/starlake:latest"
        #networkMode = "awsvpc"
        #launchType = "FARGATE"
        ...

    def delete_cluster(self, **kwargs):
        cluster_name = kwargs.get("cluster_name", self.cluster_id)
        kwargs.pop("cluster_name", None)
        task_id = kwargs.get("task_id", f"delete_cluster_{cluster_name}")
        kwargs.pop("task_id", None)
        kwargs.update({
            'pool': kwargs.get('pool', self.pool),
            'trigger_rule': kwargs.get('trigger_rule', TriggerRule.ALL_DONE),
            'wait_for_completion': True
        })
        return EcsDeleteClusterOperator(
            task_id=task_id,
            cluster_name=cluster_name,
            aws_conn_id=self.aws_conn_id,
            region_name=self.region_name,
            **kwargs
        )

class StarlakeAirflowFargateJob(StarlakeAirflowJob):
    def __init__(self, filename: str, module_name: str, pre_load_strategy: Union[StarlakePreLoadStrategy, str, None] = None, options: Optional[dict] = None, **kwargs):
        super().__init__(filename, module_name, pre_load_strategy=pre_load_strategy, options=options, **kwargs)
        cluster_name = kwargs.get("cluster_name", self.caller_globals.get("cluster_name", __class__.get_context_var("cluster_name", filename.replace(".py", "").replace(".pyc", "").lower().replace("-", "_"), options)))
        aws_conn_id = kwargs.get("aws_conn_id", self.caller_globals.get("aws_conn_id", __class__.get_context_var("aws_conn_id", "aws_default", options)))
        region_name = kwargs.get("region_name", self.caller_globals.get("region_name", __class__.get_context_var("region_name", "eu-west-3", options)))
        self.cpu = kwargs.get("cpu", self.caller_globals.get("cpu", __class__.get_context_var("cpu", 1024, options)))
        self.memory = kwargs.get("memory", self.caller_globals.get("memory", __class__.get_context_var("memory", 2048, options)))
        self._cluster = StarlakeAirflowEcsCluster(cluster_name=cluster_name, pool=self.pool, aws_conn_id=aws_conn_id, region_name=region_name, cpu=self.cpu, memory=self.memory, options=options)

    @property
    def cluster(self) -> StarlakeAirflowEcsCluster:
        return self._cluster

    def pre_tasks(self, *args, **kwargs) -> Optional[BaseOperator]:
        """Overrides StarlakeAirflowJob.pre_tasks()"""
        return self.cluster.create_cluster(
            *args,
            **kwargs
        )

    def sl_job(self, task_id: str, arguments: list, spark_config: Optional[StarlakeSparkConfig] = None, **kwargs) -> BaseOperator:
        """Overrides StarlakeAirflowJob.sl_job()
        Generate the Airflow task that will run the starlake command.

        Args:
            task_id (str): The required task id.
            arguments (list): The required arguments of the starlake command to run.
            spark_config (Optional[StarlakeSparkConfig], optional): The optional spark configuration. Defaults to None.

        Returns:
            BaseOperator: The Airflow task.
        """
        container_overrides: Dict[str, Any] = {
            "command": arguments,
            "environment": [
                {"name": key, "value": value} for key, value in self.sl_env_vars.items()
            ],
            "cpu": kwargs.get("cpu", self.cpu),
            "memory": kwargs.get("memory", self.memory)
        }
        overrides = {"containerOverrides": [container_overrides]}
        return self.cluster.run_task(
            overrides=overrides,
            **kwargs
        )

    def post_tasks(self, *args, **kwargs) -> Optional[BaseOperator]:
        """Overrides StarlakeAirflowJob.post_tasks()"""
        return self.cluster.delete_cluster(
            *args,
            **kwargs
        )

    @classmethod
    def sl_execution_environment(cls) -> Union[StarlakeExecutionEnvironment, str]:
        """Returns the execution environment to use.

        Returns:
            StarlakeExecutionEnvironment: The execution environment to use.
        """
        return StarlakeExecutionEnvironment.FARGATE
