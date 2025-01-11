module dummy_module
    USE dummy_foo_module, ONLY:dummy_foo
    IMPLICIT NONE

    PRIVATE
    PUBLIC :: dummy_routine
CONTAINS
    SUBROUTINE dummy_routine
        real(4) :: A, B, C

        A = 1
        B = 3

        
        C = dummy_foo(A,B)
    END SUBROUTINE dummy_routine

END MODULE dummy_module