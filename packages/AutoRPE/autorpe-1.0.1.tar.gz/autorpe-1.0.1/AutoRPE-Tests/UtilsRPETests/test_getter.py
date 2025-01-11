import AutoRPE.UtilsRPE.Getter as Getter
from AutoRPE.UtilsRPE import VariablePrecision


def test_get_function_type():
    from AutoRPE.UtilsRPE.Classes.Vault import Vault
    from AutoRPE.UtilsRPE.Classes.Subprogram import SubRoutine
    from AutoRPE.UtilsRPE.Classes.Variable import Variable
    from AutoRPE.UtilsRPE.Classes.Module import Module
    import AutoRPE.UtilsRPE.Classes.SourceFile as SourceFile

    
    dummy_file = SourceFile.SourceFile("dummy", ".f90")

    module = Module(dummy_file, extension=".f90")
    subroutine = SubRoutine("dummy", module)
    var_1 = Variable(subroutine, "Kmm", _type="integer", _dimension=1, _module=module)
    subroutine.accessible_var["Kmm"] = [var_1]
    vault = Vault()
    
    test_cases = [
        ("LOG(Kmm)", 'integer'),
        ("INT(Kmm)", 'integer'),
        ("cmplx(Kmm)", 'complex'),
        ("trim(Kmm)", 'char'),
        (" present(Kmm)", 'logical'),
        ("c_loc(Kmm)", 'pointer'),
        ("rpe(Kmm)", 'rpe_var'),
        ("float(Kmm)", VariablePrecision.real_id['wp']),
    ]
    
    for string, expected in test_cases:
        assert Getter.get_function_type(string, subroutine, vault) == expected


def test_type_of_real_cast_with_double_specification():
    string = 'real((ssh(:,:,kmm)+ssh_ref)*tmask(:,:,1),dp)'
    assert Getter.get_type_of_real_cast(string) == 'dp'


def test_type_of_real_cast_with_single_specification():
    string = 'real((ssh(:,:,kmm)+ssh_ref)*tmask(:,:,1),sp)'
    assert Getter.get_type_of_real_cast(string) == VariablePrecision.real_id['sp']


def test_type_of_real_cast_no_specification():
    string = 'real((ssh(:,:,kmm)+ssh_ref)*tmask(:,:,1))'
    assert Getter.get_type_of_real_cast(string) == VariablePrecision.real_id['wp']


def test_set_working_precision():
    VariablePrecision.set_working_precision("sp")
    assert VariablePrecision.value_of_working_precision["wp"] == VariablePrecision.real_id['sp']
    
    VariablePrecision.set_working_precision("dp")
    assert VariablePrecision.value_of_working_precision["wp"] == VariablePrecision.real_id['dp']


def test_dimension_of_contents_1():
    from AutoRPE.UtilsRPE.Classes.Vault import Vault
    from AutoRPE.UtilsRPE.Classes.Subprogram import SubRoutine
    from AutoRPE.UtilsRPE.Classes.Module import Module
    import AutoRPE.UtilsRPE.Classes.SourceFile as SourceFile
    
    vault = Vault()
    dummy_file = SourceFile.SourceFile("dummy", ".f90")
    dummy_module = Module(dummy_file, ".f90")
    dummy_subroutine = SubRoutine("dummy", dummy_module)
    
    assert Getter.get_dimension_of_contents("1.0", block=dummy_subroutine, vault=vault) == 0


def test_dimension_of_contents_2():
    from AutoRPE.UtilsRPE.Classes.Vault import Vault
    from AutoRPE.UtilsRPE.Classes.Subprogram import SubRoutine
    from AutoRPE.UtilsRPE.Classes.Module import Module
    import AutoRPE.UtilsRPE.Classes.SourceFile as SourceFile
    from AutoRPE.UtilsRPE.Classes.Variable import Variable
    
    # Define file, module and subroutine
    vault = Vault()
    dummy_file = SourceFile.SourceFile("dummy", ".f90")
    dummy_module = Module(dummy_file, ".f90")
    dummy_subroutine = SubRoutine("dummy", dummy_module)

    # Define variables
    vars = ["z3d", "e3t_0", "tmask"]
    for var_name in vars:
        var = Variable(dummy_subroutine, var_name, _type="real", _dimension=3, _module=dummy_module)
        dummy_subroutine.accessible_var[var_name] = [var]
    
    # Test dimensions
    string = "real(  ( ( z3d(:,:,:) - e3t_0(:,:,:) ) / e3t_0(:,:,:) * 100 * tmask(:,:,:) ) ** 2  )"
    dimension = Getter.get_dimension_of_contents(string, block=dummy_subroutine, vault=vault)
    assert dimension == 3


def test_dimension_of_contents_3():
    from AutoRPE.UtilsRPE.Classes.Vault import Vault
    from AutoRPE.UtilsRPE.Classes.Subprogram import SubRoutine
    from AutoRPE.UtilsRPE.Classes.Module import Module
    import AutoRPE.UtilsRPE.Classes.SourceFile as SourceFile
    from AutoRPE.UtilsRPE.Classes.Variable import Variable
    
    vault = Vault()
    dummy_file = SourceFile.SourceFile("dummy", ".f90")
    dummy_module = Module(dummy_file, ".f90")
    dummy_subroutine = SubRoutine("dummy", dummy_module)

    # Define variables
    vars = ["e1e2t", "zfwf"]
    for var_name in vars:
        var = Variable(dummy_subroutine, var_name, _type="real", _dimension=2, _module=dummy_module)
        dummy_subroutine.accessible_var[var_name] = [var]

    
    string = "e1e2t(:,:) * zfwf(:,:)"
    dimension = Getter.get_dimension_of_contents(string, block=dummy_subroutine, vault=vault)
    assert dimension == 2


def test_dimension_of_contents():
    from AutoRPE.UtilsRPE.Classes.Vault import Vault
    from AutoRPE.UtilsRPE.Classes.Subprogram import SubRoutine
    from AutoRPE.UtilsRPE.Classes.Module import Module
    import AutoRPE.UtilsRPE.Classes.SourceFile as SourceFile
    from AutoRPE.UtilsRPE.Classes.Variable import Variable

    
    vault = Vault()
    dummy_file = SourceFile.SourceFile("dummy", ".f90")
    dummy_module = Module(dummy_file, ".f90")
    dummy_subroutine = SubRoutine("dummy", dummy_module)
    
    # Define variables and dimensions:
    vars = {
        "a_i":3,
        "a_i_b":3,
        "zs1":2,
        "zs2":2,
        "zs12":2,
        "zmsk00":2
        }
    for var_name, dimension in vars.items():
        var = Variable(dummy_subroutine, var_name, _type="real", _dimension=dimension, _module=dummy_module)
        dummy_subroutine.accessible_var[var_name] = [var]

    cases = [
        ('SUM( a_i(:,:,:)%val - a_i_b(:,:,:)%val, dim=3 )', 2),
        ('SQRT( ( zs1(:,:)%val - zs2(:,:)%val )**2 + 4*zs12(:,:)%val**2 ) * zmsk00(:,:)', 2),
    ]
    
    for string, expected in cases:
        assert Getter.get_dimension_of_contents(string, block=dummy_subroutine, vault=vault) == expected
