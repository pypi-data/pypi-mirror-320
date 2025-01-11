try:
    from qblox_simulator_plugin.predistortions import (
        get_filter_delay,
        bias_tee_correction_hw,
        bias_tee_correction,
        exponential_overshoot_correction_hw,
        exponential_overshoot_correction,
        fir_correction_hw,
        fir_correction,
        get_impulse_response,
    )

except ModuleNotFoundError:
    from .predistortions import (
        get_filter_delay,
        exponential_overshoot_correction,
        fir_correction,
        get_impulse_response,
    )
