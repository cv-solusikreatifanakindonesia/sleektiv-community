/** @sleektiv-module */

import { Dialog } from "@web/core/dialog/dialog";
import { Component } from "@sleektiv/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class companyStateDialog extends Component {
    static components = { Dialog };
    static template = "l10n_in_pos.companyStateDialog";
    static props = {
        close: Function,
    };

    setup() {
        this.pos = usePos();
    }

    redirect() {
        window.location = "/sleektiv/companies/" + this.pos.company.id;
    }

    onClose() {
        this.props.close();
    }
}
