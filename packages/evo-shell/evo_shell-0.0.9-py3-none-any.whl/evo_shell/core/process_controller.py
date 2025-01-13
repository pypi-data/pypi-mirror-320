from multiprocessing import Process
from typing import Dict, Optional, Callable
import logging

logger = logging.getLogger("process_controller")


class ProcessController:
    def __init__(self):
        self.processes: Dict[str, Process] = {}

    # 새로운 프로세스를 시작
    def start_process(
        self, target_func: Callable, args: Optional[tuple] = None
    ) -> bool:
        try:
            arg_str = "_".join(str(arg) for arg in (args or ()))
            process_name = f"{target_func.__name__}_{arg_str}"
            if process_name in self.processes:
                raise ValueError(f"Process {process_name} already exists")

            process = Process(target=target_func, args=args or ())
            process.start()
            self.processes[process_name] = process

            logger.info(f"Process {process_name} started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start process {process_name}. {e}")
            return False

    # 프로세스 종료 (all or single)
    def terminate_process(self, process_name: Optional[str] = None) -> bool:
        try:
            # 단일 프로세스 종료
            if process_name is not None:
                if process_name not in self.processes:
                    logger.warning(f"Process {process_name} not found")
                    return False

                return self._terminate_single_process(
                    process_name, self.processes[process_name]
                )

            # 전체 프로세스 종료
            success = True
            for pid, process in list(self.processes.items()):
                if not self._terminate_single_process(pid, process):
                    success = False

            return success

        except Exception as e:
            logger.error(f"Error during process termination: {str(e)}")
            return False

    # 프로세스 단일 종료
    def _terminate_single_process(self, process_name: str, process: Process) -> bool:

        try:
            process.terminate()
            process.join(timeout=5)

            if process.is_alive():
                logger.warning(
                    f"Process {process_name} did not terminate gracefully, "
                    "forcing kill"
                )
                process.kill()

            process.join()
            del self.processes[process_name]

            logger.info(f"Process {process_name} terminated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to terminate process {process_name}: {str(e)}")
            return False

    def single_process_alive(self, process_name: str) -> bool:
        try:
            if process_name not in self.processes:
                return False
            return self.processes[process_name].is_alive()
        except Exception as e:
            logger.error(f"Error checking process status: {str(e)}")
            return False

    def all_processes_alive(self) -> bool:
        try:
            if not self.processes:  # 프로세스가 없는 경우
                return False
            return any(process.is_alive() for process in self.processes.values())
        except Exception as e:
            logger.error(f"Error checking processes status: {str(e)}")
            return False

    def is_alive(self, process_name: Optional[str] = None) -> bool:
        if process_name is not None:
            return self.single_process_alive(process_name)
        return self.all_processes_alive()
