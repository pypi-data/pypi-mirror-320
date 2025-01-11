from logging import root
import signal
import time
import AutoRPE

class Counter:
    """
    A simple counter class to track increments.
    """
    def __init__(self):
        """
        Initialize the counter with a starting value of 0.
        """
        self.count = 0

    def up(self, how_much: str=1):
        """
        Increment the counter by the specified amount and return the previous count.
        
        Parameters:
            how_much (int, optional): The amount by which to increment the counter (default is 1).
        
        Returns:
            int: The previous value of the counter before the increment.
        """
        self.count += how_much
        return self.count - 1


class GracefulKiller:
    """
    This class is used to allow the user to stop an analysis at any point creating a pause_checkpoint.pkl which
    can be used in the future to restart the analysis from the same point.

    It uses the signal library to catch signals.
    """
    kill_now = False

    def __init__(self):
        """
        Initialize the signal handler to catch SIGINT and SIGTERM signals.
        """
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.filename = None

    def exit_gracefully(self, signum: int, frame):
        """
        Handle termination signals by setting the kill flag and printing a message.
        
        Parameters:
            signum (int): The signal number received.
            frame (frame object): The current stack frame (unused in this implementation).
        """
        print("Exit has been activated, will write the checkpoint as soon as possible and exit.")
        self.kill_now = True



class BinaryTreeSearch:
    """
    Initializes the experiment with given parameters and sets up necessary components.

    Parameters:
        communicator (SSH): The communicator object used to manage communication between
                                     remote-local machines.
        local_folder (str): The local directory to store data.
        analysis_status (dict): Dictionary used for tracking the experiment's progress (status of each job of
                                the analysis).
        job_template (str): Filename (path) of template used to generate jobs for the analysis.
        vault (Vault): The vault containing variables used for the analysis.
        original_precision_level (int): The precision level to use in the original run (dp=52, sp=23, hp=10).
        reduced_precision_level (int): The precision level for the reduced precision run (dp=52, sp=23, hp=10).
        accuracy_test (object): Object containing the accuracy test to validate results.
        max_running_jobs (int): The maximum number of jobs that can run simultaneously.
        output_filename (str): The name of the output file where results will be saved.
        experiment_name (str, optional): The name of the experiment. Defaults to "BinaryTreeSearch".
    """
    def __init__(self, communicator: 'SSH', local_folder: str, analysis_status: dict,
                 job_template: str, vault: 'Vault',
                 original_precision_level: int, reduced_precision_level: int, accuracy_test: object, max_running_jobs: int,
                 output_filename: str,
                 experiment_name: str="BinaryTreeSearch"):

        # Starting SSH connection
        self.communicator = communicator
        self.max_running_jobs = max_running_jobs
        self.local_folder = local_folder

        # Parameters of the analysis
        self.original_precision_level = original_precision_level
        self.reduced_precision_level = reduced_precision_level

        # Experiment related parameter
        self.accuracy_test = accuracy_test
        self.job_template = job_template
        self.vault = vault
        self.analysis_variables = [v for v in self.vault.variables if v.id is not None and v.is_used][:]
        self.experiment_name = experiment_name

        # In case of starting from a checkpoint
        self.analysis_status = analysis_status

        # Name of the output file
        self.output_filename = output_filename

        # The tree job structure
        self.binary_tree = None

        # Used to give an incremental ID to jobs  (for visualization)
        self.counter = Counter()

    def setup(self, id_reduced_precision: list, forced_ids: list, id_banned_var: list):
        """
        Sets up the experiment driver in preparation for starting the analysis.

        Parameters:
            id_reduced_precision (list): List of variable IDs to use with reduced precision.
            forced_ids (list): List of variable IDs that must be included in the analysis.
            id_banned_var (list): List of variable IDs that should be kept in original precision.

        Returns:
            None
        """
        from AutoRPE.UtilsWorkflow.Job import Job
        from AutoRPE.UtilsWorkflow.BinaryTree import BinaryTree
        print("Starting analysis with %i variables" % len(id_reduced_precision))

        # Create the root job of the search
        # The first set will include all the variables
        root_job = Job(id_reduced_precision=[ids for ids in id_reduced_precision if ids not in id_banned_var],
                       forced_ids=[ids for ids in forced_ids if ids not in id_banned_var],
                       analysis_variables=self.analysis_variables,
                       banned_variables=id_banned_var,
                       reduced_precision_level=self.reduced_precision_level,
                       communicator=self.communicator,
                       vault=self.vault,
                       template=self.job_template,
                       local_folder=self.local_folder,
                       analysis_status=self.analysis_status,
                       result_filename=self.accuracy_test.filename_to_evaluate,
                       counter=self.counter)
        # Defining it's level to 0
        root_job.level = 0
        # Initialize the Tree with the root job
        binary_tree = BinaryTree(root_job, self.accuracy_test, local_folder=self.local_folder)


        # Save the experiment driver in the class object
        self.binary_tree = binary_tree

    def root_job_succeeded(self):
        """
        Checks if the root job of the binary tree search has successfully completed.

        Returns:
            bool: True if the root job succeeded, otherwise False.

        Raises:
            AssertionError: If the root job failed, an error is raised.
        """
        # In case the root of the tree fails, raise an error
        if self.binary_tree.root.status == "FAILED":
            raise AssertionError("Whole set job ended with a failed result. Should check what happened.")
        # The status of the root will be SUSPENDED until the entire tree has been checked
        return self.binary_tree.root.status == "SUCCESS"

    def recover_checkpoint(self):
        """
        Recovers the analysis state from a previously saved checkpoint.

        Returns:
            BinaryTree: The binary tree object after recovery from the checkpoint.
        """
        import pickle as pkl
        binary_tree = pkl.load(open(self.checkpoint_name, "rb"))
        binary_tree.accuracy_test.communicator = self.communicator
        all_jobs = binary_tree.all() + binary_tree.disinherited
        for job in all_jobs:
            job.communicator = self.communicator
            job.vault = self.vault
            job.template = self.job_template
            job.local_folder = self.local_folder
        job_with_no_parent = [job for job in all_jobs if job.parent is None and job.level == 0]
        root = job_with_no_parent[0]
        root.vault = self.vault
        return binary_tree

    def initial_check(self, forced_id: list=[], banned_id: list=[]):
        """
        Performs an initial test run with original precision to ensure the accuracy test works.

        Parameters:
            forced_id (list, optional): List of variable IDs that are forced into the test.
            banned_id (list, optional): List of variable IDs that are excluded from the test.

        Returns:
            None

        Raises:
            AssertionError: If the basic test doesn't pass, an error is raised.
        """
        from AutoRPE.UtilsWorkflow.Job import Job
        import time
        # Make a original-precision run to be sure that the accuracy test works as expected
        for var in self.analysis_variables:
            var.precision = self.original_precision_level

        check_job = Job(id_reduced_precision=[],
                        forced_ids=forced_id,
                        analysis_variables=self.analysis_variables,
                        banned_variables=banned_id,
                        reduced_precision_level=self.reduced_precision_level,
                        communicator=self.communicator,
                        vault=self.vault,
                        template=self.job_template,
                        result_filename=self.accuracy_test.filename_to_evaluate,
                        local_folder=self.local_folder,
                        analysis_status=self.analysis_status,
                        counter=0
                        )
        # Submit job and wait until it finishes
        job_status = check_job.run_job()
        while job_status not in ["COMPLETED", "FAILED"]:
            time.sleep(5)
            job_status = check_job.remote_status

        # Check that the job ran successfully
        # if self.accuracy_test.evaluate_success(remote_rundir=check_job.remote_rundir):
        result = check_job.get_result(self.accuracy_test)
        if result == 'SUCCESS':
            print("Basic test was successful, continuing with the analysis")
        else:
            raise AssertionError("Basic simulation to check that the accuracy test works properly didn't pass")

    def binary_tree_search(self, id_forced_var: list=[], id_banned_var: list=[]):
        """
        Runs the binary tree search to evaluate the precision of variables.

        Parameters:
            id_forced_var (list, optional): List of variable IDs that are forced into the analysis.
            id_banned_var (list, optional): List of variable IDs that are excluded from the analysis.

        Returns:
            Job: The root job of the binary tree after the search is complete.
        """
        # ID of variables to analyze
        id_reduced_precision = [v.id for v in self.analysis_variables]

        # Create the root job and fill the BinaryTree class
        self.setup(id_reduced_precision, id_forced_var, id_banned_var)

        # Use a signal catcher to handle experiment pause
        killer = GracefulKiller()
        # Run the whole analysis until the root job succeed

        # Run until all the jobs have finished
        while not self.root_job_succeeded():
            # Loop through the jobs in the queue and take actions if required
            step_changes = self.binary_tree.step()

            # In case there hasn't been any change, this prevents the script of polling queue system too much
            if not step_changes:
                time.sleep(10.0)

            # If there was a signal during this loop:
            if killer.kill_now:
                print("Exiting...")
                exit(0)

        return self.binary_tree.root

    def print_root_configuration(self):
        """
        Prints the configuration of the root job to the specified output file.
        """
        # Sort and keep only unique values
        line_format = "%5i ! %20s %25s %20s %5s\n"
        # set final variable precision
        for var in self.analysis_variables:
            if var.id not in self.binary_tree.root.banned_variables:
                var.precision = 23

        with open(self.output_filename, "w") as output_file:
            # Add header
            output_file.write("#   ID " + " " * 5 +
                              "" +
                              " " * 13 +
                              "variable name" + " " * 11 +
                              "subprogram name" + " " * 9 +
                              "module name" + " " * 3 +
                              "variable precision" + "\n"
                              + 100 * "#" + "\n")
            # Put the var in ascending id order
            self.analysis_variables.sort(key=lambda x: x.id)
            # Print the variables to file
            for var in self.analysis_variables:
                output_file.write(line_format %
                                  (var.id, var.name, var.procedure.name, var.procedure.module.name, var.precision))

    def update_banned_variables(self):
        """
        Updates the list of banned variables (to be kept at original precision) and writes them to a new file.
        """
        line_format = "%5i ! %20s %25s %20s %5s\n"
        with open("banned_variables_newtxt", "w") as output_file:
            # Add header
            output_file.write("#   ID " + " " * 5 +
                              "" +
                              " " * 13 +
                              "variable name" + " " * 11 +
                              "subprogram name" + " " * 9 +
                              "module name" + " " * 3 +
                              "variable precision" + "\n"
                              + 100 * "#" + "\n")
            # Put the var in ascending id order
            self.analysis_variables.sort(key=lambda x: x.id)
            # Print the variables to file
            for var in self.analysis_variables:
                if var.precision == 52:
                    output_file.write(line_format %
                                      (var.id, var.name, var.procedure.name, var.procedure.module.name, var.precision))
