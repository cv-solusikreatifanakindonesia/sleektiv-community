/** @sleektiv-module */

import * as spreadsheet from "@sleektiv/o-spreadsheet";
const { inverseCommandRegistry, otRegistry } = spreadsheet.registries;

function identity(cmd) {
    return [cmd];
}

otRegistry.addTransformation(
    "DELETE_FIGURE",
    ["LINK_SLEEKTIV_MENU_TO_CHART"],
    (toTransform, executed) => {
        if (executed.id === toTransform.chartId) {
            return undefined;
        }
        return toTransform;
    }
);

inverseCommandRegistry.add("LINK_SLEEKTIV_MENU_TO_CHART", identity);
