# This file contains the definition of a Binary Search Job, which its an extension of a Job class.
# The extension includes several methods that are useful to do a precision analysis using a binary search algorithm.
from AutoRPE.UtilsWorkflow.RemoteManager import RemoteManager
import AutoRPE.UtilsRPE.Error as Error
from numpy import var


# Extend it
class Job(RemoteManager):
    """
    Represents a binary search job for precision analysis, extending the RemoteManager.
    """
    def __init__(self,
                 id_reduced_precision: list,
                 forced_ids: list,
                 banned_variables,
                 analysis_variables: list,
                 reduced_precision_level: int,
                 communicator: 'SSH',
                 vault: 'Vault',
                 template: str,
                 local_folder: str,
                 result_filename: str,
                 counter: 'Counter',
                 analysis_status: str
                 ):
        """
        Initializes a Job instance with analysis and precision-related parameters.
        
        Parameters:
            id_reduced_precision (list): IDs of variables in reduced precision.
            forced_ids (list): IDs of variables with forced precision.
            banned_variables (list): Variables excluded from analysis.
            analysis_variables (list): Variables involved in the analysis.
            reduced_precision_level (int): Current precision level.
            communicator (SSH): Facilitates remote communication.
            vault (Vault): Stores and retrieves variables.
            template (str): Job template.
            local_folder (str): Local storage path.
            result_filename (str): Name of the result file.
            counter (Counter): Tracks the job count.
            analysis_status (str): Current status of the analysis.
        """
        super().__init__(id_reduced_precision,
                         forced_ids,
                         reduced_precision_level,
                         analysis_variables,
                         communicator,
                         vault,
                         template,
                         result_filename,
                         counter,
                         local_folder=local_folder,
                         analysis_status=analysis_status)
        # This class extends the classical job putting some extra variables that define the relations
        self.parent = None
        self.child = []
        self.child_batch_list = []
        self.child_number = None
        self.batch_size = 4

        self.reshuffle = False
        self.level = None

        # Other things that need to be saved
        self.banned_variables = banned_variables[:]
        self.local_folder = local_folder
        self.max_retrials = 1
        self.batch_counter = 0
        self.counter = counter
        self.plot_id = 0
        self.last_graph = ""

    def get_variables_reduced_precision(self):
        """
        Retrieves variables under reduced precision from the vault.
        
        Returns:
            list: Variables with reduced precision.
        """
        # Uses the vault to get variables with reduced precision being analyzed from their ids
        return [self.vault.get_variable_by_id(_id) for _id in self.id_reduced_precision]

    def get_cluster_id(self):
        """
        Determines the cluster IDs of variables under reduced precision.
        
        Returns:
            list: Unique cluster IDs, empty if no clusters exist.
        """
        var_reduced_precision = self.get_variables_reduced_precision()
        cluster_id = [var.cluster_id for var in var_reduced_precision]
        # Some variables do not belong to any cluster
        if -1 in cluster_id:
            return []
        # Just clusters in this child
        else:
            return list(set(cluster_id))

    def has_cluster(self):
        """
        Checks whether the job contains clustered variables.
        
        Returns:
            bool: True if clusters exist, False otherwise.
        """
        if self.get_cluster_id():
            return True
        else:
            return False

    def print_info_job(self, status: str):
        """
        Prints job details with the given status.
        
        Parameters:
            status (str): Job status for logging.
        """
        print("Job %s %s %s before computing fitness" % (self.incremental_id, self.hash, status))

    def ancestors(self):
        """
        Retrieves all ancestor jobs of the current job.
        
        Returns:
            list[Job]: List of ancestor jobs.
        """
        to_return = []
        cv = self
        while cv.parent is not None:
            to_return.append(cv.parent)
            cv = cv.parent
        return list(to_return)

    def update_parent_set(self):
        """
        Updates the parent job with banned and reduced precision variables.
        """
        # Root job has not parent to update
        if self.parent is None:
            return
        # Propagate the bad variables to the parent
        banned_variables = self.banned_variables[:]
        # If the job failed, also analyzed variables are bad
        if self.status == "FAILED":
            banned_variables += self.id_reduced_precision[:]
        # Get the paren job
        parent = self.parent
        # Banning one of the good children would add twice the banned variables
        parent.banned_variables += [b for b in banned_variables if b not in parent.banned_variables]
        # Remove bad variables from analyzed set
        parent.id_reduced_precision = [i for i in parent.id_reduced_precision if i not in parent.banned_variables]

    def descendants(self):
        """
        Retrieves all descendant jobs recursively.
        
        Returns:
            list[Job]: Descendants of the current job.
        """
        # Using a recursive approach to obtain the full list of descendants
        if not self.child:
            return []
        else:
            # Getting the two lists of descendants of the two child and merging them in a single list
            child_descendants = sum([child.descendants() for child in self.child], [])
            # Returning the child plus their descendants
            return self.child[:] + child_descendants

    def create_child(self, _id_subset, _index):
        """
        Creates a child job with a subset of variables.
        
        Parameters:
            _id_subset (list): Subset of reduced precision IDs.
            _index (int): Child index in the hierarchy.
        
        Returns:
            Job: Newly created child job.
        """
        child = Job(id_reduced_precision=_id_subset,
                    forced_ids=self.forced_ids,
                    analysis_variables=self.analysis_variables,
                    banned_variables=self.banned_variables,
                    reduced_precision_level=self.reduced_precision_level,
                    communicator=self.communicator,
                    vault=self.vault,
                    template=self.template,
                    local_folder=self.local_folder,
                    result_filename=self.result_filename,
                    counter=self.counter,
                    analysis_status=self.analysis_status
                    )

        child.parent = self
        child.child_number = _index
        child.level = self.level + 1
        return child

    def spawn_children(self):
        """
        Spawns children jobs by dividing variable clusters.
        """
        # Creates set for the two child
        _id_subset = self.divide_set_cluster()

        for index, id_subset in enumerate(_id_subset):
            child = self.create_child(id_subset, index)
            self.child.append(child)

    def fail_child(self, bad_child: 'Job'):
        """
        Marks a child job as failed and propagates failure to its descendants.
        
        Parameters:
            bad_child (Job): The failed child job.
        """
        if not self.child:
            return
        else:
            for child in self.child:
                if child == bad_child or child == bad_child.parent:
                    return
                else:
                    bad_var = bad_child.banned_variables + bad_child.id_reduced_precision
                    common_id = [i for i in bad_var if i in child.id_reduced_precision]
                    if common_id:
                        child.id_reduced_precision = [i for i in child.id_reduced_precision if i not in common_id]
                        child.banned_variables += common_id
                        child.fail_child(bad_child)

    def find_child_set(self, analysis_set_dict: dict):
        """
        Finds and stores active children in the analysis set dictionary.
        
        Parameters:
            analysis_set_dict (dict): Dictionary to store active children.
        """
        for child in self.child:
            if child.status != 'FAILED' and child.id_reduced_precision:
                analysis_set_dict[child.hash] = child
                child.find_child_set(analysis_set_dict)

    def create_children_batch(self):
        """
        Groups child jobs into batches for submission, ordered by banned variables.
        """
        # Save old child structure, that will be destroyed in creating new children
        self.reshuffle = self.child[:]

        # Get the list of all children nodes
        child_analysis_set_dict = {}
        self.find_child_set(child_analysis_set_dict)

        # Sort the dictionary in order of length of variables analyzed
        child_analysis_set_list = sorted(child_analysis_set_dict.values(), key=lambda x: len(x.id_reduced_precision))

        # Compute number of batches needed
        n_batches = len(child_analysis_set_list) // self.batch_size
        if len(child_analysis_set_list) % self.batch_size:
            n_batches += 1
        # Create the structure with right size
        self.child_batch_list = [[] for i in range(n_batches)]

        # Fill the structure
        for idx, child in enumerate(child_analysis_set_list):
            batch_index = idx // self.batch_size
            id_subset = [i for i in self.id_reduced_precision if i not in child.id_reduced_precision]
            banned_variables = self.banned_variables + child.id_reduced_precision
            child = self.create_child(id_subset, child)
            child.banned_variables = banned_variables
            child.reshuffle = True
            self.child_batch_list[batch_index].append(child)

    def divide_set_module(self, variables: list):
        """
        Divides a set of variables into two groups based on module and routine.
        
        Parameters:
            variables (list): Variables to be divided.
        
        Returns:
            tuple: Two subsets of variable IDs.
        """
        import AutoRPE.UtilsRPE.Error as Error
        if len(variables) == 1:
            raise Error.ClusterCantBeDivided("This cluster can't be subdivided anymore")
        # Dividing by modules
        modules = [var.procedure.module.name for var in variables]
        # It is necessary to sort the modules otherwise the order can be different in different runs
        # leading to different groups with different hashes, which prevents reproducibility
        unique_modules = list(sorted(set(modules)))
        if len(unique_modules) > 1:
            d = {}
            for mod in unique_modules:
                d[mod] = modules.count(mod)
            d = {k: v for k, v in sorted(d.items(), key=lambda item: - item[1])}
            g1 = {"mod": [], "val": 0}
            g2 = {"mod": [], "val": 0}
            for key, value in d.items():
                if g1["val"] < g2["val"]:
                    g1["val"] += value
                    g1["mod"].append(key)
                else:
                    g2["val"] += value
                    g2["mod"].append(key)
            set1 = [v.id for v in variables if v.procedure.module.name in g1["mod"]]
            set2 = [v.id for v in variables if v.procedure.module.name in g2["mod"]]
            return set1, set2
        else:
            # Separate by routines
            routines = [var.procedure.name for var in variables]
            unique_routines = list(sorted(set(routines)))
            if len(unique_routines) > 1:
                d = {}
                for routine in unique_routines:
                    d[routine] = routines.count(routine)
                d = {k: v for k, v in sorted(d.items(), key=lambda item: - item[1])}
                g1 = {"mod": [], "val": 0}
                g2 = {"mod": [], "val": 0}
                for key, value in d.items():
                    if g1["val"] < g2["val"]:
                        g1["val"] += value
                        g1["mod"].append(key)
                    else:
                        g2["val"] += value
                        g2["mod"].append(key)
                set1 = [v.id for v in variables if v.procedure.name in g1["mod"]]
                set2 = [v.id for v in variables if v.procedure.name in g2["mod"]]
                return set1, set2
            else:
                # Just separate in two halves
                # assert len(self.id_reduced_precision) > 1
                set1 = []
                set2 = self.id_reduced_precision[:]
                for i in range(int(len(self.id_reduced_precision) / 2)):
                    set1.append(set2.pop(0))
                return set1, set2

    def divide_set_cluster(self):
        """
        Divides variables into subsets based on clusters and module hierarchy.
        
        Returns:
            tuple: Two subsets of variable IDs.
        """

        # Just one variable left, no possibility to further subdivide: fail
        if len(self.id_reduced_precision) == 1:
            raise Error.ClusterCantBeDivided("This cluster can't be subdivided anymore")

        # Retrieve variables being analyzed using the id_reduced_precision
        var_reduced_precision = self.get_variables_reduced_precision()

        # Get their cluster ids
        cluster_id = [var.cluster_id for var in var_reduced_precision]

        # Separate clusters from the rest of the variables (only applies in the first iteration of the tree)
        if -1 in cluster_id and len(set(cluster_id)) > 1:
            set1 = [var.id for var in var_reduced_precision if var.cluster_id == -1]
            set2 = [var.id for var in var_reduced_precision if var.cluster_id != -1]

        # We are dealing with clusters
        elif -1 not in cluster_id:
            # It is necessary to sort the clusters otherwise the order can be different in different runs
            # leading to different groups with different hashes, which prevents reproducibility
            cluster_id = list(set(cluster_id))
            cluster_id.sort()

            # Just one cluster: fail
            if len(cluster_id) == 1:
                raise Error.ClusterCantBeDivided("This cluster can't be subdivided anymore")
            # Two cluster left: divide into two branches
            elif len(cluster_id) == 2:
                set1 = [var.id for var in var_reduced_precision if var.cluster_id == cluster_id[0]]
                set2 = [var.id for var in var_reduced_precision if var.cluster_id == cluster_id[1]]
            # Various clusters: distribute the clusters on the branches in a balanced way
            else:
                set1 = []
                set2 = [var for var in var_reduced_precision if var.cluster_id != cluster_id[-1]]
                while len(cluster_id) > 0 and len(set1) < len(set2):
                    c_id = cluster_id.pop()
                    set1.extend([v for v in var_reduced_precision if v.cluster_id == c_id])
                    set2 = [v for v in set2 if v.cluster_id != c_id]
                set1 = [v.id for v in set1]
                set2 = [v.id for v in set2]
        # 4 - Just independent variables, either global or local: divide by module/subroutine
        else:
            n_main = len([v for v in var_reduced_precision if v.procedure.name == "main"])
            if n_main != 0 and n_main != len(var_reduced_precision):
                set1 = [v.id for v in var_reduced_precision if v.procedure.name == "main"]
                set2 = [v.id for v in var_reduced_precision if v.procedure.name != "main"]
            else:

                set1, set2 = self.divide_set_module(var_reduced_precision)

        return set1, set2

    def divide_function_level(self, variables: list):
        """
        Divides variables into subsets based on function levels.
        
        Parameters:
            variables (list): Variables to be divided.
        
        Returns:
            list: List of subsets of variable IDs.
        """
        sets = []
        levels = list(set([v.procedure.level for v in variables if v.procedure.name != 'main']))
        main_variables = [v.id for v in variables if v.procedure.name == 'main']
        if len(main_variables):
            sets.append(main_variables)
        if len(levels) == 1 or len(main_variables) == len(variables):
            return self.divide_set_module(variables)
        for l in levels:
            sets.append([v.id for v in variables if v.procedure.name != 'main' and v.procedure.level == l])
        return sets

    def kind_of_exception(self):
        """
        Categorizes the exception type when merging sets fails. Types of exception:
            - No exception: It isn't a failed job
            - Intra-routine: All variables belong to same routine
            - Intra-module: All variables belong to same module, but not routine
            - Inter-module: The variables belong to different modules.
        
        Returns:
            str: Type of exception ('IntraRoutine', 'IntraModule', 'InterModule', etc.).
        """
        if not self.child:
            return "TreeLeafFail"
        child_1, child_2 = self.child
        # We'll focus only on the id of reduced precision
        ch1_variables = [self.vault.get_variable_by_id(_id) for _id in child_1.id_reduced_precision]
        ch2_variables = [self.vault.get_variable_by_id(_id) for _id in child_2.id_reduced_precision]
        ch1_routines = set([v.procedure for v in ch1_variables])
        ch2_routines = set([v.procedure for v in ch2_variables])
        if len(ch1_routines.union(ch2_routines)) == 1:
            return "IntraRoutine"
        ch1_modules = set([v.procedure.module for v in ch1_variables])
        ch2_modules = set([v.procedure.module for v in ch2_variables])
        if len(ch1_modules.union(ch2_modules)) == 1:
            return "IntraModule"
        return "InterModule"

    def graph(self):
        """
        Generates a graph representation of the job and its descendants.
        """
        members = self.descendants()

        def style(status, incremental_id):
            if status == "SUCCESS":
                color = "#00b300"
            elif status == "FAILED":
                color = "#e60000"
            elif status == "SUSPENDED":
                color = "#ffff1a"
            else:
                color = "#aaa"
            return "style %s fill:%s\n" % (incremental_id, color)
            # return "style %s fill:%s\n" % (fix_identifier(node.identifier()), color)

        graph = "graph TD\n"
        graph += style(self.status, self.incremental_id)
        max_else_status = 0
        for member in members:
            len_id_reduced_precision = len(member.id_reduced_precision)
            len_banned_var = len(member.banned_variables)
            len_forced_var = len(member.forced_ids)
            ID = member.incremental_id

            if len_id_reduced_precision == 0:
                if len_banned_var:
                    node = "%s --> %s[ " + str(ID) + " : *+" + str(len_banned_var) + "]\n"
                else:
                    node = "%s --> %s[*]\n"
            else:
                if len_banned_var:
                    node = "%s --> %s[ " + str(ID) + " : " + str(len_id_reduced_precision) + "+" + str(
                        len_banned_var) + "]\n"
                elif len_forced_var:
                    node = "%s --> %s[ " + str(ID) + " : " + str(len_id_reduced_precision) + "+ _" + str(
                        len_forced_var) + "]\n"
                else:
                    node = "%s --> %s[" + str(ID) + " : " + str(len_id_reduced_precision) + "]\n"

            graph += node % (member.parent.incremental_id, member.incremental_id)

            graph += style(member.status, member.incremental_id)
            if member.status != "SUCCESS" and member.status != "FAILED" and member.status != "SUSPENDED" \
                    and member.incremental_id >= max_else_status:
                max_else_status = member.incremental_id
        import calendar
        import time
        # ts = calendar.timegm(time.gmtime())
        # print(self.plot_id)

        # mermaid_graph_file = open(
        #     self.local_folder + "/mermaid/plot_" + str(ts) + "last_run_id_" + str(max_else_status) + ".txt", "w")
        if graph != self.last_graph:
            mermaid_graph_file = open(
                self.local_folder + "/mermaid/"+str(self.incremental_id)+"/plot_" + '{:0>4}'.format(self.plot_id) + ".txt", "w")
            mermaid_graph_file.write(graph)
            mermaid_graph_file.close()
            self.plot_id += 1
            self.last_graph = graph


    def plot_variables(self, var_name: str):
        """
        Plots a variable's values over time and compares to error limits.
        
        Parameters:
            var_name (str): Name of the variable to plot.
        
        Returns:
            None | Exception: Returns None if successful, otherwise raises exceptions.
        """
        import matplotlib.pyplot as plt
        import pickle as pkl
        import numpy as np

        hash_folder_name = self.hash

        limit_file_path = f'{self.local_folder}/analysis_configuration_files/limit_file.pkl'
        simulation_rmse_path = f'{self.remote_rundir}/simulation_RMSE.pkl'

        # Open limit file from local folder
        try:
            with open(limit_file_path, 'rb') as file:
                limit_file_data = pkl.load(file)
        except FileNotFoundError:
            print(f'File in {limit_file_path} does not exist.')
            return None
        except Exception as e:
            print(f'An error occurred while opening the file: {e}')
            return None

        # Open simulation result from remote folder:
        buffer_size = 3 * 1024 * 1024
        try:
            with self.communicator.sftp.open(simulation_rmse_path, 'rb', bufsize=buffer_size) as f:
                simulation_rmse_data = pkl.load(f)
        except FileNotFoundError:
            print(f'File in {simulation_rmse_path} does not exist.')
            return None
        except Exception as e:
            print(f'An error occurred while opening the file: {e}')
            return None

        # Limit-file values:
        values_limitfile = None
        for grid_name in limit_file_data.keys():
            if var_name in limit_file_data[grid_name].keys():
                values_limitfile = limit_file_data[grid_name][var_name]
                break
 
        if values_limitfile is None:
            print(f'variable "{var_name}" could not be found in file "{limit_file_path}"')
            return None
 
        bottom, top, mean = values_limitfile[0], values_limitfile[1], values_limitfile[2]
 
        # Simulation RMSE values:
        values_simulation = None
        for grid_name in simulation_rmse_data.keys():
            if var_name in simulation_rmse_data[grid_name].keys():
                values_simulation = simulation_rmse_data[grid_name][var_name]
                break

        if values_simulation is None:
            print(f'variable "{var_name}" could not be found in file "{simulation_rmse_path}"')
            return None

        # Start plotting
        fig, ax = plt.subplots()

        # TODO
        time = np.linspace(0, 1, len(mean))

        # Plotting the mean values
        ax.plot(time, mean, label='Ensemble mean error', color='lightblue', linestyle='dashed')

        # Plotting the error spread
        ax.fill_between(time, bottom, top, color='lightblue', edgecolor='none', alpha=0.5, label='Ensemble error spread')

        # Plotting the simulation values
        ax.plot(time, values_simulation, label='Simulation RMSE', color='brown')

        # Adding labels, legend and title
        title = f'RMSE of variable {var_name} over time vs the limits set by the limit-file.'
        ax.set_xlabel('time axis')
        ax.set_ylabel(f'{var_name}')
        ax.set_title(title)
        ax.legend(loc='best')

        # Save the plot
        image_name = f'var_{var_name}_job_{self.hash}.png'
        plt.savefig(image_name, bbox_inches='tight', pad_inches=0.25)
