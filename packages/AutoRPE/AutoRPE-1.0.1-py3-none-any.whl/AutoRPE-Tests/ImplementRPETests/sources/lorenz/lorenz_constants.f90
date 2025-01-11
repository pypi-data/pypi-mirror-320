!*****************************************************************************
! Lorenz ODE Solver
! Adapted version of the original code by John Burkardt
!
! License:
!   This code is adapted from the work of John Burkardt and is distributed
!   under the MIT license.
!*****************************************************************************


module lorenz_constants
    implicit none
    integer, parameter :: rk = kind(1.0d0)
    integer, parameter :: m = 3
    integer, parameter :: n = 10000
    real(kind=rk), parameter :: beta = 8.0d0 / 3.0d0
    real(kind=rk), parameter :: rho = 28.0d0
    real(kind=rk), parameter :: sigma = 10.0d0
end module lorenz_constants