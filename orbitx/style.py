

VPYTHON_CSS = """<style>
* {
    background-color: black;
    color: white;
    border-collapse: collapse;
    border-color: white;
}

div {
    border-collapse: collapse;
}

canvas {
    border-color: white;
}

table {
    margin-top: 1em;
    margin-bottom: 1em;
    height: 30%;
}
th {
    text-align: left;
    border-collapse: collapse;
    height: 50px;
}

td {
    width: 20%;
}

tr {
    height: 20px;
    border-style: solid;
}

.newsection {
    padding-top: 1em;
}
.num {
    font-family: monospace;
    font-weight: bold;
    border-collapse: collapse;
}
select {
    width: 100px;
}
input {
    width: 100px !important;
    height: unset !important;
}
.helptext {
    font-size: 75%;
}
</style>
<style title="disable_helptext">
.helptext {
    display: none;
}
</style>"""

VPYTHON_JS = """<script>
function show_hide_help() {
    // If helptext is enabled, we have to "disable disabling it."
    styleSheets = document.styleSheets;
    for (i = 0; i < styleSheets.length; ++i) {
        console.log(styleSheets[i].title)
        if (styleSheets[i].title == "disable_helptext") {
            styleSheets[i].disabled =
                document.getElementById("helptext_checkbox").checked
        }
    }
}

// Keep inputs deselected, so that keyboard input doesn't interfere with them.
for (var inp of document.querySelectorAll("input,select")) {
    inp.onchange = function(){this.blur()};
}
</script>"""

HELP_CHECKBOX = """
<input type="checkbox" id="helptext_checkbox" onClick="show_hide_help()">"""

# TODO: there's room for automating tables here.
INPUT_CHEATSHEET = """
<table class="helptext">
    <caption>Input Cheatsheet</caption>
    <tr>
            <th>Input</th>
            <th>Action</th>
    </tr>
    <tr>
        <td>Scroll, or ALT/OPTION-drag &nbsp</td>
        <td>Zoom View</td>
    </tr>
    <tr>
        <td>Ctrl-Click</td>
        <td>Rotate View</td>
    </tr>
    <tr>
        <td>W/S</td>
        <td>Throttle Up/Down (press shift for fine control)</td>
    </tr>
    <tr>
        <td>Enter</td>
        <td>Set engines to 100%</td>
    </tr>
    <tr>
        <td>Backspace</td>
        <td>Set engines to 0%</td>
    </tr>
    <tr>
        <td>A/D</td>
        <td>Rotate Habitat</td>
    </tr>
    <tr>
        <td>L</td>
        <td>Toggle labels</td>
    </tr>
    <!-- re-enable this when we've fixed pausing
    <tr>
        <td>P</td>
        <td>Pause simulation</td>
    </tr>-->
</table>
"""
