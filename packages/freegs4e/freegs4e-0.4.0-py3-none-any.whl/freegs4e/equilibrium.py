"""
Defines class to represent the equilibrium
state, including plasma and coil currents

Modified substantially from the original FreeGS code.

Copyright 2024 Nicola C. Amorisco, Adriano Agnello, George K. Holt, Ben Dudson.

FreeGS4E is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FreeGS4E is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with FreeGS4E.  If not, see <http://www.gnu.org/licenses/>.
"""

import warnings

import matplotlib.pyplot as plt
import numpy as np
import shapely as sh
from numpy import array, exp, linspace, meshgrid, pi
from scipy import interpolate
from scipy.integrate import romb  # Romberg integration

# Multigrid solver
from . import critical, machine, multigrid, polygons
from .boundary import fixedBoundary, freeBoundary

# Operators which define the G-S equation
from .gradshafranov import GSsparse, GSsparse4thOrder, mu0


class Equilibrium:
    """
    Represents the equilibrium state, including
    plasma and coil currents

    Data members
    ------------

    These can be read, but should not be modified directly

    R[nx,ny]
    Z[nx,ny]

    Rmin, Rmax
    Zmin, Zmax

    tokamak - The coils and circuits

    Private data members

    _applyBoundary()
    _solver - Grad-Shafranov elliptic solver
    _profiles     An object which calculates the toroidal current
    _constraints  Control system which adjusts coil currents to meet constraints
                  e.g. X-point location and flux values
    """

    def __init__(
        self,
        tokamak=machine.EmptyTokamak(),
        Rmin=0.1,
        Rmax=2.0,
        Zmin=-1.0,
        Zmax=1.0,
        nx=65,
        ny=65,
        boundary=freeBoundary,
        psi=None,
        current=0.0,
        order=4,
    ):
        """Initialises a plasma equilibrium

        Rmin, Rmax  - Range of major radius R [m]
        Zmin, Zmax  - Range of height Z [m]

        nx - Resolution in R. This must be 2^n + 1
        ny - Resolution in Z. This must be 2^m + 1

        boundary - The boundary condition, either freeBoundary or fixedBoundary

        psi - Magnetic flux. If None, use concentric circular flux
              surfaces as starting guess

        current - Plasma current (default = 0.0)

        order - The order of the differential operators to use.
                Valid values are 2 or 4.
        """

        self.tokamak = tokamak

        self._applyBoundary = boundary

        self.Rmin = Rmin
        self.Rmax = Rmax
        self.Zmin = Zmin
        self.Zmax = Zmax

        self.R_1D = linspace(Rmin, Rmax, nx)
        self.Z_1D = linspace(Zmin, Zmax, ny)
        self.R, self.Z = meshgrid(self.R_1D, self.Z_1D, indexing="ij")

        if psi is None:
            # Starting guess for psi
            psi = self.create_psi_plasma_default()
            self.gpars = np.array([0.5, 0.5, 0, 2])
        self.plasma_psi = psi

        # Calculate coil Greens functions. This is an optimisation,
        # used in self.psi() to speed up calculations
        self._pgreen = tokamak.createPsiGreens(self.R, self.Z)

        self._current = current  # Plasma current

        # self._updatePlasmaPsi(psi)  # Needs to be after _pgreen

        # Create the solver
        if order == 2:
            generator = GSsparse(Rmin, Rmax, Zmin, Zmax)
        elif order == 4:
            generator = GSsparse4thOrder(Rmin, Rmax, Zmin, Zmax)
        else:
            raise ValueError(
                "Invalid choice of order ({}). Valid values are 2 or 4.".format(
                    order
                )
            )
        self.order = order

        self._solver = multigrid.createVcycle(
            nx, ny, generator, nlevels=1, ncycle=1, niter=2, direct=True
        )

    def create_psi_plasma_default(
        self, adaptive_centre=False, gpars=(0.5, 0.5, 0, 2)
    ):
        """Creates a Gaussian starting guess for plasma_psi"""
        nx, ny = np.shape(self.R)
        xx, yy = meshgrid(
            linspace(0, 1, nx), linspace(0, 1, ny), indexing="ij"
        )

        if adaptive_centre == True:
            ntot = np.sum(self.mask_inside_limiter)
            xc = (
                np.sum(
                    self.mask_inside_limiter
                    * linspace(0, 1, nx)[:, np.newaxis]
                )
                / ntot
            )
            yc = (
                np.sum(
                    self.mask_inside_limiter
                    * linspace(0, 1, ny)[np.newaxis, :]
                )
                / ntot
            )
        else:
            xc, yc = gpars[:2]
        psi = exp(
            gpars[2]
            - ((np.abs(xx - xc)) ** gpars[3] + (np.abs(yy - yc)) ** gpars[3])
        )

        psi[0, :] = 0.0
        psi[:, 0] = 0.0
        psi[-1, :] = 0.0
        psi[:, -1] = 0.0
        return psi

    def setSolverVcycle(self, nlevels=1, ncycle=1, niter=1, direct=True):
        """
        Creates a new linear solver, based on the multigrid code

        nlevels  - Number of resolution levels, including original
        ncycle   - The number of V cycles
        niter    - Number of linear solver (Jacobi) iterations per level
        direct   - Use a direct solver at the coarsest level?

        """
        generator = GSsparse(self.Rmin, self.Rmax, self.Zmin, self.Zmax)
        nx, ny = self.R.shape

        self._solver = multigrid.createVcycle(
            nx,
            ny,
            generator,
            nlevels=nlevels,
            ncycle=ncycle,
            niter=niter,
            direct=direct,
        )

    def setSolver(self, solver):
        """
        Sets the linear solver to use. The given object/function must have a __call__ method
        which takes two inputs

        solver(x, b)

        where x is the initial guess. This should solve Ax = b, returning the result.

        """
        self._solver = solver

    def callSolver(self, psi, rhs):
        """
        Calls the psi solver, passing the initial guess and RHS arrays

        psi   Initial guess for the solution (used if iterative)
        rhs

        Returns
        -------

        Solution psi

        """
        return self._solver(psi, rhs)

    def getMachine(self):
        """
        Returns the handle of the machine, including coils
        """
        return self.tokamak

    def plasmaCurrent(self):
        """
        Plasma current [Amps]
        """
        return self._current

    def poloidalBeta(self):
        """
        Return the poloidal beta
        betap = (8pi/mu0) * int(p)dRdZ / Ip^2
        """

        dR = self.R[1, 0] - self.R[0, 0]
        dZ = self.Z[0, 1] - self.Z[0, 0]

        # Normalised psi
        psi_norm = (self.psi() - self.psi_axis) / (
            self.psi_bndry - self.psi_axis
        )

        # Plasma pressure
        pressure = self.pressure(psi_norm)
        try:
            pressure *= self._profiles.limiter_core_mask
        except AttributeError as e:
            print(e)
            warnings.warn(
                "The core mask is not in place. You need to solve for the equilibrium first!"
            )
            raise e

        # Integrate pressure in 2D
        return (
            ((8.0 * pi) / mu0)
            * romb(romb(pressure))
            * dR
            * dZ
            / (self.plasmaCurrent() ** 2)
        )

    def plasmaVolume(self):
        """Calculate the volume of the plasma in m^3"""

        dR = self.R[1, 0] - self.R[0, 0]
        dZ = self.Z[0, 1] - self.Z[0, 0]

        # Volume element
        dV = 2.0 * pi * self.R * dR * dZ

        try:
            dV *= self._profiles.limiter_core_mask
        except AttributeError as e:
            print(e)
            warnings.warn(
                "The core mask is not in place. You need to solve for the equilibrium first!"
            )
            raise e

        # Integrate volume in 2D
        return romb(romb(dV))

    def plasmaBr(self, R, Z):
        """
        Radial magnetic field due to plasma
        Br = -1/R dpsi/dZ
        """
        return -self.psi_func(R, Z, dy=1, grid=False) / R

    def plasmaBz(self, R, Z):
        """
        Vertical magnetic field due to plasma
        Bz = (1/R) dpsi/dR
        """
        return self.psi_func(R, Z, dx=1, grid=False) / R

    def Br(self, R, Z):
        """
        Total radial magnetic field
        """
        return self.plasmaBr(R, Z) + self.tokamak.Br(R, Z)

    def Bz(self, R, Z):
        """
        Total vertical magnetic field
        """
        return self.plasmaBz(R, Z) + self.tokamak.Bz(R, Z)

    def Btor(self, R, Z):
        """
        Toroidal magnetic field
        """
        # Normalised psi
        psi_norm = (self.psiRZ(R, Z) - self.psi_axis) / (
            self.psi_bndry - self.psi_axis
        )

        # Get f = R * Btor in the core. May be invalid outside the core
        fpol = self.fpol(psi_norm)

        try:
            fpol = (
                fpol * self._profiles.limiter_core_mask
                + (1.0 - self._profiles.limiter_core_mask) * self.fvac()
            )
        except AttributeError as e:
            print(e)
            warnings.warn(
                "The core mask is not in place. You need to solve for the equilibrium first!"
            )
            raise e

        return fpol / R

    def psi(self):
        """
        Total poloidal flux ψ (psi), including contribution from
        plasma and external coils.
        """
        # return self.plasma_psi + self.tokamak.psi(self.R, self.Z)
        return self.plasma_psi + self.tokamak.calcPsiFromGreens(self._pgreen)

    def psiRZ(self, R, Z):
        """
        Return poloidal flux psi at given (R,Z) location
        """
        return self.psi_func(R, Z, grid=False) + self.tokamak.psi(R, Z)

    def fpol(self, psinorm):
        """
        Return f = R*Bt at specified values of normalised psi
        """
        return self._profiles.fpol(psinorm)

    def fvac(self):
        """
        Return vacuum f = R*Bt
        """
        return self._profiles.fvac()

    def q(self, psinorm=None, npsi=100):
        """
        Returns safety factor q at specified values of normalised psi

        psinorm is a scalar, list or array of floats betweem 0 and 1.

        >>> safety_factor = eq.q([0.2, 0.5, 0.9])

        If psinorm is None, then q on a uniform psi grid will be returned,
        along with the psi values

        >>> psinorm, q = eq.q()

        Note: psinorm = 0 is the magnetic axis, and psinorm = 1 is the separatrix.
              Calculating q on either of these flux surfaces is problematic,
              and the results will probably not be accurate.
        """
        if psinorm is None:
            # An array which doesn't include psinorm = 0 or 1
            psinorm = linspace(1.0 / (npsi + 1), 1.0, npsi, endpoint=False)
            return psinorm, critical.find_safety(self, psinorm=psinorm)

        result = critical.find_safety(self, psinorm=psinorm)
        # Convert to a scalar if only one result
        if len(result) == 1:
            return np.asscalar(result)
        return result

    def pprime(self, psinorm):
        """
        Return p' at given normalised psi
        """
        return self._profiles.pprime(psinorm)

    def ffprime(self, psinorm):
        """
        Return ff' at given normalised psi
        """
        return self._profiles.ffprime(psinorm)

    def pressure(self, psinorm, out=None):
        """
        Returns plasma pressure at specified values of normalised psi
        """
        return self._profiles.pressure(psinorm)

    def separatrix(self, ntheta=20):
        """
        Returns an array of ntheta (R, Z) coordinates of the separatrix,
        equally spaced in geometric poloidal angle.
        """
        return array(critical.find_separatrix(self, ntheta=ntheta))[:, 0:2]

    def solve(self, profiles, Jtor=None, psi=None, psi_bndry=None):
        """
        Calculate the plasma equilibrium given new profiles
        replacing the current equilibrium.

        This performs the linear Grad-Shafranov solve

        profiles  - An object describing the plasma profiles.
                    At minimum this must have methods:
             .Jtor(R, Z, psi)   -> [nx, ny]
             .pprime(psinorm)
             .ffprime(psinorm)
             .pressure(psinorm)
             .fpol(psinorm)

        Jtor : 2D array
            If supplied, specifies the toroidal current at each (R,Z) point
            If not supplied, Jtor is calculated from profiles by finding O,X-points

        psi_bndry  - Poloidal flux to use as the separatrix (plasma boundary)
                     If not given then X-point locations are used.
        """

        self._profiles = profiles

        if Jtor is None:
            # Calculate toroidal current density

            if psi is None:
                psi = self.psi()
            Jtor = profiles.Jtor(self.R, self.Z, psi, psi_bndry=psi_bndry)

        # Set plasma boundary
        # Note that the Equilibrium is passed to the boundary function
        # since the boundary may need to run the G-S solver (von Hagenow's method)
        self._applyBoundary(self, Jtor, self.plasma_psi)

        # Right hand side of G-S equation
        rhs = -mu0 * self.R * Jtor

        # Copy boundary conditions
        rhs[0, :] = self.plasma_psi[0, :]
        rhs[:, 0] = self.plasma_psi[:, 0]
        rhs[-1, :] = self.plasma_psi[-1, :]
        rhs[:, -1] = self.plasma_psi[:, -1]

        # Call elliptic solver
        plasma_psi = self._solver(self.plasma_psi, rhs)

        self._updatePlasmaPsi(plasma_psi)

        # Update plasma current
        dR = self.R[1, 0] - self.R[0, 0]
        dZ = self.Z[0, 1] - self.Z[0, 0]
        self._current = romb(romb(Jtor)) * dR * dZ

    def _updatePlasmaPsi(self, plasma_psi):
        """
        Sets the plasma psi data, updates spline interpolation coefficients.
        Also updates:

        self.mask        2D (R,Z) array which is 1 in the core, 0 outside
        self.psi_axis    Value of psi on the magnetic axis
        self.psi_bndry   Value of psi on plasma boundary
        """
        self.plasma_psi = plasma_psi

        # Update spline interpolation
        self.psi_func = interpolate.RectBivariateSpline(
            self.R[:, 0], self.Z[0, :], plasma_psi
        )

        # Update the locations of the X-points, core mask, psi ranges.
        # Note that this may fail if there are no X-points, so it should not raise an error
        # Analyse the equilibrium, finding O- and X-points
        psi = self.psi()
        opt, xpt = critical.find_critical(self.R, self.Z, psi)
        # if opt:
        self.psi_axis = opt[0][2]

        if len(xpt) > 0:
            self.psi_bndry = xpt[0][2]
            self.mask = critical.inside_mask(
                self.R, self.Z, psi, opt, xpt, self.mask_outside_limiter
            )

            # Use interpolation to find if a point is in the core.
            self.mask_func = interpolate.RectBivariateSpline(
                self.R[:, 0], self.Z[0, :], self.mask
            )
        elif self._applyBoundary is fixedBoundary:
            # No X-points, but using fixed boundary
            self.psi_bndry = psi[0, 0]  # Value of psi on the boundary
            self.mask = None  # All points are in the core region
        else:
            self.psi_bndry = None
            self.mask = None

    def plot(self, axis=None, show=True, oxpoints=True):
        """
        Plot the equilibrium flux surfaces

        axis     - Specify the axis on which to plot
        show     - Call matplotlib.pyplot.show() before returning
        oxpoints - Plot X points as red circles, O points as green circles

        Returns
        -------

        axis  object from Matplotlib

        """
        from .plotting import plotEquilibrium

        return plotEquilibrium(self, axis=axis, show=show, oxpoints=oxpoints)

    def getForces(self):
        """
        Calculate forces on the coils

        Returns a dictionary of coil label -> force
        """
        return self.tokamak.getForces(self)

    def printForces(self):
        """
        Prints a table of forces on coils
        """
        print("Forces on coils")

        def print_forces(forces, prefix=""):
            for label, force in forces.items():
                if isinstance(force, dict):
                    print(prefix + label + " (circuit)")
                    print_forces(force, prefix=prefix + "  ")
                else:
                    print(
                        prefix
                        + label
                        + " : R = {0:.2f} kN , Z = {1:.2f} kN".format(
                            force[0] * 1e-3, force[1] * 1e-3
                        )
                    )

        print_forces(self.getForces())

    def innerOuterSeparatrix(
        self, Z: float = 0.0, recalculate_equilibrium: bool = True
    ):
        """
        Locate R co ordinates of separatrix at both inboard and outboard
        poloidal midplane (Z = 0).

        If the equilibrium has recently been solved, you can set
        recalculate_equilibrium to False to avoid recalculating it.

        Parameters
        ----------
        Z : float, optional
            The Z value at which to find the separatrix. Defaults to
            0.0.
        recalculate_equilibrium : bool, optional
            Whether or not to recalculate the equilibrium. Defaults to
            True.

        Returns
        -------
        R_sep_in : float
            The inner separatrix major radius.
        R_sep_out : float
            The outer separatrix major radius.
        """
        # Find the closest index to requested Z
        Zindex = np.argmin(abs(self.Z[0, :] - Z))

        # Normalise psi at this Z index
        psinorm = (self.psi()[:, Zindex] - self.psi_axis) / (
            self.psi_bndry - self.psi_axis
        )

        if recalculate_equilibrium:
            Rindex_axis = np.argmin(abs(self.R[:, 0] - self.Rmagnetic()))
        else:
            try:
                Rindex_axis = Rindex_axis = np.argmin(
                    abs(eq.R[:, 0] - self._profiles.opt[0][0])
                )
            except AttributeError as e:
                print(e)
                warnings.warn(
                    "The equilibrium object does not seem to have been updated. "
                    + "You can pass recalculate_equilibrium=True to find the magnetic axis."
                )
                raise e

        # Start from the magnetic axis
        if Rindex_axis is None:
            Rindex_axis = np.argmin(abs(self.R[:, 0] - self.Rmagnetic()))

        # Inner separatrix
        # Get the maximum index where psi > 1 in the R index range from 0 to Rindex_axis
        outside_inds = np.argwhere(psinorm[:Rindex_axis] > 1.0)

        if outside_inds.size == 0:
            R_sep_in = self.Rmin
        else:
            Rindex_inner = np.amax(outside_inds)

            # Separatrix should now be between Rindex_inner and Rindex_inner+1
            # Linear interpolation
            R_sep_in = (
                self.R[Rindex_inner, Zindex]
                * (1.0 - psinorm[Rindex_inner + 1])
                + self.R[Rindex_inner + 1, Zindex]
                * (psinorm[Rindex_inner] - 1.0)
            ) / (psinorm[Rindex_inner] - psinorm[Rindex_inner + 1])

        # Outer separatrix
        # Find the minimum index where psi > 1
        outside_inds = np.argwhere(psinorm[Rindex_axis:] > 1.0)

        if outside_inds.size == 0:
            R_sep_out = self.Rmax
        else:
            Rindex_outer = np.amin(outside_inds) + Rindex_axis

            # Separatrix should now be between Rindex_outer-1 and Rindex_outer
            R_sep_out = (
                self.R[Rindex_outer, Zindex]
                * (1.0 - psinorm[Rindex_outer - 1])
                + self.R[Rindex_outer - 1, Zindex]
                * (psinorm[Rindex_outer] - 1.0)
            ) / (psinorm[Rindex_outer] - psinorm[Rindex_outer - 1])

        return R_sep_in, R_sep_out

    def intersectsWall(self):
        """Assess whether or not the core plasma touches the vessel
        walls. Returns True if it does intersect.
        """
        separatrix = self.separatrix()  # Array [:,2]
        wall = self.tokamak.wall  # Wall object with R and Z members (lists)

        return polygons.intersect(
            separatrix[:, 0], separatrix[:, 1], wall.R, wall.Z
        )

    def magneticAxis(self):
        """Returns the location of the magnetic axis as a list [R,Z,psi]"""
        opt, xpt = critical.find_critical(self.R, self.Z, self.psi())
        return opt[0]

    def Rmagnetic(self):
        """The major radius R of magnetic major radius"""
        return self.magneticAxis()[0]

    def geometricAxis(self, npoints=300):
        """Locates geometric axis, returning [R,Z]. Calculated as the centre
        of a large number of points on the separatrix equally
        distributed in angle from the magnetic axis.
        """
        separatrix = self.separatrix(ntheta=npoints)  # Array [:,2]
        return np.mean(separatrix, axis=0)

    def Rgeometric(self, npoints=300):
        """Locates major radius R of the geometric major radius. Calculated
        as the centre of a large number of points on the separatrix
        equally distributed in angle from the magnetic axis.
        """
        return self.geometricAxis(npoints=npoints)[0]

    def minorRadius(self, npoints=300):
        """Calculates minor radius of plasma as the average distance from the
        geometric major radius to a number of points along the
        separatrix
        """
        separatrix = self.separatrix(ntheta=npoints)  # [:,2]
        axis = np.mean(separatrix, axis=0)  # Geometric axis [R,Z]

        # Calculate average distance from the geometric axis
        return np.mean(
            np.sqrt(
                (separatrix[:, 0] - axis[0]) ** 2
                + (separatrix[:, 1] - axis[1]) ** 2  # dR^2
            )
        )  # dZ^2

    def geometricElongation(self, npoints=300):
        """Calculates the elongation of a plasma using the range of R and Z of
        the separatrix

        """
        separatrix = self.separatrix(ntheta=npoints)  # [:,2]
        # Range in Z / range in R
        return (max(separatrix[:, 1]) - min(separatrix[:, 1])) / (
            max(separatrix[:, 0]) - min(separatrix[:, 0])
        )

    def aspectRatio(self, npoints=300):
        """Calculates the plasma aspect ratio"""
        return self.Rgeometric(npoints=npoints) / self.minorRadius(
            npoints=npoints
        )

    def effectiveElongation(self, npoints=300):
        """Calculates plasma effective elongation using the plasma volume"""
        return self.plasmaVolume() / (
            2.0
            * np.pi
            * self.Rgeometric(npoints=npoints)
            * np.pi
            * self.minorRadius(npoints=npoints) ** 2
        )

    def internalInductance1(self, npoints=300):
        """Calculates li1 plasma internal inductance"""

        R = self.R
        Z = self.Z
        # Produce array of Bpol^2 in (R,Z)
        B_polvals_2 = self.Bz(R, Z) ** 2 + self.Br(R, Z) ** 2

        dR = R[1, 0] - R[0, 0]
        dZ = Z[0, 1] - Z[0, 0]
        dV = 2.0 * np.pi * R * dR * dZ

        try:
            dV *= self._profiles.limiter_core_mask
        except AttributeError as e:
            print(e)
            warnings.warn(
                "The core mask is not in place. You need to solve for the equilibrium first!"
            )
            raise e

        Ip = self.plasmaCurrent()
        R_geo = self.Rgeometric(npoints=npoints)
        elon = self.geometricElongation(npoints=npoints)
        effective_elon = self.effectiveElongation(npoints=npoints)

        integral = romb(romb(B_polvals_2 * dV))
        return ((2 * integral) / ((mu0 * Ip) ** 2 * R_geo)) * (
            (1 + elon * elon) / (2.0 * effective_elon)
        )

    def internalInductance2(self):
        """Calculates li2 plasma internal inductance"""

        R = self.R
        Z = self.Z
        # Produce array of Bpol in (R,Z)
        B_polvals_2 = self.Br(R, Z) ** 2 + self.Bz(R, Z) ** 2

        dR = R[1, 0] - R[0, 0]
        dZ = Z[0, 1] - Z[0, 0]
        dV = 2.0 * np.pi * R * dR * dZ

        try:
            dV *= self._profiles.limiter_core_mask
        except AttributeError as e:
            print(e)
            warnings.warn(
                "The core mask is not in place. You need to solve for the equilibrium first!"
            )
            raise e

        Ip = self.plasmaCurrent()
        R_mag = self.Rmagnetic()

        integral = romb(romb(B_polvals_2 * dV))
        return 2 * integral / ((mu0 * Ip) ** 2 * R_mag)

    def internalInductance3(self, npoints=300):
        """Calculates li3 plasma internal inductance"""

        R = self.R
        Z = self.Z
        # Produce array of Bpol in (R,Z)
        B_polvals_2 = self.Br(R, Z) ** 2 + self.Bz(R, Z) ** 2

        dR = R[1, 0] - R[0, 0]
        dZ = Z[0, 1] - Z[0, 0]
        dV = 2.0 * np.pi * R * dR * dZ

        try:
            dV *= self._profiles.limiter_core_mask
        except AttributeError as e:
            print(e)
            warnings.warn(
                "The core mask is not in place. You need to solve for the equilibrium first!"
            )
            raise e

        Ip = self.plasmaCurrent()
        R_geo = self.Rgeometric(npoints=npoints)

        integral = romb(romb(B_polvals_2 * dV))
        return 2 * integral / ((mu0 * Ip) ** 2 * R_geo)

    def poloidalBeta2(self):
        """Calculate plasma poloidal beta by integrating the thermal pressure
        and poloidal magnetic field pressure over the plasma volume.

        """

        R = self.R
        Z = self.Z

        # Produce array of Bpol in (R,Z)
        B_polvals_2 = self.Br(R, Z) ** 2 + self.Bz(R, Z) ** 2

        dR = R[1, 0] - R[0, 0]
        dZ = Z[0, 1] - Z[0, 0]
        dV = 2.0 * np.pi * R * dR * dZ

        # Normalised psi
        psi_norm = (self.psi() - self.psi_axis) / (
            self.psi_bndry - self.psi_axis
        )

        # Plasma pressure
        pressure = self.pressure(psi_norm)

        try:
            dV *= self._profiles.limiter_core_mask
        except AttributeError as e:
            print(e)
            warnings.warn(
                "The core mask is not in place. You need to solve for the equilibrium first!"
            )
            raise e

        pressure_integral = romb(romb(pressure * dV))
        field_integral_pol = romb(romb(B_polvals_2 * dV))
        return 2 * mu0 * pressure_integral / field_integral_pol

    def toroidalBeta(self):
        """Calculate plasma toroidal beta by integrating the thermal pressure
        and toroidal magnetic field pressure over the plasma volume.

        """

        R = self.R
        Z = self.Z

        # Produce array of Btor in (R,Z)
        B_torvals_2 = self.Btor(R, Z) ** 2

        dR = R[1, 0] - R[0, 0]
        dZ = Z[0, 1] - Z[0, 0]
        dV = 2.0 * np.pi * R * dR * dZ

        # Normalised psi
        psi_norm = (self.psi() - self.psi_axis) / (
            self.psi_bndry - self.psi_axis
        )

        # Plasma pressure
        pressure = self.pressure(psi_norm)

        try:
            dV *= self._profiles.limiter_core_mask
        except AttributeError as e:
            print(e)
            warnings.warn(
                "The core mask is not in place. You need to solve for the equilibrium first!"
            )
            raise e

        pressure_integral = romb(romb(pressure * dV))

        # Correct for errors in Btor and core masking
        np.nan_to_num(B_torvals_2, copy=False)

        field_integral_tor = romb(romb(B_torvals_2 * dV))
        return 2 * mu0 * pressure_integral / field_integral_tor

    def totalBeta(self):
        """Calculate plasma total beta"""
        return 1.0 / (
            (1.0 / self.poloidalBeta2()) + (1.0 / self.toroidalBeta())
        )

    def strikepoints(self):
        """
            This function can be used to find the strikepoints of an equilibrium
            using the:

            - R and Z grids (2D)
            - psi_total (2D) (i.e. the poloidal flux map)
            - psi_boundary (single value)
            - wall coordinates (N x 2)

        It should find the intersection between any points on the psi_boundary contour
        of psi_total and the wall of the tokamak.
        """

        # find contour object for psi_boundary
        if self._profiles.flag_limiter:
            cs = plt.contour(
                self.R, self.Z, self.psi(), levels=[self._profiles.psi_bndry]
            )
        else:
            cs = plt.contour(
                self.R, self.Z, self.psi(), levels=[self._profiles.xpt[0][2]]
            )
        plt.close()  # this isn't the most elegant but we don't need the plot itself

        # for each item in the contour object there's a list of points in (r,z) (i.e. a line)
        psi_boundary_lines = []
        for i, item in enumerate(cs.allsegs[0]):
            psi_boundary_lines.append(item)

        # use the shapely package to find where each psi_boundary_line intersects the wall (or not)
        strikes = []
        wall = np.array([self.tokamak.wall.R, self.tokamak.wall.Z]).T
        curve1 = sh.LineString(wall)
        for j, line in enumerate(psi_boundary_lines):
            curve2 = sh.LineString(line)

            # find the intersection points
            intersection = curve2.intersection(curve1)

            # extract intersection points
            if intersection.geom_type == "Point":
                strikes.append(np.squeeze(np.array(intersection.xy).T))
            elif intersection.geom_type == "MultiPoint":
                strikes.append(
                    np.squeeze(
                        np.array([geom.xy for geom in intersection.geoms])
                    )
                )

        # check how many strikepoints
        if len(strikes) == 0:
            out = None
        else:
            out = np.concatenate(strikes, axis=0)

        return out


def refine(eq, nx=None, ny=None):
    """
    Double grid resolution, returning a new equilibrium


    """
    # Interpolate the plasma psi
    # plasma_psi = multigrid.interpolate(eq.plasma_psi)
    # nx, ny = plasma_psi.shape

    # By default double the number of intervals
    if not nx:
        nx = 2 * (eq.R.shape[0] - 1) + 1
    if not ny:
        ny = 2 * (eq.R.shape[1] - 1) + 1

    result = Equilibrium(
        tokamak=eq.tokamak,
        Rmin=eq.Rmin,
        Rmax=eq.Rmax,
        Zmin=eq.Zmin,
        Zmax=eq.Zmax,
        boundary=eq._applyBoundary,
        order=eq.order,
        nx=nx,
        ny=ny,
    )

    plasma_psi = eq.psi_func(result.R, result.Z, grid=False)

    result._updatePlasmaPsi(plasma_psi)

    if hasattr(eq, "_profiles"):
        result._profiles = eq._profiles

    if hasattr(eq, "control"):
        result.control = eq.control

    return result


def coarsen(eq):
    """
    Reduce grid resolution, returning a new equilibrium
    """
    plasma_psi = multigrid.restrict(eq.plasma_psi)
    nx, ny = plasma_psi.shape

    result = Equilibrium(
        tokamak=eq.tokamak,
        Rmin=eq.Rmin,
        Rmax=eq.Rmax,
        Zmin=eq.Zmin,
        Zmax=eq.Zmax,
        nx=nx,
        ny=ny,
    )

    result._updatePlasmaPsi(plasma_psi)

    if hasattr(eq, "_profiles"):
        result._profiles = eq._profiles

    if hasattr(eq, "control"):
        result.control = eq.control

    return result


def newDomain(
    eq, Rmin=None, Rmax=None, Zmin=None, Zmax=None, nx=None, ny=None
):
    """Creates a new Equilibrium, solving in a different domain.
    The domain size (Rmin, Rmax, Zmin, Zmax) and resolution (nx,ny)
    are taken from the input equilibrium eq if not specified.
    """
    if Rmin is None:
        Rmin = eq.Rmin
    if Rmax is None:
        Rmax = eq.Rmax
    if Zmin is None:
        Zmin = eq.Zmin
    if Zmax is None:
        Zmax = eq.Zmax
    if nx is None:
        nx = eq.R.shape[0]
    if ny is None:
        ny = eq.R.shape[0]

    # Create a new equilibrium with the new domain
    result = Equilibrium(
        tokamak=eq.tokamak,
        Rmin=Rmin,
        Rmax=Rmax,
        Zmin=Zmin,
        Zmax=Zmax,
        nx=nx,
        ny=ny,
    )

    # Calculate the current on the old grid
    profiles = eq._profiles
    Jtor = profiles.Jtor(eq.R, eq.Z, eq.psi())

    # Interpolate Jtor onto new grid
    Jtor_func = interpolate.RectBivariateSpline(eq.R[:, 0], eq.Z[0, :], Jtor)
    Jtor_new = Jtor_func(result.R, result.Z, grid=False)

    result._applyBoundary(result, Jtor_new, result.plasma_psi)

    # Right hand side of G-S equation
    rhs = -mu0 * result.R * Jtor_new

    # Copy boundary conditions
    rhs[0, :] = result.plasma_psi[0, :]
    rhs[:, 0] = result.plasma_psi[:, 0]
    rhs[-1, :] = result.plasma_psi[-1, :]
    rhs[:, -1] = result.plasma_psi[:, -1]

    # Call elliptic solver
    plasma_psi = result._solver(result.plasma_psi, rhs)

    result._updatePlasmaPsi(plasma_psi)

    # Solve once more, calculating Jtor using new psi
    result.solve(profiles)

    return result


if __name__ == "__main__":

    # Test the different spline interpolation routines

    import machine
    import matplotlib.pyplot as plt
    from numpy import ravel

    tokamak = machine.TestTokamak()

    Rmin = 0.1
    Rmax = 2.0

    eq = Equilibrium(tokamak, Rmin=Rmin, Rmax=Rmax)

    import constraints

    xpoints = [(1.2, -0.8), (1.2, 0.8)]
    constraints.xpointConstrain(eq, xpoints)

    psi = eq.psi()

    tck = interpolate.bisplrep(ravel(eq.R), ravel(eq.Z), ravel(psi))
    spline = interpolate.RectBivariateSpline(eq.R[:, 0], eq.Z[0, :], psi)
    f = interpolate.interp2d(eq.R[:, 0], eq.Z[0, :], psi, kind="cubic")

    plt.plot(eq.R[:, 10], psi[:, 10], "o")

    r = linspace(Rmin, Rmax, 1000)
    z = eq.Z[0, 10]
    plt.plot(r, f(r, z), label="f")

    plt.plot(r, spline(r, z), label="spline")

    plt.plot(r, interpolate.bisplev(r, z, tck), label="bisplev")

    plt.legend()
    plt.show()
