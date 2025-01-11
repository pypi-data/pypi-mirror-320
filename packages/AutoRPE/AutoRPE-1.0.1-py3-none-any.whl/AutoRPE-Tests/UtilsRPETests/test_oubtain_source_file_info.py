import AutoRPE.UtilsRPE.ObtainSourceFileInfo as ObtainSourceFileInfo


def test_find_function_type_from_header_1():
    header = 'RECURSIVE FUNCTION nodal_factort( kformula ) RESULT( zf )'
    var_declaration = [
        'INTEGER, INTENT(in) ::   kformula',
        'type(rpe_var)            ::   zf',
        'type(rpe_var)            :: zs',
        'type(rpe_var)            :: zf1',
        'type(rpe_var)            :: zf2',
        'CHARACTER(LEN=3)         ::   clformula',
    ]
    ret_type, ret_val = ObtainSourceFileInfo.find_function_type_from_header(header, var_declaration)
    expected_retval = [None, 'zf']
    assert [ret_type, ret_val] == expected_retval


def test_find_function_type_from_header_2():
    header = '   type(rpe_var) function bdy_segs_surf(phu, phv)'
    var_declaration = [
        'type(rpe_var), DIMENSION(jpi,jpj), INTENT(in)  :: phu',
        'type(rpe_var), DIMENSION(jpi,jpj), INTENT(in)  :: phv',
        'INTEGER             :: igrd',
        'INTEGER             :: ib_bdy',
        'INTEGER             :: ib',
        'INTEGER , POINTER   :: nbi',
        'INTEGER , POINTER   :: nbj',
        'type(rpe_var), POINTER   :: zflagu',
        'type(rpe_var), POINTER   :: zflagv',
    ]
    ret_type, ret_val = ObtainSourceFileInfo.find_function_type_from_header(header, var_declaration)
    expected_retval = ['rpe_var', 'bdy_segs_surf']
    assert [ret_type, ret_val] == expected_retval


def test_find_function_type_from_header_3():
    header = '   function dia_ptr_alloc()'
    var_declaration = [
        'INTEGER               ::   dia_ptr_alloc',
        'INTEGER, DIMENSION(3) ::   ierr',
    ]
    ret_type, ret_val = ObtainSourceFileInfo.find_function_type_from_header(header, var_declaration)
    expected_retval = [None, 'dia_ptr_alloc']
    assert [ret_type, ret_val] == expected_retval
