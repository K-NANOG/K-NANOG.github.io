const rows_per_rect = parseInt(get_css_variable("--rows-per-rect"));
const cols_per_rect = parseInt(get_css_variable("--cols-per-rect"));

const calendar = document.getElementById("calendar");
const life_expectancy = 60;
const numDecades = Math.floor(life_expectancy / 10);

populate_calendar(numDecades);
fill_calendar("23/05/2006");

/**
 * Fill every week, counting from the given bday
 * bday format: dd/mm/yyyy
 */
function fill_calendar(bday) {
    let [day, month, year] = bday.split("/");
    const birthDate = new Date(`${month}/${day}/${year}`);
    const now = new Date();
    const dayDiff = (now - birthDate) / (1000 * 3600 * 24);
    const years = Math.floor(dayDiff / 365.25);
    const remainingWeeks = Math.floor((dayDiff % 365.25) / 7);
    const totalWeeks = years * 52 + remainingWeeks;

    for (let week = 0; week < totalWeeks; week++) {
        paint_week(week);
    }
}

/**
 * Fill week cell
 */
function paint_week(num) {
    const week = document.getElementById(`week-${num}`);
    if (week) {
        week.classList.add("filled");
    }
}

/**
 * Set week IDs
 */
function set_ids(numDecades) {
    const weeks_per_year = cols_per_rect * 2;
    const weeks_per_decade = weeks_per_year * 10;

    for (let decade = 0; decade < numDecades; decade++) {
        for (let rect = 0; rect < 2; rect++) {
            const rectElement = document.getElementById(`rect-${decade}-${rect}`);
            rectElement.childNodes.forEach((cell, index) => {
                const row = Math.floor(index / cols_per_rect);
                const offset = index % cols_per_rect;
                const weekId = decade * weeks_per_decade + row * weeks_per_year + rect * cols_per_rect + offset;
                cell.id = `week-${weekId}`;
            });
        }
    }
}

/**
 * Fill calendar with week cells
 */
function populate_calendar(numDecades) {
    for (let i = 0; i < numDecades; i++) {
        spawn_decade(i);
    }
    set_ids(numDecades);
}

/**
 * Instantiate 2 rectangles
 */
function spawn_decade(decade) {
    for (let i = 0; i < 2; i++) {
        const rect = spawn_rectangle(rows_per_rect, cols_per_rect);
        rect.id = `rect-${decade}-${i}`;
        calendar.appendChild(rect);
    }
}

/**
 * Smaller set of cells
 */
function spawn_rectangle(rows, cols) {
    const rect = document.createElement("div");
    rect.classList.add("rect-container");

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            rect.appendChild(spawn_cell());
        }
    }
    return rect;
}

/**
 * Cell: single week square
 */
function spawn_cell() {
    const div = document.createElement("div");
    div.classList.add("week-cell");
    return div;
}

/**
 * Wrapper to get CSS variables
 */
function get_css_variable(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

document.getElementById("downloadBtn").addEventListener("click", () => {
    html2canvas(document.querySelector(".content")).then((canvas) => {
        const anchorTag = document.createElement("a");
        document.body.appendChild(anchorTag);
        anchorTag.download = "mementoMori.png";
        anchorTag.href = canvas.toDataURL();
        anchorTag.target = '_blank';
        anchorTag.click();
    });
});
