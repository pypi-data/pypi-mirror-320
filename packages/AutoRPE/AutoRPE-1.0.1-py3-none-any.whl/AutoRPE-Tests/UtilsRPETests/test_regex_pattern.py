import re
from AutoRPE.UtilsRPE import RegexPattern


def test_regex_hardcoded_array_1():
    string = ' (/ llnon, llson, llean, llwen /)'
    array_match = re.match(RegexPattern.hardcoded_array, string)
    assert array_match.group() == string


def test_regex_hardcoded_array_2():
    string = ' (/ (zshift + REAL(ji,wp), ji = 1, jpi_crs*jpj_crs) /)'
    array_match = re.match(RegexPattern.hardcoded_array, string)
    assert array_match.group() == string


def test_regex_hardcoded_array_3():
    string = '(/sd(ju)%ln_tint/)'
    array_match = re.match(RegexPattern.hardcoded_array, string)
    assert array_match.group() == string


def test_regex_hardcoded_array_4():
    string = '(/ sdjf%cltype == \'monthly\' .OR. idy == 0 /)'
    array_match = re.match(RegexPattern.hardcoded_array, string)
    assert array_match.group() == string.strip()


def test_regex_hardcoded_array_no_match():
    string = 'RESHAPE( (/pfield1d%val/), (/1,1,SIZE(pfield1d%val)/) )'
    array_match = re.match(RegexPattern.hardcoded_array, string)
    assert array_match is None


def test_regex_array_in_write_statement():
    string = '(iall_rank(idum) ,all_etime(idum),all_ctime(idum),zall_ratio(idum),idum=1, jpnij)'
    array_match = re.search(RegexPattern.array_in_write_statement, string)
    assert array_match.group() == string


def test_regex_is_call_to_function1():
    string = '   SUBROUTINE asm_inc_init( Kbb, Kmm, Krhs )'
    assert re.search(RegexPattern.call_to_function, string, flags=re.I) is None


def test_regex_is_call_to_function2():
    string = '   call asm_inc_init( Kbb, Kmm, Krhs )'
    assert re.search(RegexPattern.call_to_function, string, flags=re.I) is None


def test_regex_is_call_to_function3():
    string = ' asm_inc_init( Kbb, Kmm, Krhs )'
    assert re.search(RegexPattern.call_to_function, string, flags=re.I).group() == 'asm_inc_init('


def test_regex_real_with_precision():
    string = 'real ( kind = rk ), parameter :: sigma = 10.0D+00'
    assert re.search(RegexPattern.real_with_precision_declaration_name, string, flags=re.I) is not None

def test_regex_real_with_precision_declaration():
    """
    Testing cases for which should be detected as a precision declaration.
    """
    pattern = RegexPattern.real_with_precision_declaration
    cases = [
        'REAL(wp), DIMENSION(:,:,:), ALLOCATABLE, PUBLIC :: real_calving',
        'real :: _calving(:,:,:) = 0._wp',
        'REAL(wp), ALLOCATABLE, DIMENSION(:) :: zreal1d',
        'REAL(wp), DIMENSION(ntsi-(nn_hls):ntei+(nn_hls),ntsj-(nn_hls):ntej+(nn_hls),jpk,jpts) :: zab'
    ]
    for case in cases:
        assert re.search(pattern, case, flags=re.I) is not None


def test_regex_real_with_precision_declaration_groups():
    """
    Testing cases for which should be detected as a precision declaration,
    checking that the groups are detected as well.
    """

    pattern = RegexPattern.real_with_precision_declaration
    cases = {
        'REAL(dp), DIMENSION(jpi,jpj,jpk,jpts,jpt), INTENT(inout) :: pts': "REAL(dp)",
        'REAL(wp) :: zta': 'REAL(wp)',
        'REAL(wp) :: zalfa': 'REAL(wp)'
    }
    for string, result in cases.items():
        match = re.search(pattern, string, flags=re.I)
        assert match is not None, f"No match for: {string}"
        groups = match.groups()
        assert len(groups) > 0, f"No groups captured for: {string}"
        assert groups[0] == result, f"Expected: {result}, Got: {groups[0]}"


def test_regex_real_with_precision_negative():
    """
    Testing cases for which shouldn't be detected as a precision declaration.
    """

    pattern = RegexPattern.real_with_precision_declaration
    cases = [
        'real_calving(ki,kj,kn)     = real_calving(ki,kj,kn) + pcalved / berg_dt'
    ]
    
    for case in cases:
        assert re.search(pattern, case, flags=re.I) is None
    

def test_regex_traditional_declaration_pattern():
    """
    Testing cases for which should be detected as a traditional declaration,
    checking that the groups are detected as well.
    """
    pattern = RegexPattern.traditional_declaration_pattern
    pattern = re.compile(pattern)

    cases = {
        'real ( kind = rk ) t(0:n)' : ("real", "t(0:n)")
    }

    for case, results in cases.items():
        ref_dtype, ref_variables = results
        match = pattern.match(case)
        dtype = match.group(1)  # Data type (real, integer, etc.)
        kind_len = match.group(2) if match.group(2) else ''  # Kind or length specifier
        dimension = match.group(3) if match.group(3) else ''  # Dimension attribute
        variables = match.group(4)
        assert variables is not None
        assert ref_dtype == dtype and ref_variables == variables


def test_regex_traditional_declaration_pattern_negative():
    """
    Testing for cases that should not be detected as traditional declaration
    """
    pattern = RegexPattern.traditional_declaration_pattern
    cases = [
    '      real_calving(:,:,:) = 0._wp'
    ]
    for case in cases:
        assert re.search(pattern, case, flags=re.I) is None
    