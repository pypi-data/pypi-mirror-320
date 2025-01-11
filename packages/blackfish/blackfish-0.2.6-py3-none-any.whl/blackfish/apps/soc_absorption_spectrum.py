import marimo

__generated_with = "0.10.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import blackfish as bf
    return bf, mo


@app.cell
def _(bf):
    file = bf.apps.ui_elements.create_file_selector()
    file
    return (file,)


@app.cell
def _(bf, mo):
    fwhm_slider = bf.apps.ui_elements.create_fwhm_slider()
    show_peak_switch = bf.apps.ui_elements.create_show_peaks_switch()
    peak_threshold_slider = bf.apps.ui_elements.create_peak_threshold_slider()

    mo.hstack([
        show_peak_switch, peak_threshold_slider, fwhm_slider
    ])
    return fwhm_slider, peak_threshold_slider, show_peak_switch


@app.cell
def _(bf, file, fwhm_slider, mo, peak_threshold_slider, show_peak_switch):
    mo.stop(not file.value, mo.md("Provide a file!"))

    fig = bf.ORCA(file.value).soc_absorption_spectrum_chart(
        fwhm=fwhm_slider.value,
        peaks=show_peak_switch.value,
        peak_threshold=peak_threshold_slider.value
    )

    mo.center(mo.ui.altair_chart(fig).interactive())
    return (fig,)


if __name__ == "__main__":
    app.run()
