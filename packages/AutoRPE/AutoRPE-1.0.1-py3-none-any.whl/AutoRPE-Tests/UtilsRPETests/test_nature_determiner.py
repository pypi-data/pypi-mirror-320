import AutoRPE.UtilsRPE.NatureDeterminer as NatureDeterminer


def test_has_operations():
    string = 'SUM( a_i(:,:,:)%val - a_i_b(:,:,:)%val, dim=3 ) * r1_Dt_ice'
    assert NatureDeterminer.has_operations(string)


def test_has_operations_2():
    # Some cases that appear in NEMO
    cases = [
        'kndims=indims',
        'lduld=lluld',
        'kfillmode=jpfillnothing',
        'lsend=llsend2',
        'ktype = jp_i4',
        'pfillval=1.0_wp',
    ]
    for case in cases:
        assert not NatureDeterminer.has_operations(case)


def test_has_intrinsics():
    string = 'MAXVAL(zCu_cfl%val,dim=3)'
    assert NatureDeterminer.has_intrinsics(string)
