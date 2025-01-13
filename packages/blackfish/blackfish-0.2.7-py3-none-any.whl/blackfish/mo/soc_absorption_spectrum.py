import marimo as mo

show_peak_switch = mo.ui.switch(label="Show peaks")

peak_threshold_slider = mo.ui.slider(
    label="Peak threshold",
    start=0.1,
    stop=0.9,
    step=0.01,
    value=0.3,
    orientation="horizontal",
)

fwhm_slider = mo.ui.slider(
    label="FWHM", start=0, stop=5000, step=10, value=2000, orientation="horizontal"
)


soc_absorption_spectrum_ui = mo.ui.dictionary(
    {
        "fwhm": fwhm_slider,
        "threshold": peak_threshold_slider,
        "show": show_peak_switch,
    }
)
