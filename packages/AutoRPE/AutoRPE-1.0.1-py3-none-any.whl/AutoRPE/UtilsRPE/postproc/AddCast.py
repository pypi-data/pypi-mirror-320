import AutoRPE.UtilsRPE.BasicFunctions as BasicFunctions
import AutoRPE.UtilsRPE.Classes.Subprogram as Subprogram
import AutoRPE.UtilsRPE.CallManager as CallManager
import AutoRPE.UtilsRPE.Getter as Getter
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
import AutoRPE.UtilsRPE.RegexPattern as RegexPattern
import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer
import AutoRPE.UtilsRPE.Error as Error
import re


class SubprogramCast:
    def __init__(self, index_dummy, argument_index, precision):
        # The index of the dummy argument
        self.index_dummy = index_dummy if isinstance(index_dummy, list) else [index_dummy]
        # The index of the corresponding argument in call, can change if the argument is optional
        self.argument_index = argument_index if isinstance(argument_index, list) else [argument_index]
        self.precision = precision if isinstance(precision, list) else [precision]


def new_add_casts(dictionary_of_fix):
    import AutoRPE.UtilsRPE.postproc.AddCastUtils as AddCastUtils
    print("\n")
    module_procedure = []
    len_of_fix = len(dictionary_of_fix)
    for fix_ind, subprogram_name in enumerate(dictionary_of_fix):
        print("\rFixing exception %i/%i subprogram %s" % (fix_ind + 1, len_of_fix, subprogram_name), end="")
        subprogram_cast = dictionary_of_fix[subprogram_name]

        for key in subprogram_cast:
            if subprogram_name.count('lbclnk'):
                print("\n"+subprogram_name+' need fix in block '+subprogram_cast[key][0].block.name+"\n")
            if len(subprogram_cast[key]) > 10:
                module_procedure.append([subprogram_cast[key][0].subprogram, key])
            subprogram_calls = subprogram_cast[key]
            # Remove identical calls because they could be fixed twice
            subprogram_calls = remove_redundant_call(subprogram_calls)
            for call in subprogram_calls:

                # Find the call, if not, raise an error
                module = call.block.module
                lines_idx = AddCastUtils.find_subprogram_call(call, module)

                fixed = False
                for idx in lines_idx:
                    # Fix all the argument that need cast in line
                    for arg_ind, arg_precision in zip(call.cast.argument_index, call.cast.precision):
                        var_to_fix = call.arguments[arg_ind].name
                        if NatureDeterminer.is_a_number(var_to_fix):
                            print('here')

                        try:
                            fixed_line = AddCastUtils.cast_variable(var_to_fix, arg_precision, module.lines[idx])
                        except (Error.LineNotFound, Error.ExceptionNotManaged):
                            break
                        fixed = True
                        module.lines[idx] = fixed_line
                if not fixed:
                    raise Error.LineNotFound("call %s not found" % call)
    print("\n")
    for m_p in module_procedure:
        print("Function %s, level %i not fixed, and interface is needed on dummy %s" % (m_p[0].name,
                                                                                        m_p[0].level,
                                                                                        m_p[1]))


def remove_redundant_call(subprogram_calls):
    """When two identical call are present, they will be fixed at the same time,
       Remove the redundant call"""
    ret_val = []
    # Find the block
    block_name = list(set([c.block.name for c in subprogram_calls]))
    for b_n in block_name:
        # Remove the identical calls
        unique_call = list(set([c.call for c in subprogram_calls if c.block.name == b_n]))
        # Create a new array with just the unique
        for u_c in unique_call:
            ret_val.append([sc for sc in subprogram_calls if sc.block.name == b_n and sc.call == u_c][0])
    return ret_val


def add_casts(original_modules, dictionary_of_fix):
    import AutoRPE.UtilsRPE.postproc.OriginalFilesManager as OriginalFilesManager
    print("\n")
    module_procedure = []
    len_of_fix = len(dictionary_of_fix)
    for fix_ind, subprogram_name in enumerate(dictionary_of_fix):
        print("\rFixing exception %i/%i subprogram %s" % (fix_ind + 1, len_of_fix, subprogram_name), end="")
        subprogram_cast = dictionary_of_fix[subprogram_name]

        for key in subprogram_cast:
            if subprogram_name.count('lbclnk'):
                print("\n"+subprogram_name+' need fix in block '+subprogram_cast[key][0].block.name+"\n")
                break
            if len(subprogram_cast[key]) > 10 and not subprogram_name == 'prt_ctl_mp_prtctl':
                module_procedure.append([subprogram_cast[key][0].subprogram, key])
                continue
            subprogram_calls = subprogram_cast[key]
            # Remove identical calls because they could be fixed twice
            already_fixed = {}
            for call in subprogram_calls:
                if call.block.name not in already_fixed:
                    already_fixed[call.block.name] = [call.call]
                else:
                    # When two identical call are present, they will be fixed at the same time,
                    # when trying to fix the second call it will not exist any more, since it was fixed on first call
                    if call.call in already_fixed[call.block.name]:
                        continue
                    else:
                        already_fixed[call.block.name] += [call.call]
                try:
                    found_lines = OriginalFilesManager.find_subprogram_call(call, original_modules)
                except Error.LineNotFound:
                    continue
                fixed = False
                for line in found_lines.lines:
                    original_module = found_lines.original_module
                    OriginalFilesManager.add_include_clause(original_module)

                    # Fix all the argument that need cast in line
                    for arg_ind, arg_precision in zip(call.cast.argument_index, call.cast.precision):
                        var_to_fix = call.arguments[arg_ind].name
                        try:
                            index, fixed_line = OriginalFilesManager.cast_variable(var_to_fix, arg_precision,
                                                                                   original_module, line)
                        except (Error.LineNotFound, Error.ExceptionNotManaged):
                            break
                        fixed = True
                        original_module.lines[index] = fixed_line
                if not fixed:
                    raise Error.LineNotFound("call %s not found" % call)
    print("\n")
    for m_p in module_procedure:
        print("Function %s, level %i not fixed, and interface is needed on dummy %s" % (m_p[0].name,
                                                                                        m_p[0].level,
                                                                                        m_p[1]))
    return original_modules


def update_call(subprogram_call, vault):
    """Actual arguments may have change type due to previous iteration: update
       If subprogram is an interface: need to update keys and interface
    """
    for s_call in subprogram_call[:]:
        for arg in s_call.arguments:
            if arg.variable:
                arg.type = arg.variable.type
            else:
                arg.type = Getter.get_type_of_contents(arg.name, s_call.block, vault)
        if s_call.subprogram.interface:
            update_call_interface(s_call, vault)


def fill_cast_obj(subprogram_call, vault):
    """Stores into a cast object the fixes needed for each subprogram call"""
    # If is external, should already be ok
    if subprogram_call[0].subprogram.is_external:
        return

    # Update actual interface called and remove call from vault dictionary if interface has changed
    # (it can't be done inside the loop!!)
    update_call(subprogram_call, vault)

    for ind, s_call in enumerate(subprogram_call):
        for arg, dummy_a in zip(s_call.arguments, s_call.dummy_arguments):
            # If dummy_a is of the same type of actual argument
            # or one is wp and the other is dp:return True if wp=dp, False otherwise
            if VariablePrecision.type_are_equivalent(arg.type, dummy_a.type, working_precision="sp"):
                continue
            if NatureDeterminer.is_a_number(arg.name):
                print(arg.name)
            # If the called arg is external and the dummy is not real, no need to check
            if arg.type == "external" and dummy_a.type not in VariablePrecision.real_id:
                continue
            # Inconsistency between used argument and what the call expects
            if dummy_a.intent == "in":
                # If is wp, maintain wp
                # If is sp for sure there is a dp version of this, otherwise the code would not work in dp
                if dummy_a.type in [VariablePrecision.real_id['sp'], VariablePrecision.real_id['wp']]:
                    cast_precision = 'wp'
                else:
                    # There is no sp/dp interface (otherwise we would be in the other branch of the if/else)
                    cast_precision = dummy_a.type
                # From the dummy argument name in the subprogram object get its real position in this call
                argument_index = [da.name for da in s_call.dummy_arguments].index(dummy_a.name)
                # If a call that need fix to more than one arg, don't create another object, just append the index
                if not s_call.cast:
                    s_call.cast \
                        = SubprogramCast(dummy_a.position, argument_index, cast_precision)
                else:
                    if dummy_a.position not in s_call.cast.index_dummy:
                        s_call.cast.index_dummy.append(dummy_a.position)
                        s_call.cast.argument_index.append(argument_index)
                        s_call.cast.precision.append(cast_precision)

            # The value of the argument can be modified by the call
            else:
                if not s_call.call.count('lbc_lnk'):
                    print("This should not happen! Check the modify variable script %s" % s_call.call)
                # raise Error.ExceptionNotManaged("This should not happen! Check the modify variable script")
        # else:
        #     # This is only temporal, we don't need to check external calls, they should be already ok
        #     called_arguments = s_call.arguments
        #     # In case the procedure is not found, consider it external
        #     for argument in called_arguments:
        #         # This is a stupid workaround, since it works for NEMO but possibly not with other codes
        #         if argument.type == "sp" and not s_call.block.name.count("_sp"):
        #             pass
        #             print("\nThis should not happen! Check the modify variable script %s" % s_call.call)


def cast_obj2dict(fixes):
    """Fill a dictionary with all the call that need fix, the key will be the index of the argument that need fix"""
    dict_of_fix = {}
    argument_to_fix = []
    for f in fixes:
        index = f.cast.index_dummy
        # Sort not to duplicate key: 1_3 is the same as 3_1
        index.sort()
        dict_key = _key_from_index(index)
        if index not in argument_to_fix:
            argument_to_fix.append(index)
            dict_of_fix[dict_key] = [f]
        else:
            dict_of_fix[dict_key] += [f]

    return dict_of_fix


def get_cast_dictionary(vault):
    # All the dummy argument that need to change precision
    list_of_variables = []

    # When a dummy changes its precision, the key gets updated
    for interface in vault.interfaces_dictionary:
        vault.interfaces_dictionary[interface].generate_key()

    change_dummy = True
    while change_dummy:
        change_dummy = False
        # Update key at every cycle, since dummy keep changing
        for interface in vault.interfaces_dictionary:
            vault.interfaces_dictionary[interface].generate_key()

        # Dictionary that will contain all the subprogram calls that need fix for each subprogram
        dictionary_of_cast = {}
        # Analyze all the call and add cast where needed
        # n_cast = 0
        # for call in list(dictionary_of_calls):
        #     fill_cast_obj(dictionary_of_calls[call], vault)
        #     n_cast += len([c for c in dictionary_of_calls[call] if c.cast])
        # print("\rNcast %i " % n_cast, end="")
        dictionary_of_calls = vault.dictionary_of_calls
        list_of_calls = list(dictionary_of_calls)
        list_of_calls.sort()
        for idx_call, call in enumerate(list_of_calls):
            if change_dummy:
                print(call, str(idx_call) + "/" + str(len(list_of_calls)))
                break
            # List all the call that need a cast
            fill_cast_obj(dictionary_of_calls[call], vault)
            try:
                # It can be that the call corresponds to an interface no longer exist in the dictionary
                cast = [c for c in dictionary_of_calls[call] if c.cast]
            except KeyError:
                cast = []
            n_call_to_fix = len(cast)
            if not n_call_to_fix:
                continue

            # Transform the list of cast in a dictionary where the key is the index of the argument to cast
            dictionary_of_cast[call] = cast_obj2dict(cast)
            keys = [index for index in dictionary_of_cast[call]]
            for dict_key in keys:
                index = _index_from_key(dict_key)
                fixed_cast = []
                for arg_idx, idx in enumerate(index):
                    # List of original calls that use this dummy but do not cast it
                    o_c = [i for i in dictionary_of_calls[call] if [da for da in i.dummy_arguments if
                                                                    da.position == idx] and
                           (not i.cast or (i.cast and idx not in i.cast.index_dummy))]
                    # List of fix on this argument
                    f_c = [i for i in dictionary_of_calls[call] if i.cast and (idx in i.cast.index_dummy)]
                    # If more than half of the calls have fixes, then change the dummy
                    if not o_c or (len(o_c) < len(f_c)):
                        # Change the precision of this dummy argument
                        dummy_arg = dictionary_of_calls[call][0].subprogram.dummy_arguments[idx]
                        # Set it to argument type
                        argument_index = dictionary_of_cast[call][dict_key][0].cast.argument_index[arg_idx]
                        dummy_arg.type = dictionary_of_cast[call][dict_key][0].arguments[argument_index].type
                        list_of_variables.append(dummy_arg)
                        if dummy_arg.type == 'dp' and not dummy_arg.intent == "in":
                            raise Error.ExceptionNotManaged("We can not change dp to sp unless it is an interface")
                        # Write a list of the call where a fix was made
                        for c in f_c:
                            fixed_cast.append(c)
                        change_dummy = True
                # An index was changed in subprogram, the cast dictionary has to be recreated
                if change_dummy:
                    for c in fixed_cast:
                        c.cast = None
                    break

    for call in list(dictionary_of_cast):
        # Analyze the dictionary and groups casts together to have the smallest number of interface
        dictionary_of_cast[call] = analyze_dict_of_cast(dictionary_of_cast[call])

    # Get fixes on reshape statement
    # reshape_dict = get_reshape_fixes(vault)

    print_info(dictionary_of_cast, dictionary_of_calls)

    return list_of_variables, dictionary_of_cast, {}


def print_info(dictionary_of_cast, dictionary_of_calls):
    n_cast = 0
    total_call = 0
    fix_in_loop = 0
    for call in dictionary_of_cast:
        n_call = len(dictionary_of_calls[call])
        for dict_key in list(dictionary_of_cast[call]):
            n_call = len(dictionary_of_cast[call][dict_key])
            n_of_index = len(_index_from_key(dict_key))
            # Create an interface
            if n_call - n_call > 11 and n_call > 10:
                if dictionary_of_cast[call][dict_key][0].subprogram.interface:
                    print('The function %s need %i/%i fixes over argument %s' % (call, n_call, n_call, dict_key))
                else:
                    print(
                        'No interface for %s over argument %s, call %i/%i times' % (call, dict_key, n_call, n_call))
            # Add cast to the call
            else:
                fix_in_loop += len(
                    [c for c in dictionary_of_cast[call][dict_key] if c.line_info.loop_depth]) * n_of_index
                n_cast += n_call * n_of_index
                total_call += n_call
    print("A total of %i cast has been added on %i call, of which %i inside loops" % (n_cast, total_call, fix_in_loop))


def get_reshape_fixes(vault):
    dictionary_of_fix = {}
    n_of_modules = len(vault.modules)
    subprogram = Subprogram.Function('RESHAPE', None, is_external=True)
    for index, module in enumerate(vault.modules.values()):
        print("\rFinding reshape exception %i/%i  %20s" % (index + 1, n_of_modules, module.name), end="")
        for line_index, line in enumerate(module.lines):
            # Returns arguments of subprograms call and corresponding type and dummy
            temporal_call = BasicFunctions.remove_if_condition(line)
            reshape_call = re.search(RegexPattern.reshape_function, temporal_call, re.I)
            if reshape_call:
                # for call like RESHAPE((/(zshift + REAL(ji,wp), ji = 1, jpi_crs*jpj_crs) /), (/ jpi_crs, jpj_crs /))
                if reshape_call.group(1).count("="):
                    continue
                # else:
                #     # Split hardcoded_array has been removed: check that reshape_call.group(1) is correct
                #     called_arguments = CallManager.find_call_arguments(reshape_call.group(2))
                call = reshape_call.group(0)
                subprogram_call = CallManager.create_SubprogramCall(call,
                                                                    subprogram, module.line_info[line_index].block, vault)
                # If something was found check if can be fixed
                different_type = list(set([a.type for a in subprogram_call.arguments]))
                if len(different_type) != 1:
                    type_1_idx = [idx for idx, a in enumerate(subprogram_call.arguments) if a.type == different_type[0]]
                    type_2_idx = [idx for idx, a in enumerate(subprogram_call.arguments) if a.type == different_type[1]]

                    if len(type_1_idx) > len(type_2_idx):
                        subprogram_cast = SubprogramCast(subprogram_call, type_2_idx, different_type[0])
                    else:
                        subprogram_cast = SubprogramCast(subprogram_call, type_1_idx, different_type[1])

                    try:
                        dictionary_of_fix["RESHAPE"] += [subprogram_cast]
                    except KeyError:
                        dictionary_of_fix["RESHAPE"] = [subprogram_cast]
    print('\n')
    return dictionary_of_fix


def _key_from_index(index):
    index.sort()
    return "_".join([str(i) for i in index])


def _index_from_key(index):
    return [int(i) for i in index.split("_")]


def recreate_dict_key(dictionary):
    """Creates a dictionary whose keys are the index of the arguments that need fixes"""
    new_dict = {}
    for key in dictionary:
        argument_to_fix = []
        array_of_fix = dictionary[key]
        for f in array_of_fix:
            index = f.cast.index_dummy
            # Sort not to duplicate key: 1_3 is the same as 3_1
            index.sort()
            if index not in [[a] for a in argument_to_fix]:
                argument_to_fix.extend(index)
        argument_to_fix = list(set(argument_to_fix))
        argument_to_fix.sort()
        new_key = _key_from_index(argument_to_fix)
        new_dict[new_key] = array_of_fix
    return new_dict


def analyze_dict_of_cast(subprogram_fix):
    """Different calls need cast on different argument indexes, try to see if a unique interface can be created"""
    list_of_index = []
    for key in subprogram_fix:
        list_of_index.extend(_index_from_key(key))
    key = list(set(list_of_index))
    subprogram_fix = create_unique_interface(key, subprogram_fix)
    # The dimension of the dictionary is going to change, loop on the list of key instead of keys
    for index in list(subprogram_fix):
        # For the moment discard group of optional arguments
        if len(index.split("_")) != 1:
            continue
        # Find calls, among the ones that need casts, that does not use the same optional arg
        subprogram = subprogram_fix[index][0].subprogram
        if subprogram.dummy_arguments[int(index)].is_optional:
            # Find the index that can be fixed at the same time as the optional one
            index_to_contract = contract_index(subprogram_fix, index)
            if index_to_contract:
                # Add the list of fix to the new index
                subprogram_fix[index_to_contract] += subprogram_fix[index]
                # Delete old dictionary key
                del subprogram_fix[index]

    # After grouping fix for different dummy argument, the dictionary key need to be fixed
    return recreate_dict_key(subprogram_fix)


def create_unique_interface(key, fix):
    cast_to_group = []
    for f in list(fix):
        arg_to_fix = _index_from_key(f)
        fix_to_remove = []
        for call in fix[f]:
            arg_not_to_fix = []
            arg_not_to_fix.extend([da.position for da in call.dummy_arguments if da.position not in arg_to_fix])
            if not [a for a in arg_not_to_fix if a in key]:
                cast_to_group.append(call)
                fix_to_remove.append(call)
        for r in fix_to_remove:
            fix[f].remove(r)
        if not fix[f]:
            del fix[f]
    if cast_to_group:
        fix[_key_from_index(key)] = cast_to_group
    return fix


def update_call_interface(subprogram_call, vault):
    call_name = subprogram_call.subprogram.module.name + "_mp_" + subprogram_call.subprogram.name

    # Get the interface subprogram now that keys have been updated
    interface = check_interface(subprogram_call, vault)
    if not interface:
        # Casting intent in arguments, an interface should be found
        interface = check_interface(subprogram_call, vault, uniform_intent='in')
    if interface:
        if interface != subprogram_call.subprogram:
            if not interface.has_mixed_interface:
                raise Error.ExceptionNotManaged("A mixed interface has been found, must be an error")
            vault.dictionary_of_calls[call_name].remove(subprogram_call)
            # Check there are still calls to this interface, otherwise delete the key
            if not vault.dictionary_of_calls[call_name]:
                del vault.dictionary_of_calls[call_name]
            subprogram_call.subprogram = interface
            new_da = []
            for da in subprogram_call.dummy_arguments:
                new_da += [interface.dummy_arguments[da.position]]
            subprogram_call.dummy_arguments = new_da
            new_call_name = interface.module.name + "_mp_" + interface.name
            try:
                vault.dictionary_of_calls[new_call_name] += [subprogram_call]
            except KeyError:
                vault.dictionary_of_calls[new_call_name] = [subprogram_call]
    else:
        interface = check_interface(subprogram_call, vault, uniform_intent='all')
        if interface:
            raise Error.ExceptionNotManaged("Function %s of level %i need interface. Please, create and rerun"
                                            % (interface.name, interface.level))
        else:
            raise Error.InterfaceNotFound("No possible interface found for call %s. Check" % subprogram_call.call)


def check_interface(subprogram_call, vault, uniform_intent=None):
    """The vault has been created with wp=dp, so some interfaces are the _dp instead of _sp"""
    interface = subprogram_call.subprogram.interface
    called_arguments = CallManager.find_call_arguments(subprogram_call.call)

    try:
        return Getter.get_interface(called_arguments, interface, subprogram_call.block, vault, uniform_intent)
    except Error.InterfaceNotFound:
        return False


def contract_index(dict_of_fix, index):
    """Search among call that need fix, the ones that does not use this optional argument"""
    for k in dict_of_fix:
        if k != index:
            call_with_same_arg = [call for call in dict_of_fix[k] if index in
                                  [da.position for da in call.dummy_arguments]]
            if not call_with_same_arg:
                return k
