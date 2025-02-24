import { registry } from "@web/core/registry";
import { Component } from "@sleektiv/owl";
import { useTime } from "@point_of_sale/app/utils/time_hook";

export class SaverScreen extends Component {
    static template = "point_of_sale.SaverScreen";
    static storeOnOrder = false;
    static updatePreviousScreen = false;
    static props = [];

    setup() {
        this.time = useTime();
    }
}

registry.category("pos_screens").add("SaverScreen", SaverScreen);
