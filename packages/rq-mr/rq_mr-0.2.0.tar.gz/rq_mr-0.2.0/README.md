Implementation of map-reduce over RQ (Redis Queue)

The following environment variables can be set:
* `MAX_QUEUED_JOBS` (default=10) : Maximum number of jobs that can be queued at a time
* `WAIT_TIME` (default=1): Time in seconds between polling for status of jobs

