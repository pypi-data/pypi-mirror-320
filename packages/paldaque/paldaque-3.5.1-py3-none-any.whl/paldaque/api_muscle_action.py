import numpy as np
import palaestrai.store.database_model as dbm
import sqlalchemy.orm
from palaestrai.core import RuntimeConfig


def read_muscle_actions(
    experiment_id: int = 0,
    experiment_run_id: int = 0,
    experiment_run_instance_id: int = 0,
    experiment_run_phase_id: int = 0,
    limit: int = 10000,
    offset: int = 0,
    as_dict: bool = False,
):
    if experiment_run_phase_id > 0:
        level = 1
    elif experiment_run_instance_id > 0:
        level = 2
    elif experiment_run_id > 0:
        level = 3
    elif experiment_id > 0:
        level = 4
    else:
        level = 0

    store_uri = RuntimeConfig().store_uri

    engine = sqlalchemy.create_engine(store_uri)
    session_maker = sqlalchemy.orm.sessionmaker()
    session_maker.configure(bind=engine)
    raw = []
    with session_maker() as session:
        if level == 0:
            entries = (
                session.query(
                    dbm.MuscleAction,
                    dbm.Agent,
                    dbm.ExperimentRunPhase,
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRun,
                )
                .join(dbm.Agent, dbm.MuscleAction.agent_id == dbm.Agent.id)
                .join(
                    dbm.ExperimentRunPhase,
                    dbm.Agent.experiment_run_phase_id
                    == dbm.ExperimentRunPhase.id,
                )
                .join(
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRunPhase.experiment_run_instance_id
                    == dbm.ExperimentRunInstance.id,
                )
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .order_by(dbm.MuscleAction.id.asc())
                .limit(limit)
                .offset(offset)
            )
        elif level == 1:
            entries = (
                session.query(
                    dbm.MuscleAction,
                    dbm.Agent,
                    dbm.ExperimentRunPhase,
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRun,
                )
                .join(dbm.Agent, dbm.MuscleAction.agent_id == dbm.Agent.id)
                .join(
                    dbm.ExperimentRunPhase,
                    dbm.Agent.experiment_run_phase_id
                    == dbm.ExperimentRunPhase.id,
                )
                .join(
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRunPhase.experiment_run_instance_id
                    == dbm.ExperimentRunInstance.id,
                )
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .where(
                    dbm.Agent.experiment_run_phase_id
                    == experiment_run_phase_id
                )
                .order_by(dbm.MuscleAction.id.asc())
                .limit(limit)
                .offset(offset)
            )
        elif level == 2:
            entries = (
                session.query(
                    dbm.MuscleAction,
                    dbm.Agent,
                    dbm.ExperimentRunPhase,
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRun,
                )
                .join(dbm.Agent, dbm.MuscleAction.agent_id == dbm.Agent.id)
                .join(
                    dbm.ExperimentRunPhase,
                    dbm.Agent.experiment_run_phase_id
                    == dbm.ExperimentRunPhase.id,
                )
                .join(
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRunPhase.experiment_run_instance_id
                    == dbm.ExperimentRunInstance.id,
                )
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .where(
                    dbm.ExperimentRunPhase.experiment_run_instance_id
                    == experiment_run_instance_id
                )
                .order_by(dbm.MuscleAction.id.asc())
                .limit(limit)
                .offset(offset)
            )
        elif level == 3:
            entries = (
                session.query(
                    dbm.MuscleAction,
                    dbm.Agent,
                    dbm.ExperimentRunPhase,
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRun,
                )
                .join(dbm.Agent, dbm.MuscleAction.agent_id == dbm.Agent.id)
                .join(
                    dbm.ExperimentRunPhase,
                    dbm.Agent.experiment_run_phase_id
                    == dbm.ExperimentRunPhase.id,
                )
                .join(
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRunPhase.experiment_run_instance_id
                    == dbm.ExperimentRunInstance.id,
                )
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .where(
                    dbm.ExperimentRunInstance.experiment_run_id
                    == experiment_run_id
                )
                .order_by(dbm.MuscleAction.id.asc())
                .limit(limit)
                .offset(offset)
            )
        elif level == 4:
            entries = (
                session.query(
                    dbm.MuscleAction,
                    dbm.Agent,
                    dbm.ExperimentRunPhase,
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRun,
                )
                .join(dbm.Agent, dbm.MuscleAction.agent_id == dbm.Agent.id)
                .join(
                    dbm.ExperimentRunPhase,
                    dbm.Agent.experiment_run_phase_id
                    == dbm.ExperimentRunPhase.id,
                )
                .join(
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRunPhase.experiment_run_instance_id
                    == dbm.ExperimentRunInstance.id,
                )
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .where(dbm.ExperimentRun.experiment_id == experiment_id)
                .order_by(dbm.MuscleAction.id.asc())
                .limit(limit)
                .offset(offset)
            )

        for entry in entries.all():
            raw.append(entry)

    if as_dict:
        results = _extract(raw)
    else:
        results = []
        for entry in raw:
            results.append(
                {
                    "muscle_action_id": entry.MuscleAction.id,
                    "agent_id": entry.Agent.id,
                    "phase_id": entry.ExperimentRunPhase.id,
                    "instance_id": entry.ExperimentRunInstance.id,
                    "run_id": entry.ExperimentRun.id,
                    "experiment_id": entry.ExperimentRun.experiment_id,
                    "walltime": entry.MuscleAction.walltime.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "objective": entry.MuscleAction.objective,
                }
            )

    return results


def _extract(data):
    data_dict = {
        "muscle_action_id": [],
        "agent_id": [],
        "agent_name": [],
        "phase_id": [],
        "phase_mode": [],
        "instance_id": [],
        "run_id": [],
        "experiment_id": [],
        "walltime": [],
        "objective": [],
    }

    for idx, entry in enumerate(data):
        data_dict["muscle_action_id"].append(entry.MuscleAction.id)
        data_dict["agent_id"].append(entry.Agent.id)
        data_dict["agent_name"].append(entry.Agent.name)
        data_dict["phase_id"].append(entry.ExperimentRunPhase.id)
        data_dict["phase_mode"].append(entry.ExperimentRunPhase.mode)
        data_dict["instance_id"].append(entry.ExperimentRunInstance.id)
        data_dict["run_id"].append(entry.ExperimentRun.id)
        data_dict["experiment_id"].append(entry.ExperimentRun.experiment_id)
        data_dict["walltime"].append(
            entry.MuscleAction.walltime.strftime("%Y-%m-%d %H:%M:%S")
        )
        data_dict["objective"].append(entry.MuscleAction.objective)

        # Extract simulation times
        for key in entry.MuscleAction.simtimes:
            if key in ("py/object", "default_factory"):
                continue

            env_time_key = f"simtime_{key}"
            env_ticks_key = f"simticks_{key}"
            data_dict.setdefault(env_time_key, [])
            data_dict.setdefault(env_ticks_key, [])
            data_dict[env_time_key].append(
                entry.MuscleAction.simtimes[key]["py/state"][
                    "simtime_timestamp"
                ]
            )
            data_dict[env_ticks_key].append(
                entry.MuscleAction.simtimes[key]["py/state"]["simtime_ticks"]
            )

        try:
            for reading in entry.MuscleAction.sensor_readings:
                sensor_id = ("sensor", reading["py/state"]["uid"])
                data_dict.setdefault(sensor_id, [])
                for jdx in range(max(0, idx - len(data_dict[sensor_id]))):
                    data_dict[sensor_id].append(np.nan)
                value = reading["py/state"]["value"]
                if isinstance(value, dict):
                    if "dtype" in value and "int" in value["dtype"]:
                        value = int(value["value"])
                data_dict[sensor_id].append(value)

        except TypeError:
            pass

        try:
            for setpoint in entry.MuscleAction.actuator_setpoints:
                actuator_id = ("actuator", setpoint["py/state"]["uid"])
                data_dict.setdefault(actuator_id, [])
                for jdx in range(max(0, idx - len(data_dict[actuator_id]))):
                    data_dict[actuator_id].append(np.nan)

                value = setpoint["py/state"]["value"]
                if isinstance(value, dict):
                    if "dtype" in value and "int" in value["dtype"]:
                        value = int(value["value"])
                data_dict[actuator_id].append(value)

        except TypeError:
            pass

        try:
            for reward in entry.MuscleAction.rewards:
                reward_id = ("reward", reward["py/state"]["uid"])
                data_dict.setdefault(reward_id, [])
                for jdx in range(max(0, idx - len(data_dict[reward_id]))):
                    data_dict[reward_id].append(np.nan)
                value = reward["py/state"]["value"]
                if isinstance(value, dict):
                    if "dtype" in value and "int" in value["dtype"]:
                        value = int(value["value"])
                data_dict[reward_id].append(value)

        except TypeError:
            pass
        # for k, v in data_dict.items():
        #    if len(v) < len(data_dict["phase"]):
        #        data_dict[k].append(np.nan)

    # df = pd.concat([df, pd.DataFrame(data_dict)], ignore_index=True)

    # df = pd.concat([df, pd.DataFrame(data_dict)], ignore_index=True)
    for key, val in data_dict.items():
        while len(val) < len(data):
            val.append(np.nan)

    return data_dict
