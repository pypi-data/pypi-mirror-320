import unittest

from pylab import *

from rockit import Ocp, DirectMethod, MultipleShooting, DirectCollocation, SingleShooting, SplineMethod
from problems import integrator_control_problem, bang_bang_chain_problem
import numpy as np
import casadi as ca

class IntegrTests(unittest.TestCase):

    def test_all(self):
        T = 7
        N = 10

        for intg in ['rk','cvodes']:
            ocp = Ocp(T=T)
            x_c = ocp.state()
            x_d = ocp.state()
            u = ocp.control()
            ocp.set_der(x_c, 0.3*x_d+0.8*x_c+0.7*u)
            ocp.set_next(x_d, 0.2*x_c+0.1*x_d+0.4*u)

            ocp.subject_to(ocp.at_t0(x_c)==0.7)
            ocp.subject_to(ocp.at_t0(x_d)==0.8)
            ocp.subject_to(u==ocp.t,include_last=False)

            ocp.solver('ipopt')
            ocp.method(MultipleShooting(N=N,intg=intg))
            sol = ocp.solve()

            x_c_sol = sol.sample(x_c,grid='control')[1]
            x_d_sol = sol.sample(x_d,grid='control')[1]
            u_sol = sol.sample(u,grid='control')[1]
            
            # Check correctness of discrete dynamics
            self.assertAlmostEqual(x_d_sol[0], 0.8)
            for k in range(N):
                self.assertAlmostEqual(x_d_sol[k+1], 0.2*x_c_sol[k]+0.1*x_d_sol[k]+0.4*u_sol[k])
            # Check correctness of continuous dynamics
            self.assertAlmostEqual(x_c_sol[0], 0.7)
            options = {}
            if intg == 'rk':
                options = {"number_of_finite_elements": 1}
            intg = ca.integrator('intg',intg,{"x": x_c, "p": x_d, "u": u, "ode": 0.3*x_d+0.8*x_c+0.7*u},0,T/N,options)
            for k in range(N):
                self.assertAlmostEqual(intg(x0=x_c_sol[k],p=x_d_sol[k],u=u_sol[k])["xf"], x_c_sol[k+1])

        
if __name__ == '__main__':
    unittest.main()
