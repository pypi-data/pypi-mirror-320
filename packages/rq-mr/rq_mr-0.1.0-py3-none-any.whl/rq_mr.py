import time
from typing import Callable, Any, Generator, Dict
from redis import Redis
from rq import Worker
import logging
from rq.exceptions import NoSuchJobError
import os

from rq.job import Job
from rq.registry import StartedJobRegistry, FinishedJobRegistry, FailedJobRegistry

logger = logging.getLogger(__name__)

WORKER_BRAIN_PREFIX = os.environ.get("WORKER_BRAIN_PREFIX") or "brain"
MAX_QUEUED_JOBS = int(os.environ.get("MAX_QUEUED_JOBS") or 10)
WAIT_TIME = float(os.environ.get("WAIT_TIME") or 1)

def get_free_queue(connection):
    # Get brain worker
    # Iterate over the queues he listens to (all brain workers listen to the same)
    # Return a free one
    workers = Worker.all(connection=connection)
    computers = [w for w in workers if w.name.startswith(WORKER_BRAIN_PREFIX)]
    if len(computers) == 0:
        return None
    worker = computers[0]
    queues = worker.queues
    logger.info(f"Available queues: {queues}")
    while True:
        for queue in queues:
            if queue.count == 0:
                logger.info(f"Found queue {queue.name}")
                return queue
        raise RuntimeError("Did not find a free queue")


class ComputationEngine:
    def __init__(
            self,
            connection: Redis,
            counter: Callable[[Any], int],
            splitter: Callable[[Dict[str, Any]], Generator[Dict[str, Any], None, None]],
            atomic_computation: Callable[[Dict[str, Any]], Any],
            joiner: Callable[[Dict[str, Any], Dict[str, Any]], Any],
            data: Dict[str, Any],
            max_queued_jobs: int = MAX_QUEUED_JOBS
    ):
        self.counter = counter
        self.splitter = splitter
        self.atomic_computation = atomic_computation
        self.joiner = joiner
        self.data = data
        self.connection = connection
        self.max_queued_jobs = max_queued_jobs

        self.queue = get_free_queue(self.connection)

        self.started_registry = StartedJobRegistry(queue=self.queue)
        self.finished_registry = FinishedJobRegistry(queue=self.queue)
        self.failed_registry = FailedJobRegistry(queue=self.queue)

        self.total_number_of_jobs = self.counter(self.data)
        if self.total_number_of_jobs == 0:
            logger.error("No jobs to compute")
            raise ValueError("No jobs to compute")
        self.needed_digits = len(str(self.total_number_of_jobs))

        self.data_generator = self.splitter(self.data)
        self.total_enqueued_jobs = 0
        self.finished_enqueuing = False
        self.finished_computing = False
        self.on_queue_jobs_ids = set()
        self.running_jobs_ids = set()
        self.finished_jobs_ids = set()
        self.failed_jobs_ids = set()
        self.partial_results = {}
        self.result = None

    def make_new_job_id(self):
        self.total_enqueued_jobs += 1
        return f"{self.total_enqueued_jobs:0{self.needed_digits}d}"

    def enqueue_single_job(self):
        assert not self.finished_enqueuing
        try:
            job_data = next(self.data_generator)
        except StopIteration:
            self.finished_enqueuing = True
            logger.info("finished enqueuing")
            return
        job = Job.create(
            self.atomic_computation,
            (job_data,),
            id=self.make_new_job_id(),
            timeout=-1,
            result_ttl=-1,
            connection=self.connection
        )
        self.queue.enqueue_job(job)
        self.on_queue_jobs_ids.add(job.id)
        logger.info(f"enqueued {job.id=}")
        logger.debug("enqueued job data: %s", job_data)

    def enqueue_jobs(self):
        while not self.finished_enqueuing and len(self.on_queue_jobs_ids) < self.max_queued_jobs:
            self.enqueue_single_job()

    def collect_jobs(self):
        # Collect started, finished and failed jobs from registry
        started_registry = self.started_registry.get_job_ids()
        # Caution: we have to split the id... is this a bug?
        started_registry = [job_id.split(':')[0] for job_id in started_registry]
        finished_registry = self.finished_registry.get_job_ids()
        failed_registry = self.failed_registry.get_job_ids()
        logger.debug(f"started_registry={started_registry}, finished_registry={finished_registry}, failed_registry={failed_registry}")
        # new_started were on queue and now are started
        new_started = set(started_registry) & self.on_queue_jobs_ids
        # new_finished were on queue or running and now are finished
        new_finished = (set(finished_registry) &
                        (self.on_queue_jobs_ids | self.running_jobs_ids))
        # new_failed were on queue or running and now are failed
        new_failed = (set(failed_registry) &
                      (self.on_queue_jobs_ids | self.running_jobs_ids))
        logger.debug(f"new_started={new_started}, new_finished={new_finished}, new_failed={new_failed}")
        self.finished_jobs_ids |= new_finished
        self.failed_jobs_ids |= new_failed
        self.on_queue_jobs_ids -= (new_started | new_failed | new_finished)
        self.running_jobs_ids -= (new_finished | new_failed)
        self.running_jobs_ids |= new_started

        for job_id in new_finished:
            finished_job = self.queue.fetch_job(job_id)
            self.partial_results[job_id] = finished_job.result
            self.finished_registry.remove(job_id, delete_job=True)
            logger.info(f"finished {job_id=}")
        for job_id in new_failed:
            try:
                logger.info(f"failed {job_id=}")
                job = self.queue.fetch_job(job_id)
                logger.info(f"callstack of {job_id}: {job.exc_info}")
                logger.info(f"worker of {job_id}: {job.worker_name}")
                logger.info(f"metadata of {job_id}: {job.meta}")
                self.failed_registry.remove(job_id, delete_job=True)
            except NoSuchJobError:
                logger.info(f"failed {job_id=} -- no such job")
        if self.total_number_of_jobs == len(self.finished_jobs_ids) + len(self.failed_jobs_ids):
            logger.info(f"finished computing")
            self.finished_computing = True

    def tqrxf_stats(self) -> str:
        return (f"T/Q/R/X/F={self.total_number_of_jobs}/{len(self.on_queue_jobs_ids)}/"
                f"{len(self.running_jobs_ids)}/{len(self.failed_jobs_ids)}/{len(self.finished_jobs_ids)}")

    # def finish_computation(self):
    #     if not self.finished_computing:
    #         raise RuntimeError("Computation not finished")
    #     return self.joiner(self.data, self.results)

    # def abort_computation(self):
    #     # Get all jobs that are on queue and delete them
    #     now_queued_jobs_ids = self.queue.job_ids
    #     for job_id in self.on_queue_jobs_ids | self.running_jobs_ids:
    #         if job_id in now_queued_jobs_ids:
    #             logger.info(f"Deleting job {job_id} from queue")
    #             job = self.queue.fetch_job(job_id)
    #             job.delete()
    #         else:
    #             logger.info(f"Sending stop command to job {job_id}")
    #             try:
    #                 job = self.queue.fetch_job(job_id)
    #                 send_stop_job_command(redis, job_id)
    #                 job.delete()
    #             except:
    #                 logger.exception(f"Error stopping job {job_id}... maybe it was already finished")
    #     redis.delete(f"stop_job_{self.data['computation_name']}-{self.data['execution_name']}")
    #     my_job = get_current_job(redis)
    #     my_job.result_ttl = 0

    def run(self):
        logger.info("Running computation engine")
        while not self.finished_computing:
            # if redis.exists(f"stop_job_{self.data['computation_name']}-{self.data['execution_name']}"):
            #     logger.info("Asked to stop")
            #     self.abort_computation()
            #     return
            logger.debug(f"Enqueuing jobs. Status: {self.tqrxf_stats()}")
            self.enqueue_jobs()
            # self.save_to_redis()
            logger.debug(f"Collecting jobs. Status: {self.tqrxf_stats()}")
            self.collect_jobs()
            # self.save_to_redis()
            logger.debug(f"Waiting for next iteration. Status: {self.tqrxf_stats()}")
            logger.debug(f"{self.on_queue_jobs_ids=}, {self.running_jobs_ids=}, {self.finished_jobs_ids=}, {self.failed_jobs_ids=}")
            time.sleep(WAIT_TIME)
        logger.info("finished enqueuing and computing")
        logger.info(f"finished processing... {self.tqrxf_stats()}")
        self.result = self.joiner(self.data, self.partial_results)
