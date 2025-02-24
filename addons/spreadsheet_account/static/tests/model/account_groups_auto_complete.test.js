import { describe, expect, test } from "@sleektiv/hoot";
import { stores } from "@sleektiv/o-spreadsheet";
import { defineSpreadsheetModels } from "@spreadsheet/../tests/helpers/data";
import { makeStore } from "@spreadsheet/../tests/helpers/stores";

describe.current.tags("headless");
defineSpreadsheetModels();

const { CellComposerStore } = stores;

test("SLEEKTIV.ACCOUNT.GROUP type", async function () {
    const { store: composer } = await makeStore(CellComposerStore);

    composer.startEdition("=SLEEKTIV.ACCOUNT.GROUP(");
    const autoComplete = composer.autocompleteProvider;
    expect(autoComplete.proposals.map((p) => p.text)).toEqual([
        '"asset_receivable"',
        '"asset_cash"',
        '"asset_current"',
        '"asset_non_current"',
        '"asset_prepayments"',
        '"asset_fixed"',
        '"liability_payable"',
        '"liability_credit_card"',
        '"liability_current"',
        '"liability_non_current"',
        '"equity"',
        '"equity_unaffected"',
        '"income"',
        '"income_other"',
        '"expense"',
        '"expense_depreciation"',
        '"expense_direct_cost"',
        '"off_balance"',
    ]);
    autoComplete.selectProposal(autoComplete.proposals[0].text);
    expect(composer.currentContent).toBe('=SLEEKTIV.ACCOUNT.GROUP("asset_receivable"');
    expect(composer.autocompleteProvider).toBe(undefined);
});
