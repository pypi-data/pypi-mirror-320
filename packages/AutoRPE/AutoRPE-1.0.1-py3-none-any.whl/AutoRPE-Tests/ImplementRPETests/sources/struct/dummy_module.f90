MODULE dummy_module
    IMPLICIT NONE

    PRIVATE
    PUBLIC :: dummy_routine, DummyStruct

    ! Define a derived type (struct) with real elements
    TYPE :: DummyStruct
        REAL(4) :: A, B, C
    END TYPE DummyStruct

CONTAINS

    ! Subroutine to demonstrate usage of the DummyStruct
    SUBROUTINE dummy_routine()
        IMPLICIT NONE
        TYPE(DummyStruct) :: my_struct

        ! Assign values to the struct's components
        my_struct%A = 1.0
        my_struct%B = 3.0

        ! Perform a calculation and assign the result to another component
        my_struct%C = my_struct%A + my_struct%B

        ! Print the results
        PRINT *, "A =", my_struct%A
        PRINT *, "B =", my_struct%B
        PRINT *, "C = A + B =", my_struct%C
    END SUBROUTINE dummy_routine

END MODULE dummy_module
