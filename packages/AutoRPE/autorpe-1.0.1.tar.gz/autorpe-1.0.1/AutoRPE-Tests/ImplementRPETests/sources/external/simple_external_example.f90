program simple_subroutine_example
    implicit none

    ! Declare the external subroutine to be passed
    ! external :: my_subroutine

    real :: x, y, result

    x = 5.0
    y = 10.0

    ! Call the subroutine 'compute' and pass 'my_subroutine' as an argument
    call compute(x, y, my_subroutine, result)

    print *, 'The result is:', result

contains

    ! Define the external subroutine outside the main program
    subroutine my_subroutine(a, b, c)
        real, intent(in) :: a, b
        real, intent(out) :: c

        c = a + b
    end subroutine my_subroutine

    ! Define the subroutine 'compute' that accepts a subroutine argument
    subroutine compute(a, b, subrtn, res)
        implicit none
        real, intent(in) :: a, b
        real, intent(out) :: res
        external :: subrtn   ! Declare 'subrtn' as an external subroutine

        ! Call the passed subroutine
        call subrtn(a, b, res)
    end subroutine compute

end program simple_subroutine_example