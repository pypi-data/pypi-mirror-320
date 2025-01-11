
module testFile

contains

    subroutine testIntrinsics()
        INTEGER , INTENT(in) :: kmm      ! ocean time level index
        REAL(wp), INTENT(in) :: ptem
        REAL(wp), DIMENSION(jpi,jpj), INTENT(out) :: pdept

        LOG(kmm) ! af
        INT(ptem) ! Integer
        cmplx(ptem) ! Complex
        trim(ptem) ! Char
        present(ptem) ! Logical
        c_loc(ptem) ! Pointer
        rpe(ptem) ! rpe_var
        float(ptem) ! rpe_var

    end subroutine testIntrinsics

end module testFile