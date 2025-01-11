# Python structure to control the submission and status of a remote job with few other capabilities.


class RemoteManager:
    """
        Initializes the RemoteManager with the given parameters.

        Parameters:
            id_reduced_precision (list): List of reduced precision variable IDs.
            forced_ids (list): List of forced variable IDs, if any.
            reduced_precision_level (int): Precision level for the variables.
            analysis_variables (list): List of analysis variables.
            communicator (SSH): The communicator object for remote operations.
            vault (Vault): Vault containing variable data.
            template (str): Path to the job template.
            result_filename (str): Filename for the results.
            counter (Counter): Counter object for incrementing job IDs.
            local_folder (str): Local directory for storing job data.
            analysis_status (dict): Dictionary containing the status of various analyses.
        """
    def __init__(self, id_reduced_precision: list,
                 forced_ids: list,
                 reduced_precision_level: list,
                 analysis_variables: list,
                 communicator: 'SSH',
                 vault: 'Vault',
                 template: str,
                 result_filename: str,
                 counter: 'Counter', local_folder: str, analysis_status: str):
        self.vault = vault
        self.id_reduced_precision = id_reduced_precision
        self.forced_ids = [] if not forced_ids else forced_ids[:]
        self.analysis_variables = analysis_variables
        self.incremental_id = counter.up() if counter else 0
        self.communicator = communicator
        self.reduced_precision_level = reduced_precision_level
        self.job_name = "%i-%s" % (self.incremental_id, self.hash)
        self.num_proc = 48
        self.remote_scratch = self.communicator.remote_scratch
        self.remote_logdir = "%s/analysis/LOGS" % self.remote_scratch
        self.remote_namelist_dir = "%s/Namelists" % self.remote_logdir
        self.remote_rundir = "%s/analysis/%s" % (self.remote_scratch, self.hash)
        self.job_id_filename = "%s/job_id.txt" % self.remote_rundir
        self.local_folder = local_folder

        self.remote_jobscript_path = "%s/%s.cmd" % (self.remote_logdir, self.hash)
        self.remote_namelist = "%s/%s" % (self.remote_namelist_dir, self.hash)

        self.template = template
        self.result_filename = result_filename

        self.jobscript = self.generate_jobscript()

        self.elapsed_time = None
        self.job_id = None
        self.retrials = 0
        self._result = None
        self.analysis_status = analysis_status

        # The default status is PENDING
        self._status = "PENDING"

    @property
    def variable_set(self):
        """
        Returns the set of variable IDs, including forced IDs if provided.

        Returns:
            list: List of variable IDs, including forced IDs.
        """
        if self.forced_ids:
            return self.id_reduced_precision + self.forced_ids
        else:
            return self.id_reduced_precision

    @property
    def hash(self):
        """
        Generates a unique hash based on the list of variable IDs and reduced precision level.

        Returns:
            str: A hash string representing the unique identifier.
        """
        import hashlib
        # Sort in order of raising id
        self.variable_set.sort()
        # Convert to string the list of ids
        string_to_hash = "".join([str(i_id) + '_' + str(self.reduced_precision_level) for i_id in self.variable_set])
        # Create the hash
        hash_object = hashlib.md5(string_to_hash.encode())
        return hash_object.hexdigest()

    def variables(self):
        """
        Retrieves the variables corresponding to the variable IDs in the variable set.

        Returns:
            list: List of variables corresponding to the IDs in the variable set.
        """
        return [self.vault.get_variable_by_id(_x) for _x in set(self.variable_set)]

    @property
    def remote_status(self):
        """
        Retrieves the remote status of the job.

        Returns:
            str: Current job status.
        """
        _status = self.job_status()
        return _status

    @property
    def status(self):
        """
        Retrieves the current status of the job.

        Returns:
            str: Current job status.
        """
        return self._status

    @status.setter
    def status(self, new_value: str):
        """
        Sets a new status for the job.

        Parameters:
            new_value (str): The new status to be set for the job.

        Raises:
            AssertionError: If the new status is not a valid job status.
        """
        possible_status = ["PENDING", "RUNNING", "ASSERTION_PENDING", "SUCCESS", "FAILED", "SUSPENDED"]
        # The list of possible status shall cover all the possible situations in which a job can be found.
        # PENDING: The job has been created and ready to be launched.
        # A PENDING JOB CAN ONLY HAVE SUSPENDED ANCESTORS AND SUCCESS OR FAILED DESCENDANTS
        # RUNNING: The job is RUNNING.
        # A RUNNING JOB CAN ONLY HAVE SUSPENDED ANCESTORS AND SUCCESS OR FAILED DESCENDANTS.
        # SUCCESS: A job that has been completed with successful results and asserted.
        # A SUCCESS job can not have both descendants FAILED
        # FAILED: A job that has been completed with unsuccessful results and that can not be
        # split ( Already was or a single variable set).
        # SUSPENDED: A job that has been completed with unsuccessful results that has been split and depends on the
        # results of descendant jobs.
        # SUSPENDED ancestors must be SUSPENDED.
        # At least one direct descendant should be different from FAILED or COMPLETED
        if new_value in possible_status:
            self._status = new_value
        else:
            raise AssertionError("Unknown status")

    def generate_jobscript(self):
        """
        Generates a job script based on the template and current job parameters.

        Returns:
            str: A job script ready for submission to the scheduler.
        """
        from os import path
        with open(self.template) as f:
            job = f.read()
            job = job.replace("%REMOTE_PATH%", self.remote_scratch)
            job = job.replace("%RUNHASH%", self.hash)
            job = job.replace("%JOBNAME%", self.job_name)
            job = job.replace("%LOGDIR%", self.remote_logdir)
            job = job.replace("%NAMELIST%", self.remote_namelist)
        return job

    def check_submitted(self):
        """
        Checks if the job has already been submitted to the remote scheduler.

        Returns:
            str: The job's current status (e.g., "PENDING" or "TO_SUBMIT").
        """
        command = 'squeue --format="%i %j"'
        stdin, stdout, stderr = self.communicator.execute(command)

        output = stdout.read().decode()
        lines = output.split("\n")
        if len(lines) > 1:
            jobs_in_remote_queue = lines[1:]
            for line in jobs_in_remote_queue:
                if line.strip():
                    job_id, job_name = line.split()
                    # Take into account just the jobs related to the analysis
                    if '-' not in job_name:
                        continue
                    # Remove node id that can differ from one run to the next
                    if job_name.split("-")[1] == self.job_name.split("-")[1]:
                        self.job_id = job_id
                        return "PENDING"

        return "TO_SUBMIT"

    def check_running(self):
        """
        Checks if the job is currently running on the remote scheduler.

        Returns:
            str: The current status of the job (e.g., "RUNNING", "PENDING").
        """
        # TODO: To use this tool with other schedulers, it might be convenient to define it somewhere else.
        scheduler_status_command = 'sacct  --format="State,Elapsed"'

        # Defining the command that will be sent to the remote machine
        command = '%s --job %s --user=$USER' % (scheduler_status_command, self.job_id)

        # Executing the command using the communicator
        stdin, stdout, stderr = self.communicator.execute(command)

        # Read status and time in the output received.
        output = stdout.read().decode()
        try:
            split_output = output.split("\n")[2].split()
            status = split_output[0]
        except IndexError:
            # Workaround for jobs run by other users on MN4 (sacct on MN4 won't allow reading others users job status)
            if output == '     State    Elapsed \n---------- ---------- \n':
                status = "COMPLETED"
            else:
                status = "PENDING"
        return status


    def generate_namelist(self):
        """
        Generates a namelist for the variables being analyzed, setting their precision according to the reduced precision level.

        Returns:
            str: A string representing the generated namelist.
        """
        # Namelist blueprint
        line_text = "emulator_variable_precisions(%d) = %d\t! Variable:%24s\tRoutine:%22s\tModule:%16s\n"
        # Namelist text
        namelist = ["! namelist variable precisions\n&precisions\n"]
        # Order variables by id ascending order
        self.analysis_variables.sort(key=lambda x: x.id)
        # Fill namelist
        for v in self.analysis_variables:
            # Reduce precision if variable is being analyzed otherwise keep original
            v_precision = self.reduced_precision_level if v.id in self.variable_set else v.precision
            namelist.append(
                line_text % (v.id, v_precision, v.name, v.procedure.name, v.procedure.module.name))

        namelist.append("/\n")
        return "".join(namelist)

    def run_job(self, force: bool=False):
        """
        Submits the job to the remote scheduler if it has not been submitted or if forced.

        Parameters:
            force (bool): If True, forces the submission of the job even if it has already been submitted.

        Returns:
            str: The status of the job after attempting to run.
        
        Raises:
            ExceptionNotManaged: If the job status is unknown.
        """
        import AutoRPE.UtilsRPE.Error as Error
        # Submit the job if force is true or the results are not present yet
        job_status = self.remote_status
        if force or job_status == "TO_SUBMIT":
            # The job has not been submitted yet
            print("Submitting job with incremental id  %s " % self.incremental_id)
            self.job_id = self.submit_job()
            print("Job %s successfully submitted with job_id %s" % (self.incremental_id, self.job_id))
        else:
            if job_status in ["COMPLETED", "TIMEOUT", "FAILED", "NODE_FAIL", "CANCELLED+"]:
                return job_status
            elif job_status == "RUNNING":
                # Set the got from the remote
                print("Job %s with job_id %s is running" % (self.incremental_id, self.job_id))
            elif job_status == "PENDING":
                print("Job %s was already in queue with job_id %s" % (self.incremental_id, self.job_id))
                return "RUNNING"
            else:
                raise Error.ExceptionNotManaged("Unknown job status")

    def submit_job(self, check_low=True):
        """
        Submits the job to the scheduler and returns the job ID.

        Parameters:
            check_low (bool): If True, checks if the job is queued and handles any low-level errors.

        Returns:
            str: The job ID assigned by the scheduler.
        """
        import re
        # Write the namelist to remote file
        # try:
        #     job_result = self.communicator.sftp.open(self.remote_rundir+"/time.step").read().decode()
        #     if job_result.split()[-1] == "152":
        #         print("AHHHHHHH")
        # except IOError:
        #     pass
        self.communicator.write_file(self.generate_namelist(), self.remote_namelist)
        # Write job to remote file
        self.communicator.write_file(self.jobscript, self.remote_jobscript_path)
        # with self.communicator.sftp.file(self.remote_jobscript_path, "w") as jobscript:
        #     jobscript.write(self.jobscript)

        # Defining the scheduler submit command
        # TODO: To use this tool with other schedulers, it might be convenient to define it somewhere else.
        scheduler_submit_command = "sbatch"

        # Defining the command to submit the job
        command = "%s %s" % (scheduler_submit_command, self.remote_jobscript_path)

        # Executing the command using the communicator
        stdin, stdout, stderr = self.communicator.execute(command)
        output = str(stdout.read())



        # Read the job id of the submitted job
        job_id_pattern = "Submitted batch job +([0-9]+)"
        job_id = re.search(job_id_pattern, output).group(1)
        # Return job id

        if (check_low):
            # After MN4 update, jobs are failing due to slowliness of SLURM: add a sleep if job is not yet in queue
            import time
            status = self.check_running()
            while status == "COMPLETED":
                time.sleep(5)
                status = self.check_running()

        return job_id

    def job_status(self):
        """
        Retrieves the current status of the job based on its ID.

        Returns:
            str: The current status of the job (e.g., "COMPLETED", "PENDING").
        """
        self.update_parameters()
        try:
            self.job_id , job_status, _, self.retrials = self.analysis_status[self.hash]
            if job_status == "COMPLETED":
                return job_status
        except KeyError:
            pass
        if self.job_id is None:
            return self.check_submitted()
        else:
            return self.check_running()

    def evaluate_simulation(self, accuracy_test: object):
        """
        Evaluates the accuracy of the simulation using the provided accuracy test.

        Parameters:
            accuracy_test (object): The accuracy test to evaluate the simulation.

        Returns:
            str: The result of the accuracy test evaluation.
        """
        try:
            return accuracy_test.evaluate_success(remote_rundir=self.remote_rundir)
        except IOError:
            self.remote_scratch = '/gpfs/scratch/bsc32/bsc32402/a5x6/'
            self.remote_rundir = "%s/analysis/%s" % (self.remote_scratch, self.hash)
            return accuracy_test.evaluate_success(remote_rundir=self.remote_rundir)

    def get_result(self, accuracy_test: object):
        """
        Retrieves the result of the simulation, either from the dictionary or from the remote system.

        Parameters:
            accuracy_test (object): The accuracy test to evaluate the result.

        Returns:
            str: The simulation result, either from the dictionary or from a remote file.
        """
        if self.incremental_id > 1000 and self.parent.incremental_id == 1:
            return self.evaluate_simulation(accuracy_test)
        filename_to_evaluate = self.job_id + '_RESULT.txt'
        try:
            _, _, job_result, _ = self.analysis_status[self.hash]
        except KeyError:
            try:
                # Attempt to open and read the remote results file  
                with self.communicator.sftp.open(self.remote_rundir + "/" + filename_to_evaluate, "r") as file:
                    job_result = file.read().decode()
                # Add the result to the dictionary for future queries                
                    self.analysis_status[self.hash] = [self.job_id, self.status, job_result, self.retrials]
            except IOError as e:
                # Handle file not found, permissions, or other IO errors
                job_result = "ERROR: Could not read result file - " + str(e)
            except Exception as e:
                # Handle other unforeseen errors
                job_result = "ERROR: An unexpected error occurred - " + str(e)        # If the simulation was running when the analysis status dict was created
        if job_result == "UNKNOWN":
            job_result = self.evaluate_simulation(accuracy_test)
        elif "ERROR" in job_result:
            # Optionally handle or log the error before moving on
            pass

        return job_result

    def update_parameters(self):
        """
        Updates the parameters used for remote job submission, including paths and job-related attributes.
        """
        remote_rundir = self.remote_rundir
        job_hash = self.hash
        rundir = "%s/analysis/%s" % (self.remote_scratch, job_hash)
        if rundir != remote_rundir:
            self.remote_rundir = rundir
            self.job_name = "%i-%s" % (self.incremental_id, job_hash)

            self.remote_jobscript_path = "%s/%s.cmd" % (self.remote_logdir, job_hash)
            self.remote_namelist = "%s/%s" % (self.remote_namelist_dir, job_hash)

            self.jobscript = self.generate_jobscript()

            self.job_id_filename = "%s/job_id.txt" % self.remote_rundir
            # Reset job_id
            self.job_id = None

    # def get_checkpoint_name(self):
    #     self.name=self.incremental_id
    #     print(self.name)
    #     return self.name
