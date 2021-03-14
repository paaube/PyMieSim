import numpy as np
from mayavi import mlab
from scipy.interpolate import griddata

from PyMieSim.Physics import Angle
import PyMieSim


def GetFieldBinding(Scatterer, Structured, R, Phi, Theta):

    kwarg = { 'Index'       : Scatterer.Index,
               'Diameter'   : Scatterer.Diameter,
               'Wavelength' : Scatterer.Source.Wavelength,
               'nMedium'    : Scatterer.nMedium,
               'Phi'        : Phi,
               'Theta'      : Theta,
               'R'          : R,
               'E0'         : Scatterer.Source.E0}


    lib = PyMieSim
    if Scatterer.Source.GLMT:
        lib = lib.GLMT
        kwarg['BSC'] = Scatterer.Source._BSC_
        kwarg['MaxOrder'] = Scatterer.Source.MaxOrder

    else:
        lib = lib.LMT

    if Scatterer.type == 'Sphere': lib = lib.Sphere

    if Scatterer.type == 'Cylinder': lib = lib.Cylinder

    if Structured:
        lib = lib.Structured
    else:
        lib = lib.Unstructured

    if Scatterer.Source.Polarization:
        return lib.Fields(**kwarg, Polarization = Scatterer.Source.Polarization.Radian )
    else:
        return lib.FieldsUnpolarized(**kwarg)






def InterpFull(Meshes, Scalar, Shape):

    Phi, Theta = np.mgrid[-np.pi/2:np.pi/2:complex(Shape[0]),
                          -np.pi:np.pi:complex(Shape[1])]

    Scalar = interp_at(Meshes.Phi.Radian,
                       Meshes.Theta.Radian,
                       Scalar.astype(np.complex).flatten(),
                       Phi.flatten(),
                       Theta.flatten(),
                       algorithm='linear',
                       extrapolate=True)

    return Scalar.reshape(Shape), Phi, Theta







def interp_at(x, y, v, xp, yp, algorithm='cubic', extrapolate=False):
    """
    Interpolate data onto the specified points.

    Parameters:

    * x, y : 1D arrays
        Arrays with the x and y coordinates of the data points.
    * v : 1D array
        Array with the scalar value assigned to the data points.
    * xp, yp : 1D arrays
        Points where the data values will be interpolated
    * algorithm : string
        Interpolation algorithm. Either ``'cubic'``, ``'nearest'``,
        ``'linear'`` (see scipy.interpolate.griddata)
    * extrapolate : True or False
        If True, will extrapolate values outside of the convex hull of the data
        points.

    Returns:

    * v : 1D array
        1D array with the interpolated v values.

    """
    if algorithm not in ['cubic', 'linear', 'nearest']:
        raise ValueError("Invalid interpolation algorithm: " + str(algorithm))

    grid = griddata((x, y), v, (xp, yp), method=algorithm).ravel()

    if extrapolate and algorithm != 'nearest' and np.any(np.isnan(grid)):
        grid = extrapolate_nans(xp, yp, grid)
    return grid


def extrapolate_nans(x, y, v):
    """
    Extrapolate the NaNs or masked values in a grid INPLACE using nearest
    value.

    .. warning:: Replaces the NaN or masked values of the original array!

    Parameters:

    * x, y : 1D arrays
        Arrays with the x and y coordinates of the data points.
    * v : 1D array
        Array with the scalar value assigned to the data points.

    Returns:

    * v : 1D array
        The array with NaNs or masked values extrapolated.

    """
    if np.ma.is_masked(v):
        nans = v.mask
    else:
        nans = np.isnan(v)
    notnans = np.logical_not(nans)
    v[nans] = griddata((x[notnans], y[notnans]),
                        v[notnans],
                        (x[nans], y[nans]),
                        method='nearest').ravel()
    return v





def UnitSphere(Num, Radius=1.):
    pi = np.pi
    phi, theta = np.mgrid[-pi/2:pi/2:complex(Num), -pi:pi:complex(Num)]
    x, y, z = sp2cart(phi*0+Radius, phi, theta)

    return x, y, z


def PlotUnstructured(Scalar, Mesh, Name=''):
    x, y, z = sp2cart(Mesh.Phi.Radian.flatten()*0+1,
                      Mesh.Phi.Radian.flatten(),
                      Mesh.Theta.Radian.flatten())

    offset = 3
    X = np.linspace(-1,1,10)*1.3
    Y = np.linspace(-1,1,10)*1.3
    Z = np.linspace(-1,1,10)*2

    zeros = np.zeros_like(X)

    fig = mlab.figure(size=(600,300))

    mlab.plot3d(X, zeros, zeros, line_width=1e-12)
    mlab.plot3d(zeros, Y, zeros, line_width=1e-12)
    mlab.plot3d(zeros, zeros, Z, line_width=1e-12)

    mlab.plot3d(X+offset, zeros, zeros, line_width=1e-12)
    mlab.plot3d(zeros+offset, Y, zeros, line_width=1e-12)
    mlab.plot3d(zeros+offset, zeros, Z, line_width=1e-12)

    mlab.text(0, 0, u'Z', z=2, width=0.01)
    mlab.text(0, 1.3, u'Y', z=0, width=0.01)
    mlab.text(1.3, 0, u'X', z=0, width=0.01)

    mlab.text(0+offset, 0, u'Z', z=2, width=0.01)
    mlab.text(0+offset, 1.3, u'Y', z=0, width=0.01)
    mlab.text(1.3+offset, 0, u'X', z=0, width=0.01)

    mlab.text(offset, 0, u'Imaginary', z=-2., width=0.15)
    mlab.text(0, 0, u'Real', z=-2, width=0.07)

    mlab.text(offset/2, 0, Name, z=2, width=0.2)

    xp, yp, zp = UnitSphere(Num=50, Radius=1.)

    mlab.mesh(xp, yp, zp, colormap='gray', opacity=0.5)

    mlab.mesh(xp+offset, yp, zp, colormap='gray', opacity=0.5)

    im0 = mlab.points3d(x, y, z, Scalar.real, mode='sphere', scale_mode='none', colormap='inferno')

    im1 = mlab.points3d(x+offset, y, z, Scalar.imag, mode='sphere', scale_mode='none', colormap='inferno')

    mlab.colorbar(object = im0, label_fmt="%.0e", nb_labels=5, title='Real part', orientation='horizontal' )

    mlab.colorbar(object = im1, label_fmt="%.0e", nb_labels=5, title='Imaginary part', orientation='vertical' )

    mlab.show()







def PlotStructuredAbs(Scalar, Phi, Theta, Name=''):

        x, y, z = sp2cart(Scalar, Phi, Theta)

        X = np.linspace(np.min(x),np.max(x),10)*1.3
        Y = np.linspace(np.min(y),np.max(y),10)*1.3
        Z = np.linspace(np.min(z),np.max(z),10)*1.3

        radius = np.abs( min(np.min(x), np.min(y), np.min(z))/100 )

        zeros = np.zeros_like(X)

        mlab.plot3d(X, zeros, zeros, line_width=1e-12, tube_radius=radius)
        mlab.plot3d(zeros, Y, zeros, line_width=1e-12, tube_radius=radius)
        mlab.plot3d(zeros, zeros, Z, line_width=1e-12, tube_radius=radius)

        mlab.text(0, 0, u'Z', z=Z[-1], width=0.01)
        mlab.text(0, Y[-1], u'Y', z=0, width=0.01)
        mlab.text(X[-1], 0, u'X', z=0, width=0.01)

        mlab.text(0, 0, Name, z=Z[-1]*1.15, width=0.5)

        mlab.mesh(x, y, z, colormap='viridis')

        mlab.show()


def PlotStructuredAmplitude(Scalar, Phi, Theta, Name=''):

    x, y, z = sp2cart(Phi*0+1, Phi, Theta)

    offset = 3
    X = np.linspace(-1,1,10)*1.3
    Y = np.linspace(-1,1,10)*1.3
    Z = np.linspace(-1,1,10)*2

    zeros = np.zeros_like(X)

    fig = mlab.figure(size=(600,300))

    mlab.plot3d(X, zeros, zeros, line_width=1e-12)
    mlab.plot3d(zeros, Y, zeros, line_width=1e-12)
    mlab.plot3d(zeros, zeros, Z, line_width=1e-12)

    mlab.plot3d(X+offset, zeros, zeros, line_width=1e-12)
    mlab.plot3d(zeros+offset, Y, zeros, line_width=1e-12)
    mlab.plot3d(zeros+offset, zeros, Z, line_width=1e-12)

    mlab.text(0, 0, u'Z', z=2, width=0.01)
    mlab.text(0, 1.3, u'Y', z=0, width=0.01)
    mlab.text(1.3, 0, u'X', z=0, width=0.01)

    mlab.text(0+offset, 0, u'Z', z=2, width=0.01)
    mlab.text(0+offset, 1.3, u'Y', z=0, width=0.01)
    mlab.text(1.3+offset, 0, u'X', z=0, width=0.01)

    mlab.text(offset, 0, u'Imaginary', z=-2., width=0.15)
    mlab.text(0, 0, u'Real', z=-2, width=0.07)

    mlab.text(offset/2, 0, Name, z=2, width=0.2)

    xp, yp, zp = UnitSphere(Num=50, Radius=1.)

    mlab.mesh(xp, yp, zp, colormap='gray', opacity=0.5)

    mlab.mesh(xp+offset, yp, zp, colormap='gray', opacity=0.5)

    im0 = mlab.points3d(x, y, z, Scalar.real, mode='sphere', scale_mode='none', colormap='inferno')

    im1 = mlab.points3d(x+offset, y, z, Scalar.imag, mode='sphere', scale_mode='none', colormap='inferno')

    mlab.colorbar(object = im0, label_fmt="%.0e", nb_labels=5, title='Real part', orientation='horizontal' )

    mlab.colorbar(object = im1, label_fmt="%.0e", nb_labels=5, title='Imaginary part', orientation='vertical' )

    mlab.show()


""" Ref: https://optiwave.com/optifdtd-manuals/fdtd-far-field-transform/"""




def Angle2Direct(AngleVec: np.ndarray, k: float,) -> np.ndarray:

    RadSpace = np.deg2rad(AngleVec)

    FourierSpace = np.sin(RadSpace) * k / (2 * np.pi)

    fourier_unit = (FourierSpace[1] - FourierSpace[0]).__abs__()

    DirectSpace = np.fft.fftshift( np.fft.fftfreq( AngleVec.shape[0], d = fourier_unit ) )

    return DirectSpace



def Direct2Angle(DirectVec: np.ndarray, k: float) -> np.ndarray:

    direct_unit = (DirectVec[1] - DirectVec[0]).__abs__()

    FourierSpace = np.fft.fftshift( np.fft.fftfreq( DirectVec.shape[0], d = direct_unit ) )

    AngleVec = np.arcsin(2 * np.pi * FourierSpace / k) # conversion spatial frequency to angular space

    if np.isnan(AngleVec).any():
        raise Exception("Magnification too large.")

    return AngleVec * 180 / np.pi



def NA2Angle(NA: float) -> np.ndarray:

    return Angle( np.arcsin(NA), unit='Radian')



def Direct2spherical(X, Y, MaxAngle):
    Z = 50 / np.tan(MaxAngle)

    _, Phi, Theta = cart2sp(X, Y, X*0+Z)

    return Phi, Theta

def Direct2Angle(X, Y, MaxAngle):
    MaxZ = np.max(X) / np.cos(MaxAngle)



def AngleUnit2DirectUnit(Angle, k):
    FourierSpace = np.sin(Angle) * k / (2 * np.pi)

    fourier_unit = (FourierSpace[1] - FourierSpace[0]).__abs__()

    DirectSpace = np.fft.fftshift( np.fft.fftfreq( Angle.shape[0], d = fourier_unit ) )

    return DirectSpace




def cart2sp(x, y, z):
    """Converts data from cartesian coordinates into spherical.

    Args:
        x (scalar or array_like): X-component of data.
        y (scalar or array_like): Y-component of data.
        z (scalar or array_like): Z-component of data.

    Returns:
        Tuple (r, theta, phi) of data in spherical coordinates.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)
    scalar_input = False
    if x.ndim == 0 and y.ndim == 0 and z.ndim == 0:
        x = x[None]
        y = y[None]
        z = z[None]
        scalar_input = True
    r = np.sqrt(x**2+y**2+z**2)
    theta = np.arcsin(z/r)
    phi = np.arctan2(y, x)
    if scalar_input:
        return (r.squeeze(), theta.squeeze(), phi.squeeze())
    return (r, theta, phi)

def sp2cart(r, theta, phi):
    """Converts data in spherical coordinates into cartesian.

    Args:
        r (scalar or array_like): R-component of data.
        theta (scalar or array_like): Theta-component of data.
        phi (scalar or array_like): Phi-component of data.

    Returns:
        Tuple (x, y, z) of data in cartesian coordinates.
    """
    r = np.asarray(r)
    theta = np.asarray(theta)
    phi = np.asarray(phi)
    scalar_input = False
    if r.ndim == 0 and theta.ndim == 0 and phi.ndim == 0:
        r = r[None]
        theta = theta[None]
        phi = phi[None]
        scalar_input = True
    x = r*np.cos(theta)*np.cos(phi)
    y = r*np.cos(theta)*np.sin(phi)
    z = r*np.sin(theta)
    if scalar_input:
        return (x.squeeze(), y.squeeze(), z.squeeze())
    return (x, y, z)


def mx_rot_x(gamma):
    """Returns rotational matrix for right-handed rotation
    around X axis.

    Args:
        gamma (scalar): Rotation angle around X in radians.

    Returns:
        Numpy rotational matrix.
    """
    return np.matrix([
        [1, 0, 0],
        [0, np.cos(gamma), -np.sin(gamma)],
        [0, np.sin(gamma), np.cos(gamma)]
    ])

def mx_rot_y(theta):
    """Returns rotational matrix for right-handed rotation
    around Y axis.

    Args:
        theta (scalar): Rotation angle around Y in radians.

    Returns:
        Numpy rotational matrix.
    """
    return np.matrix([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])



def mx_rot_z(phi):
    """Returns rotational matrix for right-handed rotation
    around Z axis.

    Args:
        phi (scalar): Rotation angle around Z in radians.

    Returns:
        Numpy rotational matrix.
    """
    return np.matrix([
        [np.cos(phi), -np.sin(phi), 0],
        [np.sin(phi), np.cos(phi), 0],
        [0, 0, 1]
    ])


def mx_apply(T, x, y, z):
    """Applies rotation to data using rotational matrix.

    Args:
        T (numpy.matrix): Rotational matrix.
        x (scalar or array_like): X-component of data.
        y (scalar or array_like): Y-component of data.
        z (scalar or array_like): Z-component of data.

    Returns:
        Tuple (x, y, z) of data in cartesian coordinates.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)
    scalar_input = False
    if x.ndim == 0 and y.ndim == 0 and z.ndim == 0:
        x = x[None]
        y = y[None]
        z = z[None]
        scalar_input = True
    x_ = T[0, 0]*x+T[0, 1]*y+T[0, 2]*z
    y_ = T[1, 0]*x+T[1, 1]*y+T[1, 2]*z
    z_ = T[2, 0]*x+T[2, 1]*y+T[2, 2]*z
    if scalar_input:
        return (x_.squeeze(), y_.squeeze(), z_.squeeze())
    return (x_, y_, z_)


# -
