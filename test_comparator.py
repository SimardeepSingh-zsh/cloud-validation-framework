"""
   Common file for running validator functions.
"""
import argparse
import sys
import json
import atexit
import pymongo
from antlr4 import InputStream
from antlr4 import CommonTokenStream
from processor.comparison.comparisonantlr.comparatorLexer import comparatorLexer
from processor.comparison.comparisonantlr.comparatorParser import comparatorParser
from processor.comparison.comparisonantlr.rule_interpreter import RuleInterpreter
from processor.logging.log_handler import getlogger
from processor.helper.config.rundata_utils import init_config, delete_run_config
from processor.database.database import init_db
from processor.helper.json.json_utils import get_container_snapshot_json_files,load_json,\
    get_field_value, get_container_dir
from processor.database.database import COLLECTION, get_documents
from processor.helper.config.config_utils import DATABASE, DBNAME, get_config


logger = getlogger()


def main(arg_vals=None):
    """Main driver utility for running validator tests."""
    logger.info("Comand: '%s %s'", sys.executable.rsplit('/', 1)[-1], ' '.join(sys.argv))
    cmd_parser = argparse.ArgumentParser("Comparator functional tests.")
    cmd_parser.add_argument('container', action='store', help='Container tests directory.')
    args = cmd_parser.parse_args(arg_vals)
    # Delete the rundata at the end of the script.
    atexit.register(delete_run_config)
    logger.info(args)
    init_config()
    init_db()
    snapshot_dir, snapshot_files = get_container_snapshot_json_files(args.container)
    if not snapshot_files:
        logger.info("No Snapshot files in %s, exiting!...", snapshot_dir)
        return False
    logger.info('Snapshot files: %s', snapshot_files)
    dbname = get_config(DATABASE, DBNAME)
    for fl in snapshot_files:
        snapshot_ids = populate_snapshots_from_file(fl)
    logger.debug(snapshot_ids)
    for sid, coll in snapshot_ids.items():
        docs = get_documents(coll, {'snapshotId': sid}, dbname,
                             sort=[('timestamp', pymongo.DESCENDING)], limit=1)
        logger.debug('Number of Snapshot Documents: %s', len(docs))
        if docs and len(docs):
            doc = docs[0]['json']
            logger.debug(json.dumps(doc, indent=2))
    test6 = '%s/test6.json' % get_container_dir(args.container)
    test6_json = load_json(test6)
    logger.debug(test6_json)
    otherdata = {'dbname': dbname, 'snapshots': snapshot_ids}
    for testcase in test6_json['testSet'][0]['cases']:
        rulestr = testcase['rule']
        main_comparator(rulestr, otherdata)




def populate_snapshots_from_file(snapshot_file):
    """Load the file as json and populate from json file."""
    snapshot_coll = {}
    snapshot_json_data = load_json(snapshot_file)
    if not snapshot_json_data:
        logger.info("Snapshot file %s looks to be empty, next!...", snapshot_file)
        return snapshot_coll
    snapshots = get_field_value(snapshot_json_data, 'snapshots')
    if not snapshots:
        logger.info("Json Snapshot does not contain snapshots, next!...")
        return snapshot_coll
    for snapshot in snapshots:
        if 'nodes' not in snapshot or not snapshot['nodes']:
            logger.info("No nodes in snapshot to be backed up!...")
            continue
        for node in snapshot['nodes']:
            sid = get_field_value(node, 'snapshotId')
            col_val = node['collection'] if 'collection' in node else COLLECTION
            collection = col_val.replace('.', '').lower()
            snapshot_coll[sid] = collection
    return snapshot_coll

def main_comparator(code, otherdata):
    logger.info('#' * 75)
    logger.info('Actual Rule: %s', code)
    inputStream = InputStream(code)
    lexer = comparatorLexer(inputStream)
    stream = CommonTokenStream(lexer)
    parser = comparatorParser(stream)
    tree = parser.expression()
    # print(tree.toStringTree(recog=parser))
    children = []
    for child in tree.getChildren():
        children.append((child.getText()))
    logger.info('*' * 50)
    logger.debug("All the parsed tokens: %s", children)
    r_i = RuleInterpreter(children, **otherdata)
    # print('LHS operand: ', r_i.lhs_operand)
    # print('Comparator: ', r_i.op)
    # print('RHS operand: ', r_i.rhs_operand)
    # print('!' * 50)
    # # print(r_i.match_method(''.join(r_i.lhs)))
    # # print(r_i.match_method(''.join(r_i.rhs)))
    # r_i.compare()


if __name__ == '__main__':
    main()
