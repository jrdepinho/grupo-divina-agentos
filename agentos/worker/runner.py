import os
import socket
import threading
import time
import json
import traceback
from agentos.repositories.mission_repository import MissionRepository
from agentos.services.mission_service import MissionService
from datetime import datetime, timedelta
from agentos.utils.time import now

from agentos.core.database import connect
from agentos.executors.dispatcher import dispatch


MAX_WORKERS = max(
    1,
    int(os.getenv("AGENTOS_MAX_WORKERS", "4"))
)

repository = MissionRepository()
service = MissionService()


HEARTBEAT_INTERVAL = max(
    1,
    int(os.getenv("AGENTOS_HEARTBEAT_INTERVAL", "5"))
)

STALE_TIMEOUT = max(
    HEARTBEAT_INTERVAL * 2,
    int(os.getenv("AGENTOS_STALE_TIMEOUT", "30"))
)

RECOVERY_INTERVAL = max(
    5,
    int(os.getenv("AGENTOS_RECOVERY_INTERVAL", "10"))
)

HOSTNAME = socket.gethostname()
PROCESS_ID = os.getpid()




def executor_name():
    thread_name = threading.current_thread().name

    return f"{HOSTNAME}:{PROCESS_ID}:{thread_name}"


def next_job():
    conn = connect()

    try:
        conn.execute("BEGIN IMMEDIATE")

        row = conn.execute(
            """
            SELECT
                missions.id,
                missions.title,
                COALESCE(missions.type,'noop'),
                missions.payload
            FROM missions
            WHERE missions.status='QUEUED'
              AND NOT EXISTS (
                    SELECT 1
                    FROM mission_dependencies dependency_link
                    JOIN missions dependency
                      ON dependency.id=dependency_link.depends_on
                    WHERE dependency_link.mission_id=missions.id
                      AND dependency.status<>'DONE'
              )
            ORDER BY
                missions.priority ASC,
                missions.created_at ASC
            LIMIT 1
            """
        ).fetchone()

        if row is None:
            conn.commit()
            return None

        mission_id, title, mission_type, payload = row
        started_at = now()
        executor = executor_name()

        cursor = conn.execute(
            """
            UPDATE missions
            SET
                status='RUNNING',
                executor=?,
                started_at=?,
                finished_at=NULL,
                last_heartbeat=?
            WHERE id=?
              AND status='QUEUED'
            """,
            (
                executor,
                started_at,
                started_at,
                mission_id
            )
        )

        if cursor.rowcount != 1:
            conn.rollback()
            return None

        conn.execute(
            """
            INSERT INTO mission_events(
                mission_id,
                event,
                created_at
            )
            VALUES(?,?,?)
            """,
            (
                mission_id,
                "STARTED",
                started_at
            )
        )

        conn.commit()

        return (
            mission_id,
            title,
            mission_type,
            payload,
        )

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def update_heartbeat(mission_id):
    conn = connect()

    try:
        conn.execute(
            """
            UPDATE missions
            SET last_heartbeat=?
            WHERE id=?
              AND status='RUNNING'
            """,
            (
                now(),
                mission_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def heartbeat_loop(mission_id, stop_event):
    while not stop_event.wait(HEARTBEAT_INTERVAL):
        try:
            update_heartbeat(mission_id)

        except Exception as exc:
            print(
                f"[heartbeat] Erro na missão {mission_id}: {exc}",
                flush=True
            )







def recover_stale_jobs():
    conn = connect()

    try:
        conn.execute("BEGIN IMMEDIATE")

        stale_limit = (
            datetime.now() - timedelta(seconds=STALE_TIMEOUT)
        ).isoformat()

        stale_jobs = conn.execute(
            """
            SELECT id, title
            FROM missions
            WHERE status='RUNNING'
              AND (
                    last_heartbeat IS NULL
                    OR last_heartbeat < ?
              )
            """,
            (stale_limit,)
        ).fetchall()

        recovered_at = now()

        for mission_id, title in stale_jobs:
            conn.execute(
                """
                UPDATE missions
                SET
                    status='QUEUED',
                    executor=NULL,
                    started_at=NULL,
                    finished_at=NULL,
                    last_heartbeat=NULL,
                    report='Recuperada automaticamente após heartbeat expirado'
                WHERE id=?
                  AND status='RUNNING'
                """,
                (mission_id,)
            )

            conn.execute(
                """
                INSERT INTO mission_events(
                    mission_id,
                    event,
                    created_at
                )
                VALUES(?,?,?)
                """,
                (
                    mission_id,
                    "RECOVERED",
                    recovered_at
                )
            )

            print(
                f"[recovery] Missão recolocada na fila: {title}",
                flush=True
            )

        conn.commit()

        return len(stale_jobs)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def recovery_loop():
    while True:
        try:
            recover_stale_jobs()

        except Exception as exc:
            print(
                f"[recovery] Erro: {exc}",
                flush=True
            )

        time.sleep(RECOVERY_INTERVAL)


def execute_mission(
    mission_id,
    title,
    mission_type,
    payload,
):

    if payload:
        try:
            payload = json.loads(payload)
        except Exception:
            payload = {
                "_raw": payload
            }
    else:
        payload = {}

    mission = {
        "id": mission_id,
        "title": title,
        "type": mission_type,
        "payload": payload,
    }

    return dispatch(mission)


def worker_loop():
    worker_name = threading.current_thread().name

    while True:
        mission_id = None
        heartbeat_stop = None
        heartbeat_thread = None

        try:
            job = next_job()

            if job is None:
                time.sleep(2)
                continue

            (
                mission_id,
                title,
                mission_type,
                payload,
            ) = job

            heartbeat_stop = threading.Event()

            heartbeat_thread = threading.Thread(
                target=heartbeat_loop,
                args=(mission_id, heartbeat_stop),
                name=f"heartbeat-{mission_id[:8]}",
                daemon=True
            )

            heartbeat_thread.start()

            print(
                f"[{worker_name}] Executando: {title}",
                flush=True
            )

            try:

                result = execute_mission(
                    mission_id,
                    title,
                    mission_type,
                    payload,
                )

                repository.save_result(
                    mission_id,
                    result,
                )

                repository.finish(
                    mission_id,
                )

            except Exception as e:

                repository.fail(
                    mission_id,
                    {
                        "success": False,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )

            print(
                f"[{worker_name}] Finalizada: {title}",
                flush=True
            )

        except Exception as exc:
            print(
                f"[{worker_name}] Erro: {exc}",
                flush=True
            )

            if mission_id:
                try:
                    repository.fail(
                        mission_id,
                        {
                            "success": False,
                            "error": str(exc),
                            "traceback": traceback.format_exc(),
                        },
                    )

                except Exception as fail_exc:
                    print(
                        f"[{worker_name}] "
                        f"Erro ao registrar falha: {fail_exc}",
                        flush=True
                    )

            time.sleep(2)

        finally:
            if heartbeat_stop:
                heartbeat_stop.set()

            if heartbeat_thread:
                heartbeat_thread.join(timeout=2)


def main():
    print(
        f"AgentOS iniciado com {MAX_WORKERS} workers. "
        f"Heartbeat={HEARTBEAT_INTERVAL}s. "
        f"Timeout={STALE_TIMEOUT}s.",
        flush=True
    )

    recovery_thread = threading.Thread(
        target=recovery_loop,
        name="recovery",
        daemon=True
    )

    recovery_thread.start()

    threads = []

    for index in range(MAX_WORKERS):
        thread = threading.Thread(
            target=worker_loop,
            name=f"worker-{index + 1}",
            daemon=False
        )

        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
