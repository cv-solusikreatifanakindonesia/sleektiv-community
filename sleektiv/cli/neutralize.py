# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import optparse
import sys
from pathlib import Path

import sleektiv

from . import Command

_logger = logging.getLogger(__name__)


class Neutralize(Command):
    """Neutralize a production database for testing: no emails sent, etc."""

    def run(self, args):
        parser = sleektiv.tools.config.parser
        parser.prog = f'{Path(sys.argv[0]).name} {self.name}'
        group = optparse.OptionGroup(parser, "Neutralize", "Neutralize the database specified by the `-d` argument.")
        group.add_option("--stdout", action="store_true", dest="to_stdout",
                         help="Output the neutralization SQL instead of applying it")
        parser.add_option_group(group)
        opt = sleektiv.tools.config.parse_config(args, setup_logging=True)

        dbname = sleektiv.tools.config['db_name']
        if not dbname:
            _logger.error('Neutralize command needs a database name. Use "-d" argument')
            sys.exit(1)

        if not opt.to_stdout:
            _logger.info("Starting %s database neutralization", dbname)

        try:
            with sleektiv.sql_db.db_connect(dbname).cursor() as cursor:
                if opt.to_stdout:
                    installed_modules = sleektiv.modules.neutralize.get_installed_modules(cursor)
                    queries = sleektiv.modules.neutralize.get_neutralization_queries(installed_modules)
                    # pylint: disable=bad-builtin
                    print('BEGIN;')
                    for query in queries:
                        # pylint: disable=bad-builtin
                        print(query.rstrip(";") + ";")
                    # pylint: disable=bad-builtin
                    print("COMMIT;")
                else:
                    sleektiv.modules.neutralize.neutralize_database(cursor)

        except Exception:
            _logger.critical("An error occurred during the neutralization. THE DATABASE IS NOT NEUTRALIZED!")
            sys.exit(1)
