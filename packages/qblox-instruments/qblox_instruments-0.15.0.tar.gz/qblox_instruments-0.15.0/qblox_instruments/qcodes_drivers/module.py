# ----------------------------------------------------------------------------
# Description    : QCM/QRM QCoDeS interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

from typing import Any, Callable, List, Optional, Union
from functools import partial, wraps
import math
import warnings
from qcodes import validators as vals
from qcodes import Instrument, InstrumentChannel, Parameter
from qblox_instruments import InstrumentClass, InstrumentType, TypeHandle
from qblox_instruments.qcodes_drivers.sequencer import Sequencer
from qblox_instruments.qcodes_drivers.io_channel import IOChannel
from qblox_instruments.qcodes_drivers.quad import Quad
from qblox_instruments.ieee488_2 import (
    DummyBinnedAcquisitionData,
    DummyScopeAcquisitionData,
)
from qblox_instruments.docstring_helpers import partial_with_numpy_doc
from qblox_instruments.types import FrequencyParameter


# -- class -------------------------------------------------------------------
class Module(InstrumentChannel):
    """
    This class represents a QCM/QRM module. It combines all module specific
    parameters and functions into a single QCoDes InstrumentChannel.
    """

    # ------------------------------------------------------------------------
    def __init__(
        self,
        parent: Instrument,
        name: str,
        slot_idx: int,
    ):
        """
        Creates a QCM/QRM/QTM module class and adds all relevant parameters for
        the module.

        Parameters
        ----------
        parent : Instrument
            The QCoDeS class to which this module belongs.
        name : str
            Name of this module channel
        slot_idx : int
            The index of this module in the parent instrument, representing
            which module is controlled by this class.

        Returns
        ----------

        Raises
        ----------
        """

        # Initialize instrument channel
        super().__init__(parent, name)

        # Store sequencer index
        self._slot_idx = slot_idx

        for attr_name in Module._get_required_parent_qtm_attr_names():
            self._register(attr_name)
        for attr_name in Module._get_required_parent_qrm_qcm_attr_names():
            self._register(attr_name)

        # Add required parent attributes for the QCoDeS parameters to function
        try:
            self.parent._present_at_init(self.slot_idx)
            # Add QCM/QRM/QTM/QDM/LINQ/QRC QCoDeS parameters
            if self.is_qtm_type:
                add_qcodes_params(self, num_seq=8, num_dio=8)
            elif self.is_qcm_type or self.is_qrm_type:
                # TO DO: Improve the detection of amount of sequencers
                add_qcodes_params(self, num_seq=6)
            elif self.is_qrc_type:
                add_qcodes_params(self, num_seq=6)

        except KeyError:
            pass

        # Add module QCoDeS parameters
        self.add_parameter(
            "present",
            label="Module present status",
            docstring="Sets/gets module present status for slot {} in the " "Cluster.",
            unit="",
            vals=vals.Bool(),
            get_parser=bool,
            get_cmd=self._get_modules_present,
        )

        self.add_parameter(
            "connected",
            label="Module connected status",
            docstring="Gets module connected status for slot {} in the " "Cluster.",
            unit="",
            vals=vals.Bool(),
            get_parser=bool,
            get_cmd=self._get_modules_connected,
        )

    # ------------------------------------------------------------------------
    @property
    def slot_idx(self) -> int:
        """
        Get slot index.

        Parameters
        ----------

        Returns
        ----------
        int
            Slot index

        Raises
        ----------
        """

        return self._slot_idx

    # ------------------------------------------------------------------------
    @property
    def module_type(self) -> InstrumentType:
        """
        Get module type (e.g. QRM, QCM).

        Parameters
        ----------

        Returns
        ----------
        InstrumentType
            Module type

        Raises
        ----------
        KeyError
            Module is not available.
        """

        return self.parent._module_type(self.slot_idx)

    # ------------------------------------------------------------------------
    @property
    def is_qcm_type(self) -> bool:
        """
        Return if module is of type QCM.

        Parameters
        ----------

        Returns
        ----------
        bool
            True if module is of type QCM.

        Raises
        ----------
        KeyError
            Module is not available.
        """

        return self.parent._is_qcm_type(self.slot_idx)

    # ------------------------------------------------------------------------
    @property
    def is_qrm_type(self) -> bool:
        """
        Return if module is of type QRM.

        Parameters
        ----------

        Returns
        ----------
        bool:
            True if module is of type QRM.

        Raises
        ----------
        KeyError
            Module is not available.
        """

        return self.parent._is_qrm_type(self.slot_idx)

    # ------------------------------------------------------------------------
    @property
    def is_qtm_type(self) -> bool:
        """
        Return if module is of type QTM.

        Parameters
        ----------

        Returns
        ----------
        bool:
            True if module is of type QTM.

        Raises
        ----------
        KeyError
            Module is not available.
        """

        return self.parent._is_qtm_type(self.slot_idx)

    # ------------------------------------------------------------------------
    @property
    def is_qdm_type(self) -> bool:
        """
        Return if module is of type QDM.

        Parameters
        ----------

        Returns
        ----------
        bool:
            True if module is of type QDM.

        Raises
        ----------
        KeyError
            Module is not available.
        """

        return self.parent._is_qdm_type(self.slot_idx)

    # ------------------------------------------------------------------------
    @property
    def is_linq_type(self) -> bool:
        """
        Return if module is of type LINQ.

        Parameters
        ----------

        Returns
        ----------
        bool:
            True if module is of type LINQ.

        Raises
        ----------
        KeyError
            Module is not available.
        """

        return self.parent._is_linq_type(self.slot_idx)

    # ------------------------------------------------------------------------
    @property
    def is_qrc_type(self) -> bool:
        """
        Return if module is of type QRC.

        Parameters
        ----------

        Returns
        ----------
        bool:
            True if module is of type QRC.

        Raises
        ----------
        KeyError
            Module is not available.
        """

        return self.parent._is_qrc_type(self.slot_idx)

    # ------------------------------------------------------------------------
    @property
    def is_rf_type(self) -> bool:
        """
        Return if module is of type QCM-RF or QRM-RF.

        Parameters
        ----------

        Returns
        ----------
        bool:
            True if module is of type QCM-RF or QRM-RF.

        Raises
        ----------
        KeyError
            Module is not available.
        """

        return self.parent._is_rf_type(self.slot_idx)

    # ------------------------------------------------------------------------
    @property
    def sequencers(self) -> List:
        """
        Get list of sequencers submodules.

        Parameters
        ----------

        Returns
        ----------
        list
            List of sequencer submodules.

        Raises
        ----------
        """
        sequencers_list = []
        for submodule in self.submodules.values():
            if "sequencer" in str(submodule):
                sequencers_list.append(submodule)
        return list(sequencers_list)

    # ------------------------------------------------------------------------
    @property
    def io_channels(self) -> List:
        """
        Get list of digital I/O channels.

        Parameters
        ----------

        Returns
        ----------
        list
            List of digital I/O channels.

        Raises
        ----------
        """
        io_channels_list = []
        for submodule in self.submodules.values():
            if "io_channel" in str(submodule):
                io_channels_list.append(submodule)
        return list(io_channels_list)

    # ------------------------------------------------------------------------
    @property
    def quads(self) -> List:
        """
        Get list of digital I/O quads.

        Parameters
        ----------

        Returns
        ----------
        list
            List of digital I/O quads.

        Raises
        ----------
        """
        quads_list = []
        for submodule in self.submodules.values():
            if "quad" in str(submodule):
                quads_list.append(submodule)
        return list(quads_list)

    # ------------------------------------------------------------------------
    @staticmethod
    def _get_required_parent_qrm_qcm_attr_names() -> List:
        """
        Return list of parent attributes names that are required for the
        QCoDeS parameters to function for a QRM/QCM, so that the can be registered to this
        object using the _register method.

        Parameters
        ----------

        Returns
        ----------
        List
            List of parent attribute names to register.

        Raises
        ----------
        """

        # Constants
        NUM_LO = 2  # Maximum number of LOs
        NUM_IN = 2  # Maximum number of inputs
        NUM_OUT = 4  # Maximum number of outputs
        NUM_MRK = 4  # Maximum number of markers

        # Module present attribute
        attr_names = []
        attr_names.append("_get_modules_present")
        attr_names.append("_get_modules_connected")

        # Channel map attributes
        attr_names.append("disconnect_outputs")
        attr_names.append("disconnect_inputs")
        attr_names.append("_iter_connections")

        # LO attributes
        for operation in ["set", "get"]:
            for idx in range(0, NUM_LO):
                attr_names.append(f"_{operation}_lo_freq_{idx}")
                attr_names.append(f"_{operation}_lo_pwr_{idx}")
                attr_names.append(f"_{operation}_lo_enable_{idx}")
        attr_names.append("_run_mixer_lo_calib")

        # Input attributes
        for operation in ["set", "get"]:
            for idx in range(0, NUM_IN):
                attr_names.append(f"_{operation}_in_amp_gain_{idx}")
                attr_names.append(f"_{operation}_in_offset_{idx}")
            for idx in range(0, round(NUM_IN / 2)):
                attr_names.append(f"_{operation}_in_att_{idx}")

        # Output attributes
        for operation in ["set", "get"]:
            for idx in range(0, NUM_OUT):
                attr_names.append(f"_{operation}_out_amp_offset_{idx}")
                attr_names.append(f"_{operation}_dac_offset_{idx}")
            for idx in range(0, round(NUM_OUT / 2)):
                attr_names.append(f"_{operation}_out_att_{idx}")
                attr_names.append(f"_{operation}_max_out_att_{idx}")

        # Marker attributes
        for operation in ["set", "get"]:
            for idx in range(0, NUM_MRK):
                attr_names.append(f"_{operation}_mrk_inv_en_{idx}")

        # Scope acquisition attributes
        for operation in ["set", "get"]:
            attr_names.append(f"_{operation}_acq_scope_config")
            attr_names.append(f"_{operation}_acq_scope_config_val")
            attr_names.append(f"_{operation}_pre_distortion_config_val")
        attr_names.append(f"_get_output_latency")

        # Sequencer program attributes
        attr_names.append("get_assembler_status")
        attr_names.append("get_assembler_log")

        # Sequencer attributes
        attr_names += Sequencer._get_required_parent_attr_names()

        return attr_names

    # ------------------------------------------------------------------------
    @staticmethod
    def _get_required_parent_qtm_attr_names() -> List:
        """
        Return list of parent attributes names that are required for the
        QCoDeS parameters to function for a QTM, so that the can be registered to this
        object using the _register method.

        Parameters
        ----------

        Returns
        ----------
        List
            List of parent attribute names to register.

        Raises
        ----------
        """

        # Constants
        NUM_IN = 8  # Maximum number of inputs
        NUM_OUT = 8  # Maximum number of outputs
        NUM_MRK = 8  # Maximum number of markers

        # Module present attribute
        attr_names = []
        attr_names.append("_get_modules_present")

        # Channel map attributes
        attr_names.append("_iter_connections")

        # Sequencer program attributes
        attr_names.append("get_assembler_status")
        attr_names.append("get_assembler_log")

        # Scope trigger logic
        attr_names.append("scope_trigger_arm")

        # Sequencer attributes
        attr_names += Sequencer._get_required_parent_attr_names()
        attr_names += IOChannel._get_required_parent_attr_names()
        attr_names += Quad._get_required_parent_attr_names()

        return attr_names

    # ------------------------------------------------------------------------
    def _register(self, attr_name: str) -> None:
        """
        Register parent attribute to this sequencer using functools.partial to
        pre-select the slot index. If the attribute does not exist in the
        parent class, a method that raises a `NotImplementedError` exception
        is registered instead. The docstring of the parent attribute is also
        copied to the registered attribute.

        Parameters
        ----------
        attr_name : str
            Attribute name of parent to register.

        Returns
        ----------

        Raises
        ----------
        """

        if hasattr(self.parent, attr_name):
            parent_attr = getattr(self.parent, attr_name)
            partial_doc = (
                "Note\n"
                + "----------\n"
                + "This method calls {1}.{0} using functools.partial to set the "
                + "slot index. The docstring above is of {1}.{0}:\n\n"
            ).format(attr_name, type(self.parent).__name__)
            partial_func = partial_with_numpy_doc(
                parent_attr, self.slot_idx, end_with=partial_doc
            )
            setattr(self, attr_name, partial_func)
        else:

            def raise_not_implemented_error(*args, **kwargs) -> None:
                raise NotImplementedError(
                    f'{self.parent.name} does not have "{attr_name}" attribute.'
                )

            setattr(self, attr_name, raise_not_implemented_error)

    # ------------------------------------------------------------------------
    def _invalidate_qcodes_parameter_cache(
        self, sequencer: Optional[int] = None
    ) -> None:
        """
        Marks the cache of all QCoDeS parameters in the module, including in
        any sequencers the module might have, as invalid. Optionally,
        a sequencer can be specified. This will invalidate the cache of that
        sequencer only in stead of all parameters.

        Parameters
        ----------
        sequencer : Optional[int]
            Sequencer index of sequencer for which to invalidate the QCoDeS
            parameters.

        Returns
        ----------

        Raises
        ----------
        """

        invalidate_qcodes_parameter_cache(self, sequencer)

    # ------------------------------------------------------------------------
    def __getitem__(
        self, key: str
    ) -> Union[InstrumentChannel, Parameter, Callable[..., Any]]:
        """
        Get sequencer or parameter using string based lookup.

        Parameters
        ----------
        key : str
            Sequencer, parameter or function to retrieve.

        Returns
        ----------
        Union[InstrumentChannel, Parameter, Callable[..., Any]]
            Sequencer, parameter or function.

        Raises
        ----------
        KeyError
            Sequencer, parameter or function does not exist.
        """

        return get_item(self, key)


# -- functions ---------------------------------------------------------------


def add_qcodes_params(
    parent: Union[Instrument, Module], num_seq: int, num_dio: int = 0
) -> None:
    """
    Add all QCoDeS parameters for a single QCM/QRM module.

    Parameters
    ----------
    parent : Union[Instrument, Module]
        Parent object to which the parameters need to be added.
    num_seq : int
        Number of sequencers to add as submodules.

    Returns
    ----------

    Raises
    ----------
    """

    # -- LO frequencies (RF-modules only) ------------------------------------
    if parent.is_rf_type:
        if parent.is_qrm_type:
            parent.add_parameter(
                "out0_in0_lo_freq_cal_type_default",
                label="Default automatic mixer calibration setting",
                docstring="Sets/gets the Default automatic mixer"
                "calibration while setting local oscillator"
                "frequency for output and input 0.",
                unit="Hz",
                vals=vals.Enum("off", "lo only", "lo and sidebands"),
                set_cmd=None,
                get_cmd=None,
                initial_value="off",
            )

            out0_in0_lo_freq = Parameter(
                "_out0_in0_lo_freq",
                label="Local oscillator frequency",
                docstring="Sets/gets the local oscillator frequency for "
                "output 0 and input 0.",
                unit="Hz",
                vals=vals.Numbers(2e9, 18e9),
                set_parser=int,
                get_parser=int,
                set_cmd=parent._set_lo_freq_1,
                get_cmd=parent._get_lo_freq_1,
            )

            parent.add_parameter(
                "out0_in0_lo_freq",
                parameter_class=FrequencyParameter,
                source=out0_in0_lo_freq,
                calibration_function=partial(_calibrate_lo, parent, 1),
            )

            parent.out0_in0_lo_cal = partial(parent._run_mixer_lo_calib, 1)
        else:
            parent.add_parameter(
                "out0_lo_freq_cal_type_default",
                label="Default automatic mixer calibration setting",
                docstring="Sets/gets the Default automatic mixer"
                "calibration while setting local oscillator"
                "frequency for output 0.",
                unit="Hz",
                vals=vals.Enum("off", "lo only", "lo and sidebands"),
                set_cmd=None,
                get_cmd=None,
                initial_value="off",
            )

            out0_lo_freq = Parameter(
                "_out0_lo_freq",
                label="Output 0 local oscillator frequency",
                docstring="Sets/gets the local oscillator frequency for " "output 0.",
                unit="Hz",
                vals=vals.Numbers(2e9, 18e9),
                set_parser=int,
                get_parser=int,
                set_cmd=parent._set_lo_freq_0,
                get_cmd=parent._get_lo_freq_0,
            )

            parent.add_parameter(
                "out0_lo_freq",
                parameter_class=FrequencyParameter,
                source=out0_lo_freq,
                calibration_function=partial(_calibrate_lo, parent, 0),
            )

            parent.out0_lo_cal = partial(parent._run_mixer_lo_calib, 0)

            parent.add_parameter(
                "out1_lo_freq_cal_type_default",
                label="Default automatic mixer calibration setting",
                docstring="Sets/gets the Default automatic mixer"
                "calibration while setting local oscillator"
                "frequency for output 1.",
                unit="Hz",
                vals=vals.Enum("off", "lo only", "lo and sidebands"),
                set_cmd=None,
                get_cmd=None,
                initial_value="off",
            )

            out1_lo_freq = Parameter(
                "out1_lo_freq",
                label="Output 1 local oscillator frequency",
                docstring="Sets/gets the local oscillator frequency for " "output 1.",
                unit="Hz",
                vals=vals.Numbers(2e9, 18e9),
                set_parser=int,
                get_parser=int,
                set_cmd=parent._set_lo_freq_1,
                get_cmd=parent._get_lo_freq_1,
            )

            parent.add_parameter(
                "out1_lo_freq",
                parameter_class=FrequencyParameter,
                source=out1_lo_freq,
                calibration_function=partial(_calibrate_lo, parent, 1),
            )

            parent.out1_lo_cal = partial(parent._run_mixer_lo_calib, 1)

    # -- LO enables (RF-modules only) ----------------------------------------
    if parent.is_rf_type:
        if parent.is_qrm_type:
            parent.add_parameter(
                "out0_in0_lo_en",
                label="Local oscillator enable",
                docstring="Sets/gets the local oscillator enable for "
                "output 0 and input 0.",
                vals=vals.Bool(),
                set_parser=bool,
                get_parser=bool,
                set_cmd=parent._set_lo_enable_1,
                get_cmd=parent._get_lo_enable_1,
            )
        else:
            parent.add_parameter(
                "out0_lo_en",
                label="Output 0 local oscillator enable",
                docstring="Sets/gets the local oscillator enable for " "output 0.",
                vals=vals.Bool(),
                set_parser=bool,
                get_parser=bool,
                set_cmd=parent._set_lo_enable_0,
                get_cmd=parent._get_lo_enable_0,
            )

            parent.add_parameter(
                "out1_lo_en",
                label="Output 1 local oscillator enable",
                docstring="Sets/gets the local oscillator enable for " "output 1.",
                vals=vals.Bool(),
                set_parser=bool,
                get_parser=bool,
                set_cmd=parent._set_lo_enable_1,
                get_cmd=parent._get_lo_enable_1,
            )

    # -- Attenuation settings (RF-modules only) ------------------------------
    if parent.is_rf_type and (parent.is_qcm_type or parent.is_qrm_type):
        if parent.is_qrm_type:
            parent.add_parameter(
                "in0_att",
                label="Input 0 attenuation",
                docstring="Sets/gets input attenuation in a range of 0dB to 30dB with a resolution of 2dB per step.",
                unit="dB",
                vals=vals.Multiples(2, min_value=0, max_value=30),
                set_parser=int,
                get_parser=int,
                set_cmd=parent._set_in_att_0,
                get_cmd=parent._get_in_att_0,
            )

        parent.add_parameter(
            "out0_att",
            label="Output 0 attenuation",
            docstring=f"Sets/gets output attenuation in a range of 0 dB to {parent._get_max_out_att_0()} dB with a resolution of 2dB per step.",
            unit="dB",
            vals=vals.Multiples(
                2,
                min_value=0,
                max_value=parent._get_max_out_att_0(),
            ),
            set_parser=int,
            get_parser=int,
            set_cmd=parent._set_out_att_0,
            get_cmd=parent._get_out_att_0,
        )

        if parent.is_qcm_type:
            parent.add_parameter(
                "out1_att",
                label="Output 1 attenuation",
                docstring=f"Sets/gets output attenuation in a range of 0 dB to {parent._get_max_out_att_1()} dB with a resolution of 2dB per step.",
                unit="dB",
                vals=vals.Multiples(
                    2,
                    min_value=0,
                    max_value=parent._get_max_out_att_1(),
                ),
                set_parser=int,
                get_parser=int,
                set_cmd=parent._set_out_att_1,
                get_cmd=parent._get_out_att_1,
            )

    # -- Input gain (QRM baseband modules only) ------------------------------
    if not parent.is_rf_type and parent.is_qrm_type:
        parent.add_parameter(
            "in0_gain",
            label="Input 0 gain",
            docstring="Sets/gets input 0 gain in a range of -6dB to 26dB "
            "with a resolution of 1dB per step.",
            unit="dB",
            vals=vals.Numbers(-6, 26),
            set_parser=int,
            get_parser=int,
            set_cmd=parent._set_in_amp_gain_0,
            get_cmd=parent._get_in_amp_gain_0,
        )

        parent.add_parameter(
            "in1_gain",
            label="Input 1 gain",
            docstring="Sets/gets input 1 gain in a range of -6dB to 26dB "
            "with a resolution of 1dB per step.",
            unit="dB",
            vals=vals.Numbers(-6, 26),
            set_parser=int,
            get_parser=int,
            set_cmd=parent._set_in_amp_gain_1,
            get_cmd=parent._get_in_amp_gain_1,
        )

    # -- Input offset (QRM modules only) ------------------------------
    if parent.is_qrm_type:
        if parent.is_rf_type:
            parent.add_parameter(
                "in0_offset_path0",
                label="Input 0 offset for path 0",
                docstring="Sets/gets input 0 offset for path 0 in a range of -0.09V to 0.09V",
                unit="V",
                vals=vals.Numbers(-0.09, 0.09),
                set_parser=float,
                get_parser=float,
                set_cmd=parent._set_in_offset_0,
                get_cmd=parent._get_in_offset_0,
            )

            parent.add_parameter(
                "in0_offset_path1",
                label="Input 0 offset for path 1",
                docstring="Sets/gets input 0 offset for path 1 in a range of -0.09V to 0.09V",
                unit="V",
                vals=vals.Numbers(-0.09, 0.09),
                set_parser=float,
                get_parser=float,
                set_cmd=parent._set_in_offset_1,
                get_cmd=parent._get_in_offset_1,
            )
        else:
            parent.add_parameter(
                "in0_offset",
                label="Input 0 offset",
                docstring="Sets/gets input 0 offset in a range of -0.09V to 0.09V",
                unit="V",
                vals=vals.Numbers(-0.09, 0.09),
                set_parser=float,
                get_parser=float,
                set_cmd=parent._set_in_offset_0,
                get_cmd=parent._get_in_offset_0,
            )

            parent.add_parameter(
                "in1_offset",
                label="Input 1 offset",
                docstring="Sets/gets input 1 offset in a range of -0.09V to 0.09V",
                unit="V",
                vals=vals.Numbers(-0.09, 0.09),
                set_parser=float,
                get_parser=float,
                set_cmd=parent._set_in_offset_1,
                get_cmd=parent._get_in_offset_1,
            )

    # -- Output offsets (All modules) ----------------------------------------
    if parent.is_rf_type:
        parent.add_parameter(
            "out0_offset_path0",
            label="Output 0 offset for path 0",
            docstring="Sets/gets output 0 offset for path 0.",
            unit="mV",
            vals=vals.Numbers(-84.0, 73.0),
            set_parser=float,
            get_parser=float,
            set_cmd=parent._set_out_amp_offset_0,
            get_cmd=parent._get_out_amp_offset_0,
        )

        parent.add_parameter(
            "out0_offset_path1",
            label="Output 0 offset for path 1",
            docstring="Sets/gets output 0 offset for path 1.",
            unit="mV",
            vals=vals.Numbers(-84.0, 73.0),
            set_parser=float,
            get_parser=float,
            set_cmd=parent._set_out_amp_offset_1,
            get_cmd=parent._get_out_amp_offset_1,
        )

        if parent.is_qcm_type:
            parent.add_parameter(
                "out1_offset_path0",
                label="Output 1 offset for path 0",
                docstring="Sets/gets output 1 offset for path 0.",
                unit="mV",
                vals=vals.Numbers(-84.0, 73.0),
                set_parser=float,
                get_parser=float,
                set_cmd=parent._set_out_amp_offset_2,
                get_cmd=parent._get_out_amp_offset_2,
            )

            parent.add_parameter(
                "out1_offset_path1",
                label="Output 1 offset for path 1",
                docstring="Sets/gets output 1 offset for path 1.",
                unit="mV",
                vals=vals.Numbers(-84.0, 73.0),
                set_parser=float,
                get_parser=float,
                set_cmd=parent._set_out_amp_offset_3,
                get_cmd=parent._get_out_amp_offset_3,
            )
    elif parent.is_qrm_type or parent.is_qcm_type:
        parent.add_parameter(
            "out0_offset",
            label="Output 0 offset",
            docstring="Sets/gets output 0 offset",
            unit="V",
            vals=(
                vals.Numbers(-2.5, 2.5)
                if parent.is_qcm_type
                else vals.Numbers(-0.5, 0.5)
            ),
            set_parser=float,
            get_parser=float,
            set_cmd=parent._set_dac_offset_0,
            get_cmd=parent._get_dac_offset_0,
        )

        parent.add_parameter(
            "out1_offset",
            label="Output 1 offset",
            docstring="Sets/gets output 1 offset.",
            unit="V",
            vals=(
                vals.Numbers(-2.5, 2.5)
                if parent.is_qcm_type
                else vals.Numbers(-0.5, 0.5)
            ),
            set_parser=float,
            get_parser=float,
            set_cmd=parent._set_dac_offset_1,
            get_cmd=parent._get_dac_offset_1,
        )

        if parent.is_qcm_type:
            parent.add_parameter(
                "out2_offset",
                label="Output 2 offset",
                docstring="Sets/gets output 2 offset.",
                unit="V",
                vals=vals.Numbers(-2.5, 2.5),
                set_parser=float,
                get_parser=float,
                set_cmd=parent._set_dac_offset_2,
                get_cmd=parent._get_dac_offset_2,
            )

            parent.add_parameter(
                "out3_offset",
                label="Output 3 offset",
                docstring="Sets/gets output 3 offset.",
                unit="V",
                vals=vals.Numbers(-2.5, 2.5),
                set_parser=float,
                get_parser=float,
                set_cmd=parent._set_dac_offset_3,
                get_cmd=parent._get_dac_offset_3,
            )

    # -- Scope acquisition settings (QRM modules only) -----------------------
    if parent.is_qrm_type:
        for x in range(0, 2):
            parent.add_parameter(
                f"scope_acq_trigger_mode_path{x}",
                label=f"Scope acquisition trigger mode for input path {x}",
                docstring=f"Sets/gets scope acquisition trigger mode for input path {x} ('sequencer' = triggered by sequencer, 'level' = triggered by input level).",
                unit="",
                vals=vals.Bool(),
                val_mapping={"level": True, "sequencer": False},
                set_parser=bool,
                get_parser=bool,
                set_cmd=partial(
                    parent._set_acq_scope_config_val, ["trig", "mode_path", x]
                ),
                get_cmd=partial(
                    parent._get_acq_scope_config_val, ["trig", "mode_path", x]
                ),
            )

            parent.add_parameter(
                f"scope_acq_trigger_level_path{x}",
                label=f"Scope acquisition trigger level for input path {x}",
                docstring=f"Sets/gets scope acquisition trigger level when using input level trigger mode for input path {x}.",
                unit="",
                vals=vals.Numbers(-1.0, 1.0),
                set_parser=float,
                get_parser=float,
                set_cmd=partial(
                    parent._set_acq_scope_config_val, ["trig", "lvl_path", x]
                ),
                get_cmd=partial(
                    parent._get_acq_scope_config_val, ["trig", "lvl_path", x]
                ),
            )

            parent.add_parameter(
                f"scope_acq_avg_mode_en_path{x}",
                label=f"Scope acquisition averaging mode enable for input path {x}",
                docstring=f"Sets/gets scope acquisition averaging mode enable for input path {x}.",
                unit="",
                vals=vals.Bool(),
                set_parser=bool,
                get_parser=bool,
                set_cmd=partial(parent._set_acq_scope_config_val, ["avg_en_path", x]),
                get_cmd=partial(parent._get_acq_scope_config_val, ["avg_en_path", x]),
            )

        parent.add_parameter(
            "scope_acq_sequencer_select",
            label="Scope acquisition sequencer select",
            docstring="Sets/gets sequencer select that specifies which "
            "sequencer triggers the scope acquisition when using "
            "sequencer trigger mode.",
            unit="",
            vals=vals.Numbers(0, num_seq - 1),
            set_parser=int,
            get_parser=int,
            set_cmd=partial(parent._set_acq_scope_config_val, "sel_acq"),
            get_cmd=partial(parent._get_acq_scope_config_val, "sel_acq"),
        )

    # -- Marker settings (All modules, only 2 markers for RF modules) --------
    if parent.is_qcm_type or parent.is_qrm_type:
        for x in range(0, 4 if not parent.is_rf_type else 2):
            parent.add_parameter(
                f"marker{x}_inv_en",
                label=f"Output {x} marker invert enable",
                docstring=f"Sets/gets output {x} marker invert enable",
                unit="",
                vals=vals.Bool(),
                set_parser=bool,
                get_parser=bool,
                set_cmd=getattr(parent, f"_set_mrk_inv_en_{x}"),
                get_cmd=getattr(parent, f"_get_mrk_inv_en_{x}"),
            )

    # -- Pre-distortion configuration settings
    # Only QCMs and QRMs have predistortions for now
    if parent.is_qcm_type or parent.is_qrm_type or parent.is_qrc_type:
        _add_rtp_qcodes_params(parent)

    # Add sequencers
    for seq_idx in range(0, num_seq):
        seq = Sequencer(parent, f"sequencer{seq_idx}", seq_idx)
        parent.add_submodule(f"sequencer{seq_idx}", seq)

    # Add dio-related components
    for dio_idx in range(0, num_dio):
        io_channel = IOChannel(parent, f"io_channel{dio_idx}", dio_idx)
        parent.add_submodule(f"io_channel{dio_idx}", io_channel)
    for quad_idx in range(0, int(math.ceil(num_dio / 4))):
        quad = Quad(parent, f"quad{quad_idx}", quad_idx)
        parent.add_submodule(f"quad{quad_idx}", quad)


# ----------------------------------------------------------------------------
def invalidate_qcodes_parameter_cache(
    parent: Union[Instrument, Module],
    sequencer: Optional[int] = None,
    quad: Optional[int] = None,
    io_channel: Optional[int] = None,
) -> None:
    """
    Marks the cache of all QCoDeS parameters in the module as invalid,
    including in any sequencer submodules the module might have. Optionally,
    a sequencer can be specified. This will invalidate the cache of that
    sequencer only in stead of all parameters.

    Parameters
    ----------
    parent : Union[Instrument, Module]
        The parent module object for which to invalidate the QCoDeS parameters.
    sequencer : Optional[int]
        The sequencer index for which to invalidate the QCoDeS parameters.
    quad : Optional[int]
        The quad index for which to invalidate the QCoDeS parameters.
    io_channel : Optional[int]
        The IO channel index for which to invalidate the QCoDeS parameters.

    Returns
    ----------

    Raises
    ----------
    """

    # Invalidate module parameters
    if sequencer is None:
        for param in parent.parameters.values():
            param.cache.invalidate()
        sequencer_list = parent.sequencers
    else:
        sequencer_list = [parent.sequencers[sequencer]]

    if quad is None:
        quad_list = parent.quads
    else:
        quad_list = [parent.quads[quad]]

    if io_channel is None:
        io_channel_list = parent.io_channels
    else:
        io_channel_list = [parent.io_channels[io_channel]]

    # Invalidate sequencer parameters
    for seq in sequencer_list:
        seq._invalidate_qcodes_parameter_cache()
    for quad in quad_list:
        quad._invalidate_qcodes_parameter_cache()
    for io_channel in io_channel_list:
        io_channel._invalidate_qcodes_parameter_cache()


# ----------------------------------------------------------------------------
def get_item(
    parent: Union[Instrument, Module], key: str
) -> Union[InstrumentChannel, Parameter, Callable[[Any], Any]]:
    """
    Get submodule or parameter using string based lookup.

    Parameters
    ----------
    parent : Union[Instrument, Module]
        Parent module object to search.
    key : str
        submodule, parameter or function to retrieve.

    Returns
    ----------
    Union[InstrumentChannel, Parameter, Callable[[Any], Any]]
        Submodule, parameter or function.

    Raises
    ----------
    KeyError
        Submodule, parameter or function does not exist.
    """

    # Check for submodule
    try:
        return parent.submodules[key]
    except KeyError:
        try:
            return parent.parameters[key]
        except KeyError:
            return parent.functions[key]


# ----------------------------------------------------------------------------
def _add_rtp_qcodes_params(parent: Union[Instrument, Module]):
    if not parent.is_qcm_type and not parent.is_qrm_type and not parent.is_qrc_type:
        raise TypeError(
            "RTP parameters can only be declared for QRC, QRM and QCM modules."
        )
    predistortion_val_mapping_filter = {
        "bypassed": "disabled",
        "delay_comp": "enabled",
    }
    predist_mapping_docstring = (
        "If 'bypassed', the filter is disabled.\n"
        "If 'delay_comp', the filter is bypassed, but the output is delayed as if it were applied."
    )
    num_iir = 4
    num_markers = 4
    num_channels = 4  # This is the default and it applies to QCM modules
    if parent.is_qrm_type:
        num_channels = 2
    if parent.is_qrc_type:
        num_channels = 12
        num_markers = 1
    num_out = num_channels
    if parent.is_rf_type:
        num_out = num_channels // 2

    def add_distortion_parameters(output):
        parent.add_parameter(
            f"out{output}_fir_coeffs",
            label=f"Coefficients for the FIR filter for output {output}",
            docstring=f"Sets/gets the coefficients for the FIR filter for output {output}",
            unit="",
            vals=vals.Sequence(elt_validator=vals.Numbers(-2, 1.99), length=32),
            set_cmd=partial(
                parent._set_pre_distortion_config_val,
                [f"out{output}", "FIR", "stage0"],
            ),
            get_cmd=partial(
                parent._get_pre_distortion_config_val,
                [f"out{output}", "FIR", "stage0"],
            ),
        )
        for i in range(num_iir):
            parent.add_parameter(
                f"out{output}_exp{i}_time_constant",
                label=f"Time constant of the exponential overshoot filter {i} for output {output}",
                docstring=f"Sets/gets the time constant of the exponential overshoot filter {i} for output {output}",
                unit="",
                vals=vals.Numbers(6, float("inf")),
                set_parser=float,
                get_parser=float,
                set_cmd=partial(
                    parent._set_pre_distortion_config_val,
                    [f"out{output}", "IIR", f"stage{i}", "tau"],
                ),
                get_cmd=partial(
                    parent._get_pre_distortion_config_val,
                    [f"out{output}", "IIR", f"stage{i}", "tau"],
                ),
            )
            parent.add_parameter(
                f"out{output}_exp{i}_amplitude",
                label=f"Amplitude of the exponential overshoot filter {i} for output {output}",
                docstring=f"Sets/gets the amplitude of the exponential overshoot filter {i} for output {output}",
                unit="",
                vals=vals.Numbers(-1, 1),
                set_parser=float,
                get_parser=float,
                set_cmd=partial(
                    parent._set_pre_distortion_config_val,
                    [f"out{output}", "IIR", f"stage{i}", "amp"],
                ),
                get_cmd=partial(
                    parent._get_pre_distortion_config_val,
                    [f"out{output}", "IIR", f"stage{i}", "amp"],
                ),
            )

    def add_output_parameters(output):
        parent.add_parameter(
            f"out{output}_latency",
            label=f"Gets the latency in output path {output}",
            docstring=(
                f"Gets the latency in output path {output}.\n"
                "The output path can change depending on the filter configuration of the output."
            ),
            unit="s",
            set_cmd=False,
            get_cmd=partial(
                parent._get_output_latency,
                2 * output if parent.is_rf_type else output,
            ),
        )
        if parent.is_rf_type:
            parent.add_parameter(
                f"out{output}_fir_config",
                label=f"Configuration of FIR filter for output {output}",
                docstring=f"Sets/gets the configuration of FIR filter for output {output}.\n{predist_mapping_docstring}",
                unit="",
                val_mapping=predistortion_val_mapping_filter,
                set_cmd=partial(
                    lambda output, val: parent.parent._set_pre_distortion_config(
                        parent.slot_idx,
                        {
                            f"out{2 * output}": {"state": {"stage5": val}},
                            f"out{2 * output + 1}": {"state": {"stage5": val}},
                        },
                    ),
                    output,
                ),
                get_cmd=partial(
                    parent._get_pre_distortion_config_val,
                    [f"out{output}", "state", "stage5"],
                ),
            )
            for i in range(num_iir):
                parent.add_parameter(
                    f"out{output}_exp{i}_config",
                    label=f"Configuration of exponential overshoot filter {i} for output {output}",
                    docstring=f"Sets/gets configuration of exponential overshoot filter {i} for output {output}.\n{predist_mapping_docstring}",
                    unit="",
                    val_mapping=predistortion_val_mapping_filter,
                    set_cmd=partial(
                        lambda output, val, stage_idx=i + 1: parent.parent._set_pre_distortion_config(
                            parent.slot_idx,
                            {
                                f"out{2 * output}": {
                                    "state": {f"stage{stage_idx}": val}
                                },
                                f"out{2 * output + 1}": {
                                    "state": {f"stage{stage_idx}": val}
                                },
                            },
                        ),
                        output,
                    ),
                    get_cmd=partial(
                        parent._get_pre_distortion_config_val,
                        [f"out{2 * output}", "state", f"stage{i + 1}"],
                    ),
                )
        else:
            parent.add_parameter(
                f"out{output}_fir_config",
                label=f"Configuration of FIR filter for output {output}",
                docstring=f"Sets/gets the configuration of FIR filter for output {output}.\n{predist_mapping_docstring}",
                unit="",
                val_mapping=predistortion_val_mapping_filter,
                set_cmd=partial(
                    parent._set_pre_distortion_config_val,
                    [f"out{output}", "state", "stage5"],
                ),
                get_cmd=partial(
                    parent._get_pre_distortion_config_val,
                    [f"out{output}", "state", "stage5"],
                ),
            )
            for i in range(num_iir):
                parent.add_parameter(
                    f"out{output}_exp{i}_config",
                    label=f"Configuration of exponential overshoot filter {i} for output {output}",
                    docstring=f"Sets/gets configuration of exponential overshoot filter {i} for output {output}.\n{predist_mapping_docstring}",
                    unit="",
                    val_mapping=predistortion_val_mapping_filter,
                    set_cmd=partial(
                        parent._set_pre_distortion_config_val,
                        [f"out{output}", "state", f"stage{i + 1}"],
                    ),
                    get_cmd=partial(
                        parent._get_pre_distortion_config_val,
                        [f"out{output}", "state", f"stage{i + 1}"],
                    ),
                )

    def add_marker_parameters(x):
        parent.add_parameter(
            f"marker{x}_fir_config",
            label=f"Delay compensation config for the FIR filter on marker {x}",
            docstring=f"Delay compensation config for the FIR filter on marker {x}. If 'bypassed', the marker is not delayed. If 'enabled', the marker is delayed.",
            unit="",
            val_mapping=predistortion_val_mapping_marker,
            set_cmd=partial(
                parent._set_pre_distortion_config_val,
                [f"out{x}", "markers", "state", "stage5"],
            ),
            get_cmd=partial(
                parent._get_pre_distortion_config_val,
                [f"out{x}", "markers", "state", "stage5"],
            ),
        )
        for i in range(num_iir):
            parent.add_parameter(
                f"marker{x}_exp{i}_config",
                label=f"Delay compensation config for the exponential overshoot filter {i} on marker {x}",
                docstring=f"Delay compensation config for the exponential overshoot filter {i} on marker {x}. If 'bypassed', the marker is not delayed. If 'enabled', the marker is delayed.",
                unit="",
                val_mapping=predistortion_val_mapping_marker,
                set_cmd=partial(
                    parent._set_pre_distortion_config_val,
                    [f"out{x}", "markers", "state", f"stage{i + 1}"],
                ),
                get_cmd=partial(
                    parent._get_pre_distortion_config_val,
                    [f"out{x}", "markers", "state", f"stage{i + 1}"],
                ),
            )

    if not parent.is_rf_type:
        if parent.is_qcm_type:
            predist_mapping_docstring += "\nIf 'enabled', the filter is enabled."
            predistortion_val_mapping_filter["enabled"] = "enabled"
            predistortion_val_mapping_filter["delay_comp"] = "comp_delay"

        for output in range(num_out):
            add_output_parameters(output)
            if parent.is_qcm_type:
                add_distortion_parameters(output)
    else:
        for output in range(num_out):
            add_output_parameters(output)

    predistortion_val_mapping_marker = {
        "bypassed": "disabled",
        "delay_comp": "enabled",
    }

    for x in range(num_markers):
        add_marker_parameters(x)


# ----------------------------------------------------------------------------
def _calibrate_lo(
    parent: Union[Instrument, Module],
    output: int,
    cal_type: Optional[str] = None,
) -> None:
    """
    Calibrate the mixer according to the calibration type.

    Parameters
    ----------
    parent : Union[Instrument, Module]
        Parent module object to search.
    output : str
        Output of the module.
    cal_type : Optional[str]
        Automatic mixer calibration to perform after
        setting the frequency. Can be one of
        'off', 'lo only' or 'lo and sidebands'.

    Raises
    ----------
    ValueError
        cal_type is not one of
        'off', 'lo only' or 'lo and sidebands'.
    """
    if cal_type is None:
        if parent.is_qrm_type:
            cal_type = parent.out0_in0_lo_freq_cal_type_default()
        else:
            cal_type = parent.parameters[f"out{output}_lo_freq_cal_type_default"]()
    if cal_type == "lo only":
        parent._run_mixer_lo_calib(output)
        return
    elif cal_type == "lo and sidebands":
        if parent.is_qrm_type:
            connected_sequencers = [
                sequencer
                for sequencer in parent.sequencers
                if sequencer.parameters["connect_out0"]() == "IQ"
            ]
        else:
            connected_sequencers = [
                sequencer
                for sequencer in parent.sequencers
                if (
                    sequencer.parameters[f"connect_out{output}"]() == "IQ"
                    and sequencer.parameters[f"connect_out{(output+1)%2}"]() == "off"
                )
            ]
        parent._run_mixer_lo_calib(output)
        for sequencer in connected_sequencers:
            sequencer.sideband_cal()
        return
    if cal_type != "off":
        raise ValueError(
            "cal_type must be one of 'off', 'lo only' or 'lo and sidebands'."
        )
