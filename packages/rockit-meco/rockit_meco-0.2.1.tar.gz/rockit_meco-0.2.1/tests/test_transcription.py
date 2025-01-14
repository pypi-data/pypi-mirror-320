import unittest

from rockit import Ocp, DirectMethod, MultipleShooting, FreeTime, DirectCollocation, SingleShooting, UniformGrid, GeometricGrid, FreeGrid
from problems import integrator_control_problem, vdp, vdp_dae
from casadi import DM, jacobian, sum1, sum2, MX, rootfinder
from numpy import sin, pi, linspace
from numpy.testing import assert_array_almost_equal
try:
  from contextlib import redirect_stdout
except:
  redirect_stdout = None
from io import StringIO
import numpy as np



class TranscriptionTests(unittest.TestCase):

    def test_order(self):
      import logging
      from io import StringIO
      log_stream = StringIO()
      log_handler = logging.StreamHandler(log_stream)
      logging.basicConfig(stream=log_stream, level=logging.DEBUG)

      #  (free-time problems can be configured with `FreeTime(initial_guess)`)
      ocp = Ocp(t0=0, T=10)

      # Define two scalar states (vectors and matrices also supported)
      x1 = ocp.state()
      x2 = ocp.state()

      # Define one piecewise constant control input
      #  (use `order=1` for piecewise linear)
      u = ocp.control()

      # Compose time-dependent expressions a.k.a. signals
      #  (explicit time-dependence is supported with `ocp.t`)
      e = 1 - x2**2

      # Specify differential equations for states
      #  (DAEs also supported with `ocp.algebraic` and `add_alg`)
      ocp.set_der(x1, e * x1 - x2 + u)
      ocp.set_der(x2, x1)

      # Lagrange objective term: signals in an integrand
      ocp.add_objective(ocp.integral(x1**2 + x2**2 + u**2))
      # Mayer objective term: signals evaluated at t_f = t0_+T
      ocp.add_objective(ocp.at_tf(x1**2))

      # Path constraints
      #  (must be valid on the whole time domain running from `t0` to `tf`,
      #   grid options available such as `grid='inf'`)
      ocp.subject_to(x1 >= -0.25)
      ocp.subject_to(-1 <= (u <= 1 ))

      # Boundary constraints
      ocp.subject_to(ocp.at_t0(x1) == 0)
      ocp.subject_to(ocp.at_t0(x2) == 1)

      #%%
      # Solving the problem
      # -------------------

      # Pick an NLP solver backend
      #  (CasADi `nlpsol` plugin):
      ocp.solver('ipopt')

      # Pick a solution method
      #  e.g. SingleShooting, MultipleShooting, DirectCollocation
      #
      #  N -- number of control intervals
      #  M -- number of integration steps per control interval
      #  grid -- could specify e.g. UniformGrid() or GeometricGrid(4)
      method = MultipleShooting(N=10, intg='rk')
      ocp.method(method)

      # Solve
      sol = ocp.solve()

      log_stream.seek(0)
      lines = log_stream.readlines()
      return
      self.assertTrue(lines.count('INFO:root:augment\n')==1)
      self.assertTrue(lines.count('INFO:root:transcribe\n')==1)
      log_pos = log_stream.tell()

      # Solve
      sol = ocp.solve()

      log_stream.seek(log_pos)
      lines = log_stream.readlines()
      self.assertTrue(lines.count('INFO:root:augment\n')==0)
      self.assertTrue(lines.count('INFO:root:transcribe\n')==0)
      log_pos = log_stream.tell()

      method = MultipleShooting(N=20, intg='rk')
      ocp.method(method)

      # Solve
      sol = ocp.solve()

      log_stream.seek(log_pos)
      lines = log_stream.readlines()
      self.assertTrue(lines.count('INFO:root:augment\n')==1)
      self.assertTrue(lines.count('INFO:root:transcribe\n')==1)
      log_pos = log_stream.tell()


      ocp.set_initial(u, 6)

      # Solve
      sol = ocp.solve()

      log_stream.seek(log_pos)
      lines = log_stream.readlines()
      self.assertTrue(lines.count('INFO:root:augment\n')==0)
      self.assertTrue(lines.count('INFO:root:transcribe\n')==0)
      log_pos = log_stream.tell()



if __name__ == '__main__':
    unittest.main()
