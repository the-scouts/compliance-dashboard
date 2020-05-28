window.dash_clientside = Object.assign({}, window.dash_clientside, {
    compliance: {
        download_pdf: downloadPdf,
        download_png: downloadImg,
        new_dashboard_spinner: newDashboardSpinner,
        new_dashboard_spinner_hide: newDashboardSpinnerHide,
    }
});

const svg_spinner = '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid" fill="#6a6a6a"><path d="M50 25h1v10h-1z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-1.22s" repeatCount="indefinite"/></path><path d="M62.5 28.35l.866.5-5 8.66-.866-.5z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-1.11s" repeatCount="indefinite"/></path><path d="M71.65 37.5l.5.866-8.66 5-.5-.866z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-0.99s" repeatCount="indefinite"/></path><path d="M75 50v1H65v-1z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-0.88s" repeatCount="indefinite"/></path><path d="M71.65 62.5l-.5.866-8.66-5 .5-.866z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-0.77s" repeatCount="indefinite"/></path><path d="M62.5 71.65l-.866.5-5-8.66.866-.5z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-0.66s" repeatCount="indefinite"/></path><path d="M50 75h-1V65h1z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-0.55s" repeatCount="indefinite"/></path><path d="M37.5 71.65l-.866-.5 5-8.66.866.5z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-0.44s" repeatCount="indefinite"/></path><path d="M28.35 62.5l-.5-.866 8.66-5 .5.866z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-0.33s" repeatCount="indefinite"/></path><path d="M25 50v-1h10v1z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-0.22s" repeatCount="indefinite"/></path><path d="M28.35 37.5l.5-.866 8.66 5-.5.866z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="-0.11s" repeatCount="indefinite"/></path><path d="M37.5 28.35l.866-.5 5 8.66-.866.5z"><animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1.33s" begin="0s" repeatCount="indefinite"/></path></svg>'

function showPopup(popupId, text) {
    const downloadPopup = document.getElementById(popupId);
    downloadPopup.innerHTML = "".concat(svg_spinner, "<hr/><p>", text, "</p>");
    downloadPopup.style.display = "block";
}

function hidePopup(popupId) {
    const downloadPopup = document.getElementById(popupId);
    downloadPopup.style.display = "none"
}

function downloadPdf(input) {
    // TODO: Compress PDF. 12Mb native -> 90kb through adobe
    // TODO bold not working for some reason
    
    // Filter for when button not yet clicked
    if (input == null) {
        return window.dash_clientside.no_update;
    }
    // get needed elements
    const title = document.getElementsByClassName("report-title")[0]
    const reportContainer = document.getElementById("report-container")

    // store original text
    const titleTxt = title.innerText

    // display a message to the user
    showPopup("download-popup", "Downloading report, please wait...")
    title.innerText = titleTxt.replace("–", "-")

    // initialise the jsPDF object
    let pdf = new jsPDF({
        orientation: "landscape",
        unit: "pt",
        format: "a4",
        // compress: true,
        putOnlyUsedFonts: true,

    });

    // get needed width/height ratios
    const widthRatio = pdf.internal.pageSize.getWidth() / reportContainer.offsetWidth;
    const heightRatio = pdf.internal.pageSize.getHeight() / reportContainer.offsetHeight;
    const ratio = heightRatio < widthRatio ? heightRatio : widthRatio;

    // generate PDF
    pdf.setDisplayMode('fullpage');
    pdf.html(
        reportContainer,
        {
            callback: doc => {
                doc.save("dashboard.pdf")
                title.innerText = titleTxt
                setTimeout(() => hidePopup("download-popup"), 1000)
            },
            html2canvas: {
                scale: ratio,
            }
        }
    );
    return window.dash_clientside.no_update;
}

function downloadImg(input) {
    // Filter for when button not yet clicked
    if (input == null) {
        return window.dash_clientside.no_update;
    }

    // Show waiting popup
    showPopup("download-popup", "Downloading report, please wait...")

    html2canvas(
        document.getElementById("report-container"),
        {scale: 2}
    ).then(
        canvas => {
            let downloadLink = document.createElement("a");
            downloadLink.href = canvas.toDataURL("image/png");
            downloadLink.download = "dashboard.png";
            downloadLink.target = "_blank"
            downloadLink.click();
            setTimeout(() => hidePopup("download-popup"), 1000)
        }
    );
    return window.dash_clientside.no_update;
}

function newDashboardSpinner(input) {
    // Filter for when button not yet clicked
    if (input == null) {
        return window.dash_clientside.no_update;
    }
    showPopup("new-dash-popup", "Generating report, please wait...<br/>(this may be a short while)")
    return window.dash_clientside.no_update;
}

function newDashboardSpinnerHide(input){
    // Filter for when button not yet clicked
    if (input == null) {
        return window.dash_clientside.no_update;
    }
    hidePopup("new-dash-popup")
    return window.dash_clientside.no_update;
}