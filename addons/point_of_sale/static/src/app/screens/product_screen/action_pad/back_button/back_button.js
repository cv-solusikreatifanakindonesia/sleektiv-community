import { Component } from "@sleektiv/owl";

export class BackButton extends Component {
    static template = "point_of_sale.BackButton";
    static props = {
        onClick: { type: Function },
    };
}
