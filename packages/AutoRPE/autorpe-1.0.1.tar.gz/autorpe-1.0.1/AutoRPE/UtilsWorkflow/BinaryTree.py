from logging import root
from os.path import join


class BinaryTree:
    """
    Represents a binary tree of jobs for an experiment, where each job can have various statuses. 
    Jobs are processed based on their statuses and are moved through different stages in the workflow.

    - PENDING: The job has been created and is ready to be launched.
    - RUNNING: The job is currently running.
    - SUCCESS: A job that has been completed with successful results and asserted.
    - FAILED: A job that has been completed with unsuccessful results and cannot be split.
    - SUSPENDED: A job that has been completed with unsuccessful results, that has been split, and depends on
      the results of descendant jobs.

    Initializes the binary tree with a root job, accuracy test, local folder, and a maximum number
    of running jobs.

    Parameters:
        root (Job): The root job of the binary tree, which starts the experiment.
        accuracy_test (object): The accuracy test to evaluate the job results.
        local_folder (str): The local folder where the experiment data is stored.
        max_running_jobs (int, optional): The maximum number of jobs allowed to run concurrently (default is 100).
    """
    def __init__(self, root: 'Job', accuracy_test: object, local_folder: str, max_running_jobs: int=100):
        # Save the seed job, i.e. the seed of the father of the binary tree
        self.root = root
        self.loop = 0
        self.max_id = 0
        # Initialize the different lists of Binary jobs
        self.pending = []
        self.running = []
        self.success = []
        self.failed = []
        self.suspended = []
        self.disinherited = []
        self.local_folder = local_folder
        self.checkpoint_folder = join(local_folder, "checkpoints")
        # Initialize a dictionary with links to all the lists
        self.__dict = {"PENDING": self.pending,
                       "RUNNING": self.running,
                       "SUCCESS": self.success,
                       "FAILED": self.failed,
                       "SUSPENDED": self.suspended,
                       "DISINHERITED": self.disinherited,
                       }
        # Set the number of maximum jobs running at the same time
        self.accuracy_test = accuracy_test
        self.max_running_jobs = max_running_jobs

        # Set checkpoint name and put seed job to pending
        self.pending.append(self.root)
        # self.checkpoint_name = "checkpoint_%s.pkl" % self.root.hash

    def sort_pending(self, lower_first: bool=True):
        """
        Sorts the pending jobs based on their levels, either prioritizing lower or higher levels.

        Parameters:
            lower_first (bool, optional): If True, jobs are sorted by ascending level; otherwise, by descending level.

        Returns:
            None
        """
        if lower_first:
            self.pending.sort(key=lambda _x: _x.level)
        else:
            self.pending.sort(key=lambda _x: - _x.level)

    def all(self):
        """
        Returns a list of all jobs across different statuses (excluding disinherited jobs).

        Returns:
            list: A combined list of jobs from all statuses.
        """
        self.sort_pending()
        return self.running + self.pending + self.success + self.failed + self.suspended

    def __getitem__(self, item: str):
        """
        Allows direct access to the job lists by their status name (e.g., "PENDING", "RUNNING", etc.).

        Parameters:
            item (str): The status of the jobs to access (e.g., "PENDING").

        Returns:
            list: The list of jobs with the specified status.
        """
        return self.__dict[item]

    def step(self):
        """
        Loops through all the jobs, checks their status, and updates their status accordingly.

        Returns:
            int: The number of jobs that had their status changed.
        """

        step_changes = 0
        for job in self.all():
            status = job.status
            if status == "PENDING":
                if len(self.running) < self.max_running_jobs:
                    # Check the job is already in queue, if not submit the job
                    self.check_pending(job)

            elif status == "RUNNING":
                # Check the job has finished
                self.check_running(job)

            elif status == "SUSPENDED":
                self.check_children(job)
            # Register the change if any
            if status != job.status:
                step_changes += 1
                # Create a mermaid graph for the new status
                # job4 = [j for j in self.all() if j.incremental_id==4]
                # job3 = [j for j in self.all() if j.incremental_id == 3]
                # if job4:
                #     job4[0].graph()
                # if job3:
                #     job3[0].graph()
                self.root.graph()

        # for job in self.pending:
        #     self.checkpoint(job.incremental_id)

        self.loop += step_changes
        # In case the status of any of the jobs from the experiment changed, print the status.
        if step_changes:
            self.print_status()
        return step_changes

    def check_pending(self, job: 'Job'):
        """
        Checks if a job is already in the queue. If not, it is submitted for execution.

        Parameters:
            job (Job): The job to be checked and potentially started.

        Returns:
            None
        """
        # Check the job is already in queue, if not submit the job
        job.run_job()
        job.status = "RUNNING"
        self.pending.remove(job)
        self.running.append(job)

    def check_running(self, job: 'Job'):
        """
        Checks if a running job has finished and updates its status accordingly.

        Parameters:
            job (Job): The job to be checked.

        Returns:
            None
        """
        remote_status = job.remote_status
        if remote_status == "COMPLETED":
            # job.retrials = 0
            # Passes on the remote directory and the communicator so as to retrieve pkl result file
            # Create plots
            # self.create_plots()
            result = job.get_result(self.accuracy_test)
            if result == "SUCCESS" :
                self.move_to_success(job)
                print("Job %s %s terminated with success" % (job.incremental_id, job.hash))
            elif result == "FAIL":
                self.fail(job)
            else:
                print("WHATTHEHELL")
                # self.create_plots()
                # plot_result.plot_result(
                #     input_file=self._result,
                #     limits=self.accuracy_test.limits,
                #     ensemble_members_path=self.accuracy_test.members_path,
                #     output_folder=self.local_folder + "/plot/plot_Test" + str(self.hash)
                # )

        elif remote_status in ["FAILED", "TIMEOUT", "NODE_FAIL"]:
            # Fail for numerical reasons its ok
            if self.accuracy_test.fail_for_numerical_reason(remote_rundir=job.remote_rundir):
                self.fail(job)
            elif remote_status == "NODE_FAIL":
                job.job_id = None
                # Remove entry from dictionary if the job is stored
                if job.hash in job.analysis_status:
                    job.analysis_status.pop(job.hash)
                # Re-run the job
                print("Node where job %s was running failed, resubmitting job " % job.remote_rundir)
                self.move_to_pending(job)
            elif job.retrials < job.max_retrials and len(job.id_reduced_precision) > 1:
                # Reset job_id
                job.job_id = None
                # Remove entry from dictionary if the job is stored
                if job.hash in job.analysis_status:
                    job.analysis_status.pop(job.hash)
                # Re-run the job
                print("job %s failed for unknown reasons, resubmitting job " % job.remote_rundir)
                self.move_to_pending(job)
                job.retrials += 1
            else:
                if job.retrials > 0:
                    print("Job failed for unknown reasons, was resubmitted %i times" % job.retrials)
                self.fail(job)
        elif remote_status == 'CANCELLED+':
            job.retrials += 1
            self.fail(job)
        elif remote_status == "RUNNING":
            pass
        elif remote_status == "PENDING":
            pass
        else:
            raise AssertionError("Unhandled status %s" % remote_status)

    def move_to_success(self, job: 'Job'):
        """
        Moves a job to the SUCCESS list after it has completed successfully.

        Parameters:
            job (Job): The job to be moved to success.

        Returns:
            None
        """
        self[job.status].remove(job)
        self.success.append(job)
        job.status = "SUCCESS"
        job.update_parent_set()

    def move_to_failed(self, job: 'Job'):
        """
        Moves a job to the FAILED list after it has failed.

        Parameters:
            job (Job): The job to be moved to failed.

        Returns:
            None
        """
        self[job.status].remove(job)
        self.failed.append(job)
        job.status = "FAILED"
        if not job.reshuffle:
            job.update_parent_set()
        job.print_info_job("failed")

    def move_to_pending(self, job: 'Job'):
        """
        Moves a job to the PENDING list, indicating it is ready to be re-executed.

        Parameters:
            job (Job): The job to be moved to pending.

        Returns:
            None
        """
        # Case of a new job move to pending
        if job in self[job.status]:
            self[job.status].remove(job)
        self.pending.append(job)
        job.status = "PENDING"
        job.print_info_job("added to pending")

    def move_to_suspended(self, job: 'Job'):
        """
        Moves a job to the SUSPENDED list, indicating it has failed and needs further evaluation.

        Parameters:
            job (Job): The job to be moved to suspended.

        Returns:
            None
        """
        self[job.status].remove(job)
        self.suspended.append(job)
        job.status = "SUSPENDED"
        job.print_info_job("suspended")

    def fail(self, job: 'Job'):
        """
        Handles the failure of a job, either by resubmitting it, subdividing it into children, or marking it as failed.

        Parameters:
            job (Job): The job that has failed.

        Returns:
            None
        """
        import AutoRPE.UtilsRPE.Error as Error
        import AutoRPE.UtilsWorkflow.ExceptionManager as ExceptionManager
        # The job is already a try to save some var from banned list, put it to fail
        if job.reshuffle:
            self.move_to_failed(job)
            return

        if not job.child:
            try:
                # If the job can be subdivided: spawn children
                job.spawn_children()
                self.move_to_suspended(job)
                for ch in job.child:
                    if ch not in self.all():
                        self.move_to_pending(ch)
            except Error.ClusterCantBeDivided:
                # This is a leaf, we cannot subdivide the set, move to failed
                self.move_to_failed(job)
        else:
            # Either both child failed or father failed while the child were ok, check why and decide what to do
            ExceptionManager.resolve_exception(job, self)
            # exception_manager.divide_and_force(self, queue)
            # queue.root.graph(queue.disinherited)

    def check_children(self, job: 'Job'):
        """
        Checks if all child jobs of a given job have finished. If all children are finished, updates the job status accordingly.

        Parameters:
            job (Job): The job whose children are being checked.

        Returns:
            None
        """
        # Check if all the child jobs have finished
        all_finished = all([c.status == "FAILED" or c.status == "SUCCESS" for c in job.child])
        if all_finished:
            # The initial reshuffled job is being analyzed
            if job.reshuffle and (job.parent is None or not job.parent.reshuffle):
                self.manage_reshuffled_job(job)
                return
            # for child in job.child:
            #     # Get the banned variables from all the child
            #     job.banned_variables += child.banned_variables
            #
            #     # In case the child job failed, include its analysis variables in the banned variables
            #     if child.status == "FAILED":
            #         self.move_to_failed(child)
            #     # Keep unique values only
            #     job.banned_variables = list(set(job.banned_variables))
            # job.id_reduced_precision = [var for var in job.id_reduced_precision if var not in job.banned_variables]

            if not job.id_reduced_precision:
                # The does not need to be rerun, both child have failed and all variables are double
                self.move_to_success(job)
            else:
                self.move_to_pending(job)

    def manage_reshuffled_job(self, job: 'Job'):
        """
        Manages a reshuffled job by determining whether it can be re-executed based on its child jobs' statuses.

        Parameters:
            job (Job): The reshuffled job to be managed.

        Returns:
            None
        """
        import AutoRPE.UtilsWorkflow.ExceptionManager as ExceptionManager
        # The failed child must be discarded, since it contains the combination of prole that fails
        child = [c for c in job.child if not c.status == "FAILED"]
        if len(child) == 0:
            ExceptionManager.resolve_exception(job, self)
            return
        max_len = max([len(c.id_reduced_precision) for c in child])
        for c in child:
            if len(c.id_reduced_precision) == max_len:
                job.id_reduced_precision = c.id_reduced_precision
                job.banned_variables = c.banned_variables
                job.child = job.reshuffle
                # First, move to failed the job
                self.move_to_failed(c.child_number)
                # Then ban his variables in his ancestors up to this job
                job.fail_child(c.child_number)
                for i_job in self.all():
                    if i_job.hash == c.child_number:
                        for var_id in i_job.id_reduced_precision:
                            self.ban_variable(job, var_id)
                        # There can be more than one, the recursive function will take care of banning identical jobs
                        break
                self.move_to_success(job)

                return

    def ban_variable(self, job: 'Job', var_id: str):
        """
        Bans a variable from being used in a job or its children if it is part of the reduced precision set.

        Parameters:
            job (Job): The job where the variable is banned.
            var_id (str): The ID of the variable to be banned.

        Returns:
            None
        """
        for c in job.child:
            if var_id in c.id_reduced_precision:
                c.id_reduced_precision.remove(var_id)
                c.banned_variables.append(var_id)
                if not c.id_reduced_precision:
                    self.move_to_failed(c)
                self.ban_variable(c, var_id)
        return

    def print_status(self):
        """
        Prints the current status of all jobs in the experiment, showing the number of jobs in each list.

        Returns:
            None
        """
        for key in self.__dict.keys():
            print("\t%18s: %4i" % (key, len(self[key])))

    def checkpoint(self, incremental_id: int):
        """
        Saves a checkpoint of the experiment at the current status.

        Parameters:
            incremental_id (int): The ID of the job at which to save the checkpoint.

        Returns:
            None
        """
        import pickle
        import sys
        from os.path import isfile
        sys.setrecursionlimit(8000)

        if not incremental_id % 10 == 0 and incremental_id >= 15:
            return

        if incremental_id > self.max_id:
            self.max_id = incremental_id
            filename = "checkpoint_at_job_%s_d.pkl" % incremental_id
        else:
            filename = "checkpoint_at_job_%s_u.pkl" % incremental_id

        checkpoint_name = self.checkpoint_folder + "/%s" % filename
        if isfile(checkpoint_name):
            return

        print("Saving checkpoint!", end="\r")

        all_jobs = self.all() + self.disinherited

        # Remove communicator before saving it, since it throws the  TypeError: can't pickle _thread.lock objects
        communicator = self.accuracy_test.communicator

        self.accuracy_test.communicator = None
        for job in all_jobs:
            job.communicator = None

        # Dump object if does not exist

        # pickle.dump(self, open(checkpoint_name, "wb"))

        # Restore the communicator
        self.accuracy_test.communicator = communicator
        for job in all_jobs:
            job.communicator = communicator
        print("Checkpoint saved at %s!" % filename)

    def __hash__(self):
        """
        Returns the hash of the experiment, which is the same as the hash of the root job.

        Returns:
            int: The hash of the experiment.
        """
        return self.root.hash
