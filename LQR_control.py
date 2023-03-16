
import math
import random

import matplotlib.pyplot as plt
import numpy as np
import scipy
from CBFsteer import CBF_RRT
import time

SHOW_ANIMATION = False


class LQRPlanner:

    def __init__(self):
        self.MAX_TIME = 100.0  # Maximum simulation time
        self.DT = 0.05  # Time tick
        self.GOAL_DIST = 0.1
        self.MAX_ITER = 150
        self.EPS = 0.01

        # control limitation
        self.u_lower_lim = -5
        self.u_upper_lim = 5

         # Linear system model
        self.A, self.B = self.get_system_model()
        # LQR gain is invariant
        self.K = self.lqr_control(self.A, self.B)

    def lqr_planning(self, sx, sy, gx, gy, show_animation=True):

        rx, ry = [sx], [sy]

        error = []

        x = np.array([sx - gx, sy - gy]).reshape(2, 1)  # State vector

        found_path = False


        time = 0.0
        while time <= self.MAX_TIME:
            time += self.DT

            u = self.K @ x

            u = np.clip(u, self.u_lower_lim, self.u_upper_lim)

            x = self.A @ x + self.B @ u

            rx.append(x[0, 0] + gx)
            ry.append(x[1, 0] + gy)


            d = math.sqrt((gx - rx[-1]) ** 2 + (gy - ry[-1]) ** 2)
            error.append(d)

            if d <= self.GOAL_DIST:
                found_path = True
                # print('errors ', d)
                break

            # animation
            if show_animation:  # pragma: no cover
                # for stopping simulation with the esc key.
                plt.gcf().canvas.mpl_connect('key_release_event',
                        lambda event: [exit(0) if event.key == 'escape' else None])
                plt.plot(sx, sy, "or")
                plt.plot(gx, gy, "ob")
                plt.plot(rx, ry, "-r")
                plt.axis("equal")
                plt.pause(1.0)

        if not found_path:
            print("Cannot found path")
            return rx, ry, error,found_path

        return rx, ry, error,found_path


    def dlqr(self, A,B,Q,R):
        """
        Solve the discrete time lqr controller.
        x[k+1] = A x[k] + B u[k]
        cost = sum x[k].T*Q*x[k] + u[k].T*R*u[k]
        """
        # first, solve the ricatti equation
        P = np.matrix(scipy.linalg.solve_discrete_are(A, B, Q, R))
        # compute the LQR gain
        K = np.matrix(scipy.linalg.inv(B.T*P*B+R)*(B.T*P*A))

        eigVals, eigVecs = scipy.linalg.eig(A-B*K)
        
        return -K

    def get_system_model(self):

        A = np.matrix([[1, 0],[0 , 1]])

        B = np.matrix([[self.DT, 0], [0, self.DT]])


        return A, B

    def lqr_control(self, A, B):

        Q = np.matrix("1 0; 0 1")
        R = np.matrix("0.01 0; 0 0.01")

        Kopt = self.dlqr(A, B, Q, R)


        return Kopt


def main():
    print(__file__ + " start!!")

    ntest = 1  # number of goal
    area = 50.0  # sampling area

    lqr_planner = LQRPlanner()

    for i in range(ntest):
        start_time = time.time()
        sx = 6.0
        sy = 6.0
        gx = random.uniform(-area, area)
        gy = random.uniform(-area, area)

        rx, ry, error, foundpath = lqr_planner.lqr_planning(sx, sy, gx, gy, show_animation=SHOW_ANIMATION)


        f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)

        print("time of running LQR: ", time.time() - start_time)

        ax1.plot(sx, sy, "or")
        ax1.plot(gx, gy, "ob")
        ax1.plot(rx, ry, "-r")
        ax1.grid()
        
        ax2.plot(error, label="errors")
        ax2.legend(loc='upper right')
        ax2.grid()
        plt.show()




        if SHOW_ANIMATION:  # pragma: no cover
            plt.plot(sx, sy, "or")
            plt.plot(gx, gy, "ob")
            plt.plot(rx, ry, "-r")
            plt.axis("equal")
            plt.pause(1.0)


if __name__ == '__main__':

    main()