import marimo as mo


def create_file_selector():
    # return mo.ui.file(label="Select a file", multiple=False, kind="area")
    return mo.ui.text(placeholder="Path to output file", full_width=True, debounce=True)


def create_fwhm_slider():
    return mo.ui.slider(
        label="FWHM", start=0, stop=5000, step=10, value=2000, debounce=False
    )


def create_show_peaks_switch():
    return mo.ui.switch(label="Show Peaks")


def create_peak_threshold_slider():
    return mo.ui.slider(
        label="Peak Threshold",
        start=0,
        stop=1,
        step=0.01,
        value=0.1,
        debounce=False,
    )
