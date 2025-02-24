/** @sleektiv-module **/
import { setSelection } from "@web_editor/js/editor/sleektiv-editor/src/utils/utils";
import { makeView, setupViewRegistries } from "@web/../tests/views/helpers";
import { patchWithCleanup, nextTick, triggerHotkey } from "@web/../tests/helpers/utils";
import { Wysiwyg } from "@web_editor/js/wysiwyg/wysiwyg";
import {
    triggerEvent,
    insertText,
    insertParagraphBreak,
} from "@web_editor/js/editor/sleektiv-editor/test/utils";

function onMount() {
    const editor = wysiwyg.sleektivEditor;
    const editable = editor.editable;
    editor.testMode = true;
    return { editor, editable };
}

function inputText(selector, content) {
    const selectorElement = document.querySelector(selector);
    selectorElement.focus();
    for (const char of content) {
        selectorElement.dispatchEvent(new window.KeyboardEvent("keydown", { key: char }));
        document.execCommand("insertText", false, char);
        selectorElement.dispatchEvent(new window.KeyboardEvent("keyup", { key: char }));
    }
}

let serverData;
let wysiwyg;

QUnit.module(
    "Link Creation",
    {
        before: function () {
            serverData = {
                models: {
                    note: {
                        fields: {
                            body: {
                                string: "Editor",
                                type: "html",
                            },
                        },
                        records: [
                            {
                                id: 1,
                                display_name: "first record",
                                body: "<p><br></p>",
                            },
                        ],
                    },
                },
            };
        },
        beforeEach: async function () {
            setupViewRegistries();
            patchWithCleanup(Wysiwyg.prototype, {
                init() {
                    super.init(...arguments);
                    wysiwyg = this;
                },
            });
            await makeView({
                type: "form",
                serverData,
                resModel: "note",
                arch:
                    "<form>" +
                    '<field name="body" widget="html_legacy" style="height: 100px"/>' +
                    "</form>",
                resId: 1,
            });
        },
    },
    function () {
        QUnit.module("HotKeys");

        QUnit.test("should be able to create link with ctrl+k and typing Create link in command palette search", async function (assert) {
            const { editor, editable } = onMount();
            const node = editable.querySelector("p");
            setSelection(node, 0);
            // Open command palette
            await triggerHotkey("control+k");
            // Search Create link from command palette
            inputText(".o_command_palette_search input", "Create link");
            await nextTick();
            await triggerHotkey("Enter");
            // Insert link url
            inputText('input[id="o_link_dialog_url_input"]', "#");
            // Click on Insert button
            editor.document.querySelector(".o_dialog footer button.btn-primary").click();
            await nextTick();
            editor.clean();
            assert.strictEqual(
                editable.innerHTML,
                `<p><a href="#" target="_blank">#</a><br></p>`
            );
        });

        QUnit.test("should be able to create link with ctrl+k and ctrl+k", async function (assert) {
            const { editor, editable } = onMount();
            const node = editable.querySelector("p");
            setSelection(node, 0);
            // Open command palette
            await triggerHotkey("control+k");
            // Hot key for Create link
            await triggerHotkey("control+k")
            // Insert link url
            inputText('input[id="o_link_dialog_url_input"]', "#");
            // Click on Insert button
            editor.document.querySelector(".o_dialog footer button.btn-primary").click();
            await nextTick();
            editor.clean();
            assert.strictEqual(
                editable.innerHTML,
                `<p><a href="#" target="_blank">#</a><br></p>`
            );
        });

        QUnit.test(
            "should be able to create link with ctrl+k , and should make link on two existing characters",
            async function (assert) {
                const { editor, editable } = onMount();
                const node = editable.querySelector("p");
                setSelection(node, 0);
                insertText(editor, "Hello");
                setSelection(node, 1, node, 3);
                // Open command palette
                await triggerHotkey("control+k");
                // Hot key for Create link
                await triggerHotkey("control+k")
                // Insert link url
                inputText('input[id="o_link_dialog_url_input"]', "#");
                // Click on Insert button
                editor.document.querySelector(".o_dialog footer button.btn-primary").click();
                await nextTick();
                editor.clean();
                assert.strictEqual(
                    editable.innerHTML,
                    `<p>H<a href="#" target="_blank">el</a>lo</p>`
                );
            }
        );


        QUnit.module("Typing based");

        QUnit.test("typing valid URL + space should convert to link", async function (assert) {
                const { editor, editable } = onMount();
                const node = editable.querySelector("p");
                setSelection(node, 0);
                inputText(".sleektiv-editor-editable p", "http://google.co.in");
                insertText(editor, " ");
                editor.clean();
                assert.strictEqual(
                    editable.innerHTML,
                    `<p><a href="http://google.co.in">http://google.co.in</a> </p>`
                );
            }
        );

        QUnit.test("typing invalid URL + space should not convert to link", async function (assert) {
            const { editor, editable } = onMount();
            const node = editable.querySelector("p");
            setSelection(node, 0);
            inputText(".sleektiv-editor-editable p", "www.sleektiv");
            insertText(editor, " ");
            editor.clean();
            assert.strictEqual(editable.innerHTML, "<p>www.sleektiv </p>");
        });


        QUnit.module("Toolbar based");

        QUnit.test("should convert all selected text to link", async function (assert) {
            const { editor, editable } = onMount();
            const node = editable.querySelector("p");
            setSelection(node, 0);
            insertText(editor, "Hello");
            setSelection(node, 0, node, 5);
            await nextTick();
            // Click on link button from floating toolbar
            editor.document.querySelector("#toolbar .fa-link").click();
            await nextTick();
            // Insert link url
            inputText('input[id="o_link_dialog_url_input"]', "#");
            // Click on Insert button
            editor.document.querySelector(".o_dialog footer button.btn-primary").click();
            await nextTick();
            editor.clean();
            assert.strictEqual(
                editable.innerHTML,
                `<p><a href="#" target="_blank">Hello</a></p>`
            );
        });

        QUnit.test("should set the link on two existing characters", async function (assert) {
            const { editor, editable } = onMount();
            const node = editable.querySelector("p");
            setSelection(node, 0);
            insertText(editor, "Hello");
            setSelection(node, 1, node, 3);
            // Click on link button from floating toolbar
            editor.document.querySelector("#toolbar .fa-link").click();
            await nextTick();
            // Insert link url
            inputText('input[id="o_link_dialog_url_input"]', "#");
            // Click on Insert button
            editor.document.querySelector(".o_dialog footer button.btn-primary").click();
            await nextTick();
            editor.clean();
            assert.strictEqual(
                editable.innerHTML,
                `<p>H<a href="#" target="_blank">el</a>lo</p>`
            );
        });


        QUnit.module("PowerBox related");

        QUnit.test("Should be able to insert link on empty p", async function (assert) {
            const { editor, editable } = onMount();
            const node = editable.querySelector("p");
            setSelection(node, 0);
            triggerEvent(node, "input", { data: "/" });
            // Click on link button from powerbox
            editor.document.querySelector(".oe-powerbox-commandWrapper .fa-link").click();
            await nextTick();
            // Insert link url
            inputText('input[id="o_link_dialog_url_input"]', "#");
            // Click on Insert button
            editor.document.querySelector(".o_dialog footer button.btn-primary").click();
            await nextTick();
            editor.clean();
            assert.strictEqual(
                editable.innerHTML,
                `<p><a href="#" target="_blank">#</a><br></p>`
            );
        });

        QUnit.test("should insert a link and preserve spacing", async function (assert) {
            const { editor, editable } = onMount();
            const node = editable.querySelector("p");
            setSelection(node, 0);
            insertText(editor, "ab");
            setSelection(node.firstChild, 1, node.firstChild, 1);
            insertText(editor, " ");
            setSelection(node.firstChild, 2, node.firstChild, 2);
            insertText(editor, " ");
            setSelection(node.firstChild, 3, node.firstChild, 3);
            insertText(editor, " ");
            setSelection(node.firstChild, 2, node.firstChild, 2);
            triggerEvent(node, "input", { data: "/" });
            // Click on link button from powerbox
            editor.document.querySelector(".oe-powerbox-commandWrapper .fa-link").click();
            await nextTick();
            // Insert link label
            inputText('input[id="o_link_dialog_label_input"]', "link");
            // Insert link url
            inputText('input[id="o_link_dialog_url_input"]', "#");
            // Click on Insert button
            editor.document.querySelector(".o_dialog footer button.btn-primary").click();
            await nextTick();
            editor.clean();
            assert.strictEqual(
                editable.innerHTML,
                `<p>a <a href="#" target="_blank">link</a>&nbsp;&nbsp;b</p>`
            );
        });

        QUnit.test(
            "should insert a link and write a character after the link is created",
            async function (assert) {
                const { editor, editable } = onMount();
                const node = editable.querySelector("p");
                setSelection(node, 0);
                insertText(editor, "ab");
                setSelection(node.firstChild, 1);
                triggerEvent(node, "input", { data: "/" });
                // Click on link button from powerbox
                editor.document.querySelector(".oe-powerbox-commandWrapper .fa-link").click();
                await nextTick();
                // Insert link url
                inputText('input[id="o_link_dialog_url_input"]', "#");
                // Click on Insert button
                editor.document.querySelector(".o_dialog footer button.btn-primary").click();
                await nextTick();
                insertText(editor, "D");
                editor.clean();
                assert.strictEqual(
                    editable.innerHTML,
                    `<p>a<a href="#" target="_blank">#</a>Db</p>`
                );
            }
        );

        QUnit.test(
            "should insert a link and write 2 character after the link is created",
            async function (assert) {
                const { editor, editable } = onMount();
                const node = editable.querySelector("p");
                setSelection(node, 0);
                insertText(editor, "ab");
                setSelection(node.firstChild, 1);
                triggerEvent(node, "input", { data: "/" });
                // Click on link button from powerbox
                editor.document.querySelector(".oe-powerbox-commandWrapper .fa-link").click();
                await nextTick();
                await triggerHotkey("Enter");
                // Insert link url
                inputText('input[id="o_link_dialog_url_input"]', "#");
                // Click on Insert button
                editor.document.querySelector(".o_dialog footer button.btn-primary").click();
                await nextTick();
                insertText(editor, "E");
                insertText(editor, "D");
                editor.clean();
                assert.strictEqual(
                    editable.innerHTML,
                    `<p>a<a href="#" target="_blank">#</a>EDb</p>`
                );
            }
        );

        QUnit.test(
            "should insert a link and write a character after the link then create a new <p>",
            async function (assert) {
                const { editor, editable } = onMount();
                const node = editable.querySelector("p");
                setSelection(node, 0);
                insertText(editor, "ab");
                triggerEvent(node, "input", { data: "/" });
                // Click on link button from powerbox
                editor.document.querySelector(".oe-powerbox-commandWrapper .fa-link").click();
                await nextTick();
                await triggerHotkey("Enter");
                // Insert link label
                inputText('input[id="o_link_dialog_label_input"]', "link");
                // Insert link url
                inputText('input[id="o_link_dialog_url_input"]', "#");
                // Click on Insert button
                editor.document.querySelector(".o_dialog footer button.btn-primary").click();
                await nextTick();
                insertText(editor, "E");
                await insertParagraphBreak(editor);
                editor.clean();
                assert.strictEqual(
                    editable.innerHTML,
                    `<p>ab<a href="#" target="_blank">link</a>E</p><p><br></p>`
                );
            }
        );

        QUnit.test(
            "should insert a link, write a character, a new <p>, and another character",
            async function (assert) {
                const { editor, editable } = onMount();
                const node = editable.querySelector("p");
                setSelection(node, 0);
                insertText(editor, "ab");
                setSelection(node.firstChild, 1);
                triggerEvent(node, "input", { data: "/" });
                // Click on link button from powerbox
                editor.document.querySelector(".oe-powerbox-commandWrapper .fa-link").click();
                await nextTick();
                await triggerHotkey("Enter");
                // Insert link label
                inputText('input[id="o_link_dialog_label_input"]', "link");
                // Insert link url
                inputText('input[id="o_link_dialog_url_input"]', "#");
                // Click on Insert button
                editor.document.querySelector(".o_dialog footer button.btn-primary").click();
                await nextTick();
                insertText(editor, "E");
                await insertParagraphBreak(editor);
                insertText(editor, "D");
                editor.clean();
                assert.strictEqual(
                    editable.innerHTML,
                    `<p>a<a href="#" target="_blank">link</a>E</p><p>Db</p>`
                );
            }
        );

        QUnit.test(
            "should insert a link and write a character at the end of the link then insert a <br>",
            async function (assert) {
                const { editor, editable } = onMount();
                const node = editable.querySelector("p");
                setSelection(node, 0);
                insertText(editor, "ab");
                setSelection(node.firstChild, 1);
                triggerEvent(node, "input", { data: "/" });
                // Click on link button from powerbox
                editor.document.querySelector(".oe-powerbox-commandWrapper .fa-link").click();
                await nextTick();
                await triggerHotkey("Enter");
                // Insert link label
                inputText('input[id="o_link_dialog_label_input"]', "link");
                // Insert link url
                inputText('input[id="o_link_dialog_url_input"]', "#");
                // Click on Insert button
                editor.document.querySelector(".o_dialog footer button.btn-primary").click();
                await nextTick();
                insertText(editor, "E");
                triggerEvent(node, "input", { inputType: "insertLineBreak" });
                editor.clean();
                assert.strictEqual(
                    editable.innerHTML,
                    `<p>a<a href="#" target="_blank">link</a>E<br>b</p>`
                );
            }
        );

        QUnit.test(
            "should insert a link and write a character insert a <br> and another character",
            async function (assert) {
                const { editor, editable } = onMount();
                const node = editable.querySelector("p");
                setSelection(node, 0);
                insertText(editor, "ab");
                setSelection(node.firstChild, 1);
                triggerEvent(node, "input", { data: "/" });
                // Click on link button from powerbox
                editor.document.querySelector(".oe-powerbox-commandWrapper .fa-link").click();
                await nextTick();
                await triggerHotkey("Enter");
                // Insert link label
                inputText('input[id="o_link_dialog_label_input"]', "link");
                // Insert link url
                inputText('input[id="o_link_dialog_url_input"]', "#");
                // Click on Insert button
                editor.document.querySelector(".o_dialog footer button.btn-primary").click();
                await nextTick();
                insertText(editor, "E");
                triggerEvent(node, "input", { inputType: "insertLineBreak" });
                insertText(editor, "D");
                editor.clean();
                assert.strictEqual(
                    editable.innerHTML,
                    `<p>a<a href="#" target="_blank">link</a>E<br>Db</p>`
                );
            }
        );
    }
);
