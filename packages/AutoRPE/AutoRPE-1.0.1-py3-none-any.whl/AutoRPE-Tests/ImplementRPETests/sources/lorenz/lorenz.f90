!*****************************************************************************
! Lorenz ODE Solver
! Adapted version of the original code by John Burkardt
!
! License:
!   This code is adapted from the work of John Burkardt and is distributed
!   under the MIT license.
!*****************************************************************************


program main
  use lorenz_constants
  use lorenz_routines
  implicit none

  real(kind=rk) :: t(0:n), x(m, 0:n), dt, t_final
  integer :: j
  character(len=255) :: data_filename
  open(unit=10, file='lorenz_trajectories.csv', status='replace')

  ! Initialize parameters
  t_final = 40.0d0
  dt = t_final / real(n, kind=rk)
  t = [(real(j, kind=rk) * t_final / real(n, kind=rk), j = 0, n)]
  x(:, 0) = (/ 8.0d0, 1.0d0, 1.0d0 /)

  ! Time integration using RK4
  do j = 0, n - 1
    call rk4vec(t(j), x(:, j), dt, lorenz_rhs, x(:, j + 1))
  end do

  ! Write results to CSV file
  write(10, '(a)') 'Time,X,Y,Z'
  do j = 0, n
    write(10, '(f10.6, ",", f10.6, ",", f10.6, ",", f10.6)') t(j), x(:, j)
  end do

  close(10)

  print *, 'Trajectories saved to "lorenz_trajectories.csv".'
end program main