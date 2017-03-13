from collections import OrderedDict

class Var:
    def __init__(self, name, dims, units, long_description, dtype=None, output=False,
                 time_dependent = True, scale=1., average=False, extra_attributes=None):
        self.name = name
        self.dims = dims
        self.units = units
        self.long_description = long_description
        self.dtype = dtype if dtype else "float"
        self.output = output
        self.time_dependent = time_dependent
        self.scale = scale
        self.average = average
        self.extra_attributes = extra_attributes or {} #: Additional attributes to be written in netCDF output


# fill value for netCDF output (invalid data is replaced by this value)
FILL_VALUE = 1e-33

#
XT = ("xt",)
XU = ("xu",)
YT = ("yt",)
YU = ("yu",)
ZT = ("zt",)
ZW = ("zw",)
T_HOR = ("xt","yt")
U_HOR = ("xu","yt")
V_HOR = ("xt","yu")
ZETA_HOR = ("xu","yu")
T_GRID = ("xt","yt","zt")
U_GRID = ("xu","yt","zt")
V_GRID = ("xt","yu","zt")
W_GRID = ("xt","yt","zw")
ZETA_GRID = ("xu","yu","zt")
TIMESTEPS = ("timesteps",)
TENSOR_COMP = ("tensor1", "tensor2")
NP = ("np",)
#
OUTPUT_DIMENSIONS = XT + XU + YT + YU + ZT + ZW


def get_dimensions(pyom, grid, include_ghosts=True):
    dimensions = {
        "xt": pyom.nx,
        "xu": pyom.nx,
        "yt": pyom.ny,
        "yu": pyom.ny,
        "zt": pyom.nz,
        "zw": pyom.nz,
        "timesteps": 3,
        "tensor1": 2,
        "tensor2": 2,
        "np": pyom.np
    }
    if include_ghosts:
        for d in ("xt","xu","yt","yu"):
            dimensions[d] += 4
    return tuple(dimensions[grid_dim] for grid_dim in grid)


def remove_ghosts(array, dims):
    ghost_mask = tuple(slice(2,-2) if dim in ("xt", "yt", "xu", "yu") else slice(None) for dim in dims)
    return array[ghost_mask]


def get_grid_mask(pyom, grid):
    masks = {
        T_HOR: pyom.maskT[:,:,-1],
        U_HOR: pyom.maskU[:,:,-1],
        V_HOR: pyom.maskV[:,:,-1],
        ZETA_HOR: pyom.maskZ[:,:,-1],
        T_GRID: pyom.maskT,
        U_GRID: pyom.maskU,
        V_GRID: pyom.maskV,
        W_GRID: pyom.maskW,
        ZETA_GRID: pyom.maskZ
    }
    if len(grid) > 2:
        if grid[:3] in masks.keys():
            return masks[grid[:3]]
    if len(grid) > 1:
        if grid[:2] in masks.keys():
            return masks[grid[:2]]
    return None


MAIN_VARIABLES = OrderedDict([
    ("zt", Var(
        "Vertical coordinate (T)", ZT, "m", "Vertical coordinate",
        output=True, time_dependent=False, extra_attributes={"positive": "up"}
    )),
    ("zw", Var(
        "Vertical coordinate (W)", ZW, "m", "Vertical coordinate", output=True,
        time_dependent=False, extra_attributes={"positive": "up"}
    )),
    ("dzt", Var(
        "Vertical spacing (T)", ZT, "m", "Vertical spacing", output=True, time_dependent=False
    )),
    ("dzw", Var(
        "Vertical spacing (W)", ZW, "m", "Vertical spacing", output=True, time_dependent=False
    )),
    ("cost", Var(
        "Metric factor (T)", YT, "1", "Metric factor for spherical coordinates",
        time_dependent=False
    )),
    ("cosu", Var(
        "Metric factor (U)", YU, "1", "Metric factor for spherical coordinates",
        time_dependent=False
    )),
    ("tantr", Var(
        "Metric factor", YT, "1", "Metric factor for spherical coordinates",
        time_dependent=False
    )),
    ("coriolis_t", Var(
        "Coriolis frequency", T_HOR, "1/s",
        "Coriolis frequency at T grid point", time_dependent=False
    )),
    ("coriolis_h", Var(
        "Horizontal Coriolis frequency", T_HOR, "1/s",
        "Horizontal Coriolis frequency at T grid point", time_dependent=False
    )),

    ("kbot", Var(
        "Index of deepest cell", T_HOR, "",
        "Index of the deepest grid cell (counting from 1, 0 means all land)",
        dtype="int", time_dependent=False
    )),
    ("ht", Var(
        "Total depth (T)", T_HOR, "m", "Total depth of the water column", output=True,
        time_dependent=False
    )),
    ("hu", Var(
        "Total depth (U)", U_HOR, "m", "Total depth of the water column", output=True,
        time_dependent=False
    )),
    ("hv", Var(
        "Total depth (V)", V_HOR, "m", "Total depth of the water column", output=True,
        time_dependent=False
    )),
    ("hur", Var(
        "Total depth (U), masked", U_HOR, "m",
        "Total depth of the water column (masked)", time_dependent=False
    )),
    ("hvr", Var(
        "Total depth (V), masked", V_HOR, "m",
        "Total depth of the water column (masked)", time_dependent=False
    )),
    ("beta", Var(
        "Change of Coriolis freq.", T_HOR, "1/(ms)",
        "Change of Coriolis frequency with latitude", output=True, time_dependent=False
    )),
    ("area_t", Var(
        "Area of T-box", T_HOR, "m^2", "Area of T-box", output=True, time_dependent=False
    )),
    ("area_u", Var(
        "Area of U-box", U_HOR, "m^2", "Area of U-box", output=True, time_dependent=False
    )),
    ("area_v", Var(
        "Area of V-box", V_HOR, "m^2", "Area of V-box", output=True, time_dependent=False
    )),

    ("maskT", Var(
        "Mask for tracer points", T_GRID, "",
        "Mask in physical space for tracer points", dtype="int", time_dependent=False
    )),
    ("maskU", Var(
        "Mask for U points", U_GRID, "",
        "Mask in physical space for U points", dtype="int", time_dependent=False
    )),
    ("maskV", Var(
        "Mask for V points", V_GRID, "",
        "Mask in physical space for V points", dtype="int", time_dependent=False
    )),
    ("maskW", Var(
        "Mask for W points", W_GRID, "",
        "Mask in physical space for W points", dtype="int", time_dependent=False
    )),
    ("maskZ", Var(
        "Mask for Zeta points", ZETA_GRID, "",
        "Mask in physical space for Zeta points", dtype="int", time_dependent=False
    )),

    ("rho", Var(
        "Density", T_GRID + TIMESTEPS, "kg/m^3", "Potential density", output=True
    )),
    ("int_drhodT", Var(
        "Der. of dyn. enthalpy by temperature", T_GRID + TIMESTEPS, "?",
        "Partial derivative of dynamic enthalpy by temperature", output=True
    )),
    ("int_drhodS", Var(
        "Der. of dyn. enthalpy by salinity", T_GRID + TIMESTEPS, "?",
        "Partial derivative of dynamic enthalpy by salinity", output=True
    )),
    ("Nsqr", Var(
        "Square of stability frequency", W_GRID + TIMESTEPS, "1/s^2",
        "Square of stability frequency", output=True
    )),
    ("Hd", Var(
        "Dynamic enthalpy", T_GRID + TIMESTEPS, "m^2/s^2", "Dynamic enthalpy", output=True
    )),
    ("dHd", Var(
        "Change of dyn. enth. by adv.", T_GRID + TIMESTEPS, "m^2/s^3",
        "Change of dynamic enthalpy due to advection"
    )),

    ("temp", Var(
        "Temperature", T_GRID + TIMESTEPS, "deg C",
        "Conservative temperature", output=True
    )),
    ("dtemp", Var(
        "Temperature tendency", T_GRID + TIMESTEPS, "deg C/s",
        "Conservative temperature tendency",
    )),
    ("salt", Var(
        "Salinity", T_GRID + TIMESTEPS, "g/kg", "Salinity", output=True
    )),
    ("dsalt", Var(
        "Salinity tendency", T_GRID + TIMESTEPS, "g/(kg s)",
        "Salinity tendency",
    )),
    ("dtemp_vmix", Var(
        "Change of temp. by vertical mixing", T_GRID, "deg C/s",
        "Change of temperature due to vertical mixing",
    )),
    ("dtemp_hmix", Var(
        "Change of temp. by horizontal mixing", T_GRID, "deg C/s",
        "Change of temperature due to horizontal mixing",
    )),
    ("dsalt_vmix", Var(
        "Change of sal. by vertical mixing", T_GRID, "deg C/s",
        "Change of salinity due to vertical mixing",
    )),
    ("dsalt_hmix", Var(
        "Change of sal. by horizontal mixing", T_GRID, "deg C/s",
        "Change of salinity due to horizontal mixing",
    )),
    ("dtemp_iso", Var(
        "Change of temp. by isop. mixing", T_GRID, "deg C/s",
        "Change of temperature due to isopycnal mixing plus skew mixing",
    )),
    ("dsalt_iso", Var(
        "Change of sal. by isop. mixing", T_GRID, "deg C/s",
        "Change of salinity due to isopycnal mixing plus skew mixing",

    )),
    ("forc_temp_surface", Var(
        "Surface temperature flux", T_HOR, "m K/s", "Surface temperature flux",
        output=True
    )),
    ("forc_salt_surface", Var(
        "Surface salinity flux", T_HOR, "m g/s kg", "Surface salinity flux",
        output=True
    )),

    ("flux_east", Var(
        "Multi-purpose flux", U_GRID, "?", "Multi-purpose flux"
    )),
    ("flux_north", Var(
        "Multi-purpose flux", V_GRID, "?", "Multi-purpose flux"
    )),
    ("flux_top", Var(
        "Multi-purpose flux", W_GRID, "?", "Multi-purpose flux"
    )),

    ("u", Var(
        "Zonal velocity", U_GRID + TIMESTEPS, "m/s", "Zonal velocity", output=True
    )),
    ("v", Var(
        "Meridional velocity", V_GRID + TIMESTEPS, "m/s", "Meridional velocity", output=True
    )),
    ("w", Var(
        "Vertical velocity", W_GRID + TIMESTEPS, "m/s", "Vertical velocity", output=True
    )),
    ("du", Var(
        "Zonal velocity tendency", U_GRID + TIMESTEPS, "m/s",
        "Zonal velocity tendency"
    )),
    ("dv", Var(
        "Meridional velocity tendency", V_GRID + TIMESTEPS, "m/s",
        "Meridional velocity tendency"
    )),
    ("du_cor", Var(
        "Change of u by Coriolis force", U_GRID, "m/s^2",
        "Change of u due to Coriolis force"
    )),
    ("dv_cor", Var(
        "Change of v by Coriolis force", V_GRID, "m/s^2",
        "Change of v due to Coriolis force"
    )),
    ("du_mix", Var(
        "Change of u by vertical mixing", U_GRID, "m/s^2",
        "Change of u due to implicit vertical mixing"
    )),
    ("dv_mix", Var(
        "Change of v by vertical mixing", V_GRID, "m/s^2",
        "Change of v due to implicit vertical mixing"
    )),
    ("du_adv", Var(
        "Change of u by advection", U_GRID, "m/s^2",
        "Change of u due to advection"
    )),
    ("dv_adv", Var(
        "Change of v by advection", V_GRID, "m/s^2",
        "Change of v due to advection"
    )),
    ("p_hydro", Var(
        "Hydrostatic pressure", T_GRID, "m^2/s^2", "Hydrostatic pressure", output=True
    )),
    ("kappaM", Var(
        "Vertical viscosity", T_GRID, "m^2/s", "Vertical viscosity", output=True
    )),
    ("kappaH", Var(
        "Vertical diffusivity", W_GRID, "m^2/s", "Vertical diffusivity", output=True
    )),
    ("surface_taux", Var(
        "Surface wind stress", U_HOR, "m^2/s^2", "Zonal surface wind stress", output=True
    )),
    ("surface_tauy", Var(
        "Surface wind stress", V_HOR, "m^2/s^2", "Meridional surface wind stress", output=True
    )),
    ("forc_rho_surface", Var(
        "Surface density flux", T_HOR, "?", "Surface potential density flux", output=True
    )),

    ("K_gm", Var(
        "Skewness diffusivity", W_GRID, "m^2/s",
        "GM diffusivity, either constant or from EKE model"
    )),
    ("K_iso", Var(
        "Isopycnal diffusivity", W_GRID, "m^2/s", "Along-isopycnal diffusivity"
    )),

    ("u_wgrid", Var(
        "U on W grid", W_GRID, "m/s", "Zonal velocity interpolated to W grid points"
    )),
    ("v_wgrid", Var(
        "V on W grid", W_GRID, "m/s", "Meridional velocity interpolated to W grid points"
    )),
    ("w_wgrid", Var(
        "W on W grid", W_GRID, "m/s", "Vertical velocity interpolated to W grid points"
    ))
])

CONDITIONAL_VARIABLES = OrderedDict([
    ("coord_degree", OrderedDict([
        ("xt", Var(
            "Zonal coordinate (T)", XT, "degrees_east",
            "Zonal (x) coordinate of T-grid point",
            output=True, time_dependent=False
        )),
        ("xu", Var(
            "Zonal coordinate (U)", XU, "degrees_east",
            "Zonal (x) coordinate of U-grid point",
            output=True, time_dependent=False
        )),
        ("yt", Var(
            "Meridional coordinate (T)", YT, "degrees_north",
            "Meridional (y) coordinate of T-grid point",
            output=True, time_dependent=False
        )),
        ("yu", Var(
            "Meridional coordinate (U)", YU, "degrees_north",
            "Meridional (y) coordinate of U-grid point",
            output=True, time_dependent=False
        )),
        ("dxt", Var(
            "Zonal T-grid spacing", XT, "degrees_east",
            "Zonal (x) spacing of T-grid point",
            output=True, time_dependent=False
        )),
        ("dxu", Var(
            "Zonal U-grid spacing", XU, "degrees_east",
            "Zonal (x) spacing of U-grid point",
            output=True, time_dependent=False
        )),
        ("dyt", Var(
            "Meridional T-grid spacing", YT, "degrees_north",
            "Meridional (y) spacing of T-grid point",
            output=True, time_dependent=False
        )),
        ("dyu", Var(
            "Meridional U-grid spacing", YU, "degrees_north",
            "Meridional (y) spacing of U-grid point",
            output=True, time_dependent=False
        ))
    ])),

    ("not coord_degree", OrderedDict([
        ("xt", Var(
            "Zonal coordinate (T)", XT, "km",
            "Zonal (x) coordinate of T-grid point",
            output=True, scale=1e-3, time_dependent=False
        )),
        ("xu", Var(
            "Zonal coordinate (U)", XU, "km",
            "Zonal (x) coordinate of U-grid point",
            output=True, scale=1e-3, time_dependent=False
        )),
        ("yt", Var(
            "Meridional coordinate (T)", YT, "km",
            "Meridional (y) coordinate of T-grid point",
            output=True, scale=1e-3, time_dependent=False
        )),
        ("yu", Var(
            "Meridional coordinate (U)", YU, "km",
            "Meridional (y) coordinate of U-grid point",
            output=True, scale=1e-3, time_dependent=False
        )),
        ("dxt", Var(
            "Zonal T-grid spacing", XT, "m",
            "Zonal (x) spacing of T-grid point",
            output=True, time_dependent=False
        )),
        ("dxu", Var(
            "Zonal U-grid spacing", XU, "m",
            "Zonal (x) spacing of U-grid point",
            output=True, time_dependent=False
        )),
        ("dyt", Var(
            "Meridional T-grid spacing", YT, "m",
            "Meridional (y) spacing of T-grid point",
            output=True, time_dependent=False
        )),
        ("dyu", Var(
            "Meridional U-grid spacing", YU, "m",
            "Meridional (y) spacing of U-grid point",
            output=True, time_dependent=False
        ))
    ])),

    ("enable_conserve_energy", OrderedDict([
    #!---------------------------------------------------------------------------------
    #!     variables related to dissipation
    #!---------------------------------------------------------------------------------
    #      real*8, allocatable, dimension(:,:,:)    :: K_diss_v          ! kinetic energy dissipation by vertical, rayleigh and bottom friction
    #      real*8, allocatable, dimension(:,:,:)    :: K_diss_h          ! kinetic energy dissipation by horizontal friction
    #      real*8, allocatable, dimension(:,:,:)    :: K_diss_gm         ! mean energy dissipation by GM (TRM formalism only)
    #      real*8, allocatable, dimension(:,:,:)    :: K_diss_bot        ! mean energy dissipation by bottom and rayleigh friction
    #      real*8, allocatable, dimension(:,:,:)    :: P_diss_v          ! potential energy dissipation by vertical diffusion
    #      real*8, allocatable, dimension(:,:,:)    :: P_diss_nonlin     ! potential energy dissipation by nonlinear equation of state
    #      real*8, allocatable, dimension(:,:,:)    :: P_diss_adv        ! potential energy dissipation by
    #      real*8, allocatable, dimension(:,:,:)    :: P_diss_comp       ! potential energy dissipation by compress.
    #      real*8, allocatable, dimension(:,:,:)    :: P_diss_hmix       ! potential energy dissipation by horizontal mixing
    #      real*8, allocatable, dimension(:,:,:)    :: P_diss_iso        ! potential energy dissipation by isopycnal mixing
    #      real*8, allocatable, dimension(:,:,:)    :: P_diss_skew       ! potential energy dissipation by GM (w/o TRM)
    #      real*8, allocatable, dimension(:,:,:)    :: P_diss_sources    ! potential energy dissipation by restoring zones, etc
        ("K_diss_v", Var(
            "Dissipation of kinetic Energy", W_GRID, "m^2/s^3",
            "Dissipation of kinetic Energy"
        )),
        ("K_diss_bot", Var(
            "Dissipation of kinetic Energy", W_GRID, "m^2/s^3",
            "Dissipation of kinetic Energy"
        )),
        ("K_diss_h", Var(
            "Dissipation of kinetic Energy", W_GRID, "m^2/s^3",
            "Dissipation of kinetic Energy"
        )),
        ("P_diss_v", Var(
            "Dissipation of potential Energy", W_GRID, "m^2/s^3",
            "Dissipation of potential Energy"
        )),
        ("P_diss_nonlin", Var(
            "Dissipation of potential Energy", W_GRID, "m^2/s^3",
            "Dissipation of potential Energy"
        )),
        ("P_diss_iso", Var(
            "Dissipation of potential Energy", W_GRID, "m^2/s^3",
            "Dissipation of potential Energy"
        )),
        ("P_diss_skew", Var(
            "Dissipation of potential Energy", W_GRID, "m^2/s^3",
            "Dissipation of potential Energy"
        )),
        ("P_diss_hmix", Var(
            "Dissipation of potential Energy", W_GRID, "m^2/s^3",
            "Dissipation of potential Energy"
        )),
        ("P_diss_adv", Var(
            "Dissipation of potential Energy", W_GRID, "m^2/s^3",
            "Dissipation of potential Energy"
        )),
        ("P_diss_comp", Var(
            "Dissipation of potential Energy", W_GRID, "m^2/s^3",
            "Dissipation of potential Energy"
        )),
        ("P_diss_sources", Var(
            "Dissipation of potential Energy", W_GRID, "m^2/s^3",
            "Dissipation of potential Energy"
        )),
        ("K_diss_gm", Var(
            "Dissipation of mean energy", W_GRID, "m^2/s^3",
            "Dissipation of mean energy"
        ))
    ])),

    ("enable_streamfunction", OrderedDict([
        ("psi", Var(
            "Streamfunction", ZETA_HOR + TIMESTEPS, "m^3/s", "Streamfunction", output=True
        )),
        ("dpsi", Var(
            "Streamfunction tendency", ZETA_HOR + TIMESTEPS, "m^3/s^2", "Streamfunction tendency"
        )),
        #("psin", Var(
        #    "Boundary streamfunction", ZETA_HOR + ISLE, "m^3/s",
        #    "Boundary streamfunction"
        #)),
    ])),

    ("not enable_streamfunction", OrderedDict([
        ("surf_press", Var("Surface pressure", T_HOR, "m^2/s^2", "Surface pressure", output=True)),
    ])),

    ("enable_tempsalt_sources", OrderedDict([
        ("temp_source", Var(
            "Source of temperature", T_GRID, "K/s",
            "Non-conservative source of temperature", output=True
        )),
        ("salt_source", Var(
            "Source of salt", T_GRID, "g/(kg s)",
            "Non-conservative source of salt", output=True
        )),
    ])),

    ("enable_momentum_sources", OrderedDict([
        ("u_source", Var(
            "Source of zonal velocity", U_GRID, "m/s^2 (?)",
            "Non-conservative source of zonal velocity", output=True
        )),
        ("v_source", Var(
            "Source of meridional velocity", V_GRID, "m/s^2 (?)",
            "Non-conservative source of meridional velocity", output=True
        )),
    ])),

    ("not enable_hydrostatic", OrderedDict([
        ("p_non_hydro", Var(
            "Non-hydrostatic pressure", T_GRID, "m^2/s^2",
            "Non-hydrostatic pressure", output=True
        )),
        ("dw", Var(
            "Vertical velocity tendency", W_GRID + TIMESTEPS, "m/s^2",
            "Vertical velocity tendency"
        )),
        ("dw_cor", Var(
            "Change of w by Coriolis force", W_GRID + TIMESTEPS, "m/s^2",
            "Change of vertical velocity due to Coriolis force"
        )),
        ("dw_adv", Var(
            "Change of w by advection", W_GRID + TIMESTEPS, "m/s^2",
            "Change of vertical velocity due to advection"
        )),
        ("dw_mix", Var(
            "Change of w by vertical mixing", W_GRID + TIMESTEPS, "m/s^2",
            "Change of vertical velocity due to vertical mixing"
        )),
    ])),
    ("enable_neutral_diffusion", OrderedDict([
        ("K_11", Var("Isopycnal mixing coefficient", T_GRID, "?", "Isopycnal mixing tensor component")),
        ("K_13", Var("Isopycnal mixing coefficient", T_GRID, "?", "Isopycnal mixing tensor component")),
        ("K_22", Var("Isopycnal mixing coefficient", T_GRID, "?", "Isopycnal mixing tensor component")),
        ("K_23", Var("Isopycnal mixing coefficient", T_GRID, "?", "Isopycnal mixing tensor component")),
        ("K_31", Var("Isopycnal mixing coefficient", T_GRID, "?", "Isopycnal mixing tensor component")),
        ("K_32", Var("Isopycnal mixing coefficient", T_GRID, "?", "Isopycnal mixing tensor component")),
        ("K_33", Var("Isopycnal mixing coefficient", T_GRID, "?", "Isopycnal mixing tensor component")),
        ("Ai_ez", Var("?", T_GRID + TENSOR_COMP, "?", "?")),
        ("Ai_nz", Var("?", T_GRID + TENSOR_COMP, "?", "?")),
        ("Ai_bx", Var("?", T_GRID + TENSOR_COMP, "?", "?")),
        ("Ai_by", Var("?", T_GRID + TENSOR_COMP, "?", "?")),
    ])),
    ("enable_skew_diffusion", OrderedDict([
        ("B1_gm", Var(
            "Zonal component of GM streamfunction", V_GRID, "m^2/s",
            "Zonal component of GM streamfunction"
        )),
        ("B2_gm", Var(
            "Meridional component of GM streamfunction", U_GRID, "m^2/s",
            "Meridional component of GM streamfunction"
        ))
    ])),
    ("enable_bottom_friction_var", OrderedDict([
        ("r_bot_var_u", Var(
            "Bottom friction coeff.", U_HOR, "?", "Zonal bottom friction coefficient"
        )),
        ("r_bot_var_v", Var(
            "Bottom friction coeff.", V_HOR, "?", "Meridional bottom friction coefficient"
        )),
    ])),
    ("enable_TEM_friction", OrderedDict([
        ("kappa_gm", Var("Vertical diffusivity", W_GRID, "m^2/s", "Vertical diffusivity")),
    ])),
    ("enable_tke", OrderedDict([
        ("tke", Var(
            "Turbulent kinetic energy", W_GRID + TIMESTEPS, "m^2/s^2",
            "Turbulent kinetic energy", output=True
        )),
        ("sqrttke", Var(
            "Square-root of TKE", W_GRID, "m/s", "Square-root of TKE"
        )),
        ("dtke", Var(
            "Turbulent kinetic energy tendency", W_GRID + TIMESTEPS, "m^2/s^3",
            "Turbulent kinetic energy tendency"
        )),
        ("Prandtlnumber", Var("Prandtl number", W_GRID, "", "Prandtl number")),
        ("mxl", Var("Mixing length", W_GRID, "m", "Mixing length")),
        ("forc_tke_surface", Var(
            "TKE surface flux", T_HOR, "m^3/s^3", "TKE surface flux", output=True
        )),
        ("tke_diss", Var(
            "TKE dissipation", W_GRID, "m^2/s^3", "TKE dissipation"
        )),
        ("tke_surf_corr", Var(
            "Correction of TKE surface flux", T_HOR, "m^3/s^3",
            "Correction of TKE surface flux"
        )),
    ])),
    ("enable_eke", OrderedDict([
        ("eke", Var(
            "meso-scale energy", W_GRID + TIMESTEPS, "m^2/s^2",
            "meso-scale energy", output=True
        )),
        ("deke", Var(
            "meso-scale energy tendency", W_GRID + TIMESTEPS, "m^2/s^3",
            "meso-scale energy tendency"
        )),
        ("sqrteke", Var(
            "square-root of eke", W_GRID, "m/s", "square-root of eke"
        )),
        ("L_rossby", Var("Rossby radius", T_HOR, "m", "Rossby radius")),
        ("L_rhines", Var("Rhines scale", W_GRID, "m", "Rhines scale")),
        ("eke_len", Var("Eddy length scale", T_GRID, "m", "Eddy length scale")),
        ("eke_diss_iw", Var(
            "Dissipation of EKE to IW", W_GRID, "m^2/s^3",
            "Dissipation of EKE to internal waves"
        )),
        ("eke_diss_tke", Var(
            "Dissipation of EKE to TKE", W_GRID, "m^2/s^3",
            "Dissipation of EKE to TKE"
        )),
        ("eke_bot_flux", Var(
            "Flux by bottom friction", T_HOR, "m^3/s^3", "Flux by bottom friction"
        )),
    ])),
    ("enable_eke_leewave_dissipation", OrderedDict([
        ("eke_topo_hrms", Var(
            "?", T_HOR, "?", "?"
        )),
        ("eke_topo_lam", Var(
            "?", T_HOR, "?", "?"
        )),
        ("hrms_k0", Var(
            "?", T_HOR, "?", "?"
        )),
        ("c_lee", Var(
            "Lee wave dissipation coefficient", T_HOR, "1/s",
            "Lee wave dissipation coefficient"
        )),
        ("eke_lee_flux", Var(
            "Lee wave flux", T_HOR, "m^3/s^3", "Lee wave flux",
        )),
        ("c_Ri_diss", Var(
            "Interior dissipation coefficient", W_GRID, "1/s",
            "Interior dissipation coefficient"
        )),
    ])),
    ("enable_idemix", OrderedDict([
        ("E_iw", Var(
            "Internal wave energy", W_GRID + TIMESTEPS, "m^2/s^2", "Internal wave energy", output=True
        )),
        ("dE_iw", Var(
            "Internal wave energy tendency", W_GRID + TIMESTEPS, "m^2/s^2",
            "Internal wave energy tendency"
        )),
        ("c0", Var(
            "Vertical IW group velocity", W_GRID, "m/s",
            "Vertical internal wave group velocity"
        )),
        ("v0", Var(
            "Horizontal IW group velocity", W_GRID, "m/s",
            "Horizontal internal wave group velocity"
        )),
        ("alpha_c", Var("?", W_GRID, "?", "?")),
        ("iw_diss", Var(
            "IW dissipation", W_GRID, "m^2/s^3", "Internal wave dissipation"
        )),
        ("forc_iw_surface", Var(
            "IW surface forcing", T_HOR, "m^3/s^3",
            "Internal wave surface forcing", time_dependent=False, output=True
        )),
        ("forc_iw_bottom", Var(
            "IW bottom forcing", T_HOR, "m^3/s^3",
            "Internal wave bottom forcing", time_dependent=False, output=True
        )),
    ])),
    ("enable_idemix_M2", OrderedDict([
        ("E_M2", Var("M2 energy", T_HOR, "m^3/s^2", "M2 energy", output=True)),
        ("dE_M2", Var("M2 energy tendency", T_HOR, "m^3/s^3", "M2 energy tendency")),
        ("E_struct_M2", Var("M2 structure function", T_GRID, "", "M2 structure function")),
        ("cg_M2", Var("M2 group velocity", T_HOR, "m/s", "M2 group velocity")),
        ("kdot_x_M2", Var("M2 refraction", U_HOR, "1/s", "M2 refraction")),
        ("kdot_y_M2", Var("M2 refraction", V_HOR, "1/s", "M2 refraction")),
        ("tau_M2", Var("M2 decay time scale", T_HOR, "1/s", "M2 decay time scale")),
        ("alpha_M2_cont", Var(
            "M2-continuum coupling coefficient", T_HOR, "s/m^3",
            "M2-continuum coupling coefficient"
        )),
        ("forc_M2", Var("M2 forcing", T_HOR, "m^3/s^3", "M2 forcing")),
    ])),
            # if self.enable_idemix_M2 or self.enable_idemix_niw:
            #     self.topo_shelf = np.zeros((self.nx+4,self.ny+4))
            #     self.topo_hrms = np.zeros((self.nx+4,self.ny+4))
            #     self.topo_lam = np.zeros((self.nx+4,self.ny+4))
            #     self.phit = np.zeros(self.np)
            #     self.dphit = np.zeros(self.np)
            #     self.phiu = np.zeros(self.np)
            #     self.dphiu = np.zeros(self.np)
            #     self.maskTp = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.maskUp = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.maskVp = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.maskWp = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.cn = np.zeros((self.nx+4,self.ny+4))
            #     self.phin = np.zeros((self.nx+4,self.ny+4,self.nz))
            #     self.phinz = np.zeros((self.nx+4,self.ny+4,self.nz))
            #     self.tau_M2 = np.zeros((self.nx+4,self.ny+4))
            #     self.tau_niw = np.zeros((self.nx+4,self.ny+4))
            #     self.alpha_M2_cont = np.zeros((self.nx+4,self.ny+4))
            #     self.bc_south = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.bc_north = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.bc_west = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.bc_east = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.M2_psi_diss = np.zeros((self.nx+4,self.ny+4,self.np))
            #
            # if self.enable_idemix_M2:
            #     self.E_M2 = np.zeros((self.nx+4,self.ny+4,self.np,3))
            #     self.dE_M2p = np.zeros((self.nx+4,self.ny+4,self.np,3))
            #     self.cg_M2 = np.zeros((self.nx+4,self.ny+4))
            #     self.kdot_x_M2 = np.zeros((self.nx+4,self.ny+4))
            #     self.kdot_y_M2 = np.zeros((self.nx+4,self.ny+4))
            #     self.forc_M2 = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.u_M2 = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.v_M2 = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.w_M2 = np.zeros((self.nx+4,self.ny+4,self.np))
            #     self.E_struct_M2 = np.zeros((self.nx+4,self.ny+4,self.nz))
            #     self.E_M2_int = np.zeros((self.nx+4,self.ny+4))
    ("enable_idemix_niw", OrderedDict([
        ("omega_niw", Var("?", T_HOR, "?", "?")),
        ("E_niw", Var(
            "NIW energy", T_HOR + NP + TIMESTEPS, "m^3/s^2", "NIW energy", output=True
        )),
        ("dE_niwp", Var(
            "NIW energy tendency", T_HOR + NP + TIMESTEPS, "m^3/s^3",
            "NIW energy tendency"
        )),
        ("cg_niw", Var("NIW group velocity", T_HOR, "m/s", "NIW group velocity")),
        ("kdot_x_niw", Var("NIW refraction", U_HOR, "1/s", "NIW refraction")),
        ("kdot_y_niw", Var("NIW refraction", V_HOR, "1/s", "NIW refraction")),
        ("forc_niw", Var("NIW forcing", T_HOR, "m^3/s^3", "NIW forcing")),
        ("u_niw", Var("?", T_HOR + NP, "?", "?")),
        ("v_niw", Var("?", T_HOR + NP, "?", "?")),
        ("w_niw", Var("?", T_HOR + NP, "?", "?")),
        ("E_struct_niw", Var(
            "NIW structure function", T_GRID, "", "NIW structure function"
        )),
        ("E_niw_int", Var(
            "?", T_HOR, "?", "?"
        )),
        ("tau_niw", Var(
            "NIW decay time scale", T_HOR, "1/s", "NIW decay time scale"
        )),
    ])),
])
