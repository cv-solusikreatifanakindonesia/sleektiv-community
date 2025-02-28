/** @sleektiv-module **/

import { barcodeGenericHandlers } from "@barcodes/barcode_handlers";
import { barcodeService } from "@barcodes/barcode_service";
import {
    editInput,
    getFixture,
    mockTimeout,
    nextTick,
    patchWithCleanup,
} from "@web/../tests/helpers/utils";
import { makeView, setupViewRegistries } from "@web/../tests/views/helpers";
import { registry } from "@web/core/registry";
import { simulateBarCode } from "../helpers";

const serviceRegistry = registry.category("services");

let serverData;
let target;

QUnit.module("Barcodes", (hooks) => {
    hooks.beforeEach(() => {
        target = getFixture();
        serverData = {
            models: {
                order: {
                    fields: {
                        _barcode_scanned: { string: "Barcode scanned", type: "char" },
                        line_ids: {
                            string: "Order lines",
                            type: "one2many",
                            relation: "order_line",
                        },
                    },
                    records: [{ id: 1, line_ids: [1, 2] }],
                },
                order_line: {
                    fields: {
                        product_id: { string: "Product", type: "many2one", relation: "product" },
                        product_barcode: { string: "Product Barcode", type: "char" },
                        quantity: { string: "Quantity", type: "integer" },
                    },
                    records: [
                        { id: 1, product_id: 1, quantity: 0, product_barcode: "1234567890" },
                        { id: 2, product_id: 2, quantity: 0, product_barcode: "0987654321" },
                    ],
                },
                product: {
                    fields: {
                        name: { string: "Product name", type: "char" },
                        int_field: { string: "Integer", type: "integer" },
                        int_field_2: { string: "Integer", type: "integer" },
                        barcode: { string: "Barcode", type: "char" },
                    },
                    records: [
                        { id: 1, name: "Large Cabinet", barcode: "1234567890" },
                        { id: 2, name: "Cabinet with Doors", barcode: "0987654321" },
                    ],
                },
            },
        };

        setupViewRegistries();
        serviceRegistry.add("barcode", barcodeService, { force: true });
        serviceRegistry.add("barcode_autoclick", barcodeGenericHandlers, { force: true });
    });

    QUnit.test("Button with barcode_trigger", async (assert) => {
        const form = await makeView({
            type: "form",
            resModel: "product",
            serverData,
            arch: `<form>
                        <header>
                            <button name="do_something" string="Validate" type="object" barcode_trigger="DOIT"/>
                            <button name="do_something_else" string="Validate" type="object" invisible="1" barcode_trigger="DOTHAT"/>
                        </header>
                    </form>`,
            resId: 2,
        });

        patchWithCleanup(form.env.services.action, {
            doActionButton: (data) => {
                assert.step(data.name);
            },
        });
        patchWithCleanup(form.env.services.notification, {
            add: (params) => {
                assert.step(params.type);
            },
        });

        // OBTDOIT
        simulateBarCode(["O", "B", "T", "D", "O", "I", "T", "Enter"]);
        await nextTick();
        // OBTDOTHAT (should not call execute_action as the button isn't visible)
        simulateBarCode(["O", "B", "T", "D", "O", "T", "H", "A", "T", "Enter"]);
        await nextTick();
        assert.verifySteps(["do_something"]);

        assert.containsOnce(target, ".o_form_statusbar > .o_statusbar_buttons");
    });

    QUnit.test(
        "Two buttons with same barcode_trigger and the same string and action",
        async function (assert) {
            const form = await makeView({
                type: "form",
                resModel: "product",
                serverData,
                arch: `<form>
                    <header>
                        <button name="do_something" string="Validate" type="object" invisible="0" barcode_trigger="DOIT"/>
                        <button name="do_something" string="Validate" type="object" invisible="1" barcode_trigger="DOIT"/>
                    </header>
                </form>`,
                resId: 2,
            });

            patchWithCleanup(form.env.services.action, {
                doActionButton: (data) => {
                    assert.step(data.name);
                },
            });
            patchWithCleanup(form.env.services.notification, {
                add: (params) => {
                    assert.step(params.type);
                },
            });
            // OBTDOIT should call execute_action as the first button is visible
            simulateBarCode(["O", "B", "T", "D", "O", "I", "T", "Enter"]);
            await nextTick();
            assert.verifySteps(["do_something"]);
        }
    );

    QUnit.test("edit, save and cancel buttons", async function (assert) {
        await makeView({
            type: "form",
            resModel: "product",
            serverData,
            arch: '<form><field name="display_name"/></form>',
            mockRPC: function (route, args) {
                if (args.method === "web_save") {
                    assert.step("save");
                }
            },
            resId: 1,
        });

        // OCDEDIT
        simulateBarCode(["O", "C", "D", "E", "D", "I", "T", "Enter"]);
        await nextTick();
        assert.containsOnce(target, ".o_form_editable", "should have switched to 'edit' mode");
        // dummy change to check that it actually saves
        await editInput(target.querySelector(".o_field_widget input"), null, "test");
        // OCDSAVE
        simulateBarCode(["O", "C", "D", "S", "A", "V", "E", "Enter"]);
        await nextTick();
        assert.verifySteps(["save"], "should have saved");

        // OCDEDIT
        simulateBarCode(["O", "C", "D", "E", "D", "I", "T", "Enter"]);
        await nextTick();
        // dummy change to check that it correctly discards
        await editInput(target.querySelector(".o_field_widget input"), null, "test");
        // OCDDISC
        simulateBarCode(["O", "C", "D", "D", "I", "S", "C", "Enter"]);
        await nextTick();
        assert.verifySteps([], "should not have saved");
    });

    QUnit.test("pager buttons", async function (assert) {
        const mock = mockTimeout();

        await makeView({
            type: "form",
            resModel: "product",
            serverData,
            arch: '<form><field name="display_name"/></form>',
            resId: 1,
            resIds: [1, 2],
        });

        assert.strictEqual(target.querySelector(".o_field_widget input").value, "Large Cabinet");


        // OCDNEXT
        simulateBarCode(["O", "C", "D", "N", "E", "X", "T", "Enter"]);
        await nextTick();
        assert.strictEqual(
            target.querySelector(".o_field_widget input").value,
            "Cabinet with Doors"
        );

        // OCDPREV
        simulateBarCode(["O", "C", "D", "P", "R", "E", "V", "Enter"]);
        await nextTick();
        assert.strictEqual(target.querySelector(".o_field_widget input").value, "Large Cabinet");

        // OCDPAGERLAST
        simulateBarCode(["O","C","D","P","A","G","E","R","L","A","S","T","Enter"]);
        // need to await 2 macro steps
        await mock.advanceTime(50);
        await mock.advanceTime(50);
        assert.strictEqual(
            target.querySelector(".o_field_widget input").value,
            "Cabinet with Doors"
        );

        // OCDPAGERFIRST
        simulateBarCode(["O","C","D","P","A","G","E","R","F","I","R","S","T","Enter"]);
        // need to await 2 macro steps
        await mock.advanceTime(50);
        await mock.advanceTime(50);
        assert.strictEqual(target.querySelector(".o_field_widget input").value, "Large Cabinet");
    });
});
