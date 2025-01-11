!*****************************************************************************
! Lorenz ODE Solver
! Adapted version of the original code by John Burkardt
!
! License:
!   This code is adapted from the work of John Burkardt and is distributed
!   under the MIT license.
!*****************************************************************************


module lorenz_routines
    use lorenz_constants
    implicit none
  contains
  
    subroutine lorenz_rhs(t, x, dxdt)
      real(kind=rk), intent(in) :: t
      real(kind=rk), intent(in) :: x(m)
      real(kind=rk), intent(out) :: dxdt(m)
  
      dxdt(1) = sigma * (x(2) - x(1))
      dxdt(2) = x(1) * (rho - x(3)) - x(2)
      dxdt(3) = x(1) * x(2) - beta * x(3)
    end subroutine lorenz_rhs
  
    subroutine rk4vec(t0, u0, dt, f, u)
      real(kind=rk), intent(in) :: t0, dt
      real(kind=rk), intent(in) :: u0(m)
      external :: f
      real(kind=rk), intent(out) :: u(m)
  
      real(kind=rk) :: f0(m), f1(m), f2(m), f3(m)
      real(kind=rk) :: u1(m), u2(m), u3(m)
  
      call f(t0, u0, f0)
  
      call f(t0 + dt / 2.0d0, u0 + dt * f0 / 2.0d0, f1)
      call f(t0 + dt / 2.0d0, u0 + dt * f1 / 2.0d0, f2)
      call f(t0 + dt, u0 + dt * f2, f3)
  
      u = u0 + dt * (f0 + 2.0d0 * f1 + 2.0d0 * f2 + f3) / 6.0d0
    end subroutine rk4vec
  
  end module lorenz_routines