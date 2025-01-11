module dummy_module
    IMPLICIT NONE

    PRIVATE
    PUBLIC :: dummy_routine
CONTAINS
    SUBROUTINE dummy_routine
        real(4) :: A, B, C

        A = 1
        B = 3

        
        C = A + B
    END SUBROUTINE dummy_routine

END MODULE dummy_module