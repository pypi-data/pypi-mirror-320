module dummy_foo_module
    IMPLICIT NONE

    PRIVATE
    PUBLIC :: dummy_foo
CONTAINS
    FUNCTION dummy_foo (A,B) RESULT(C)
        real(4) :: A, B, C

        A = 1
        B = 3
   
        C = A + B
    END FUNCTION dummy_foo

end module dummy_foo_module
! END MODULE