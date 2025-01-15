#!/usr/bin/env python3
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from appomni.threat.align_tools.align.AlignLexer import AlignLexer
from appomni.threat.align_tools.align.AlignParser import AlignParser
from appomni.threat.align_tools.align.AlignListener import AlignListener
import sys
import os
import json
import argparse
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AlignLintingError:
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def to_dict(self):
        return {
            "message": self.message,
            "line": self.line,
            "column": self.column
        }


class AlignLogLinter(AlignListener):
    VALID_COMMANDS = {
        'copy', 'set', 'translate', 'date', 'convert', 'del', 'rename', 'to_json',
        'append', 'dedupe', 'split', 'convert_nested', 'from_json', 'parse_ip',
        'parse_user_agent', 'parse_sql', 'http', 'regex_capture'
    }

    def __init__(self, schema):
        self.errors = []
        self.variables = set()
        self.referenced_paths = set()
        self.defined_paths = set()
        self.schema = schema

    def get_schema_at_path(self, path):
        parts = path.split('.')
        current = self.schema

        for part in parts:
            if 'properties' not in current:
                return None
            if part not in current['properties']:
                return None
            current = current['properties'][part]
        return current

    def validate_path_and_value(self, path, value, ctx):
        if path.startswith("'") or path.startswith('"'):
            path = path[1:-1]
        if value and (value.startswith("'") or value.startswith('"')):
            value = value[1:-1]

        field_schema = self.get_schema_at_path(path)
        if not field_schema:
            self.errors.append(
                AlignLintingError(
                    f"Invalid path: {path}",
                    ctx.start.line,
                    ctx.start.column
                )
            )
            return False

        if value and 'enum' in field_schema:
            if value not in field_schema['enum']:
                self.errors.append(
                    AlignLintingError(
                        f"Invalid value for '{path}': '{value}' must be one of: {', '.join(field_schema['enum'])}",
                        ctx.start.line,
                        ctx.start.column
                    )
                )
                return False

        return True

    def validate_convert(self, ctx):
        assignments = {assignment.key().getText(): assignment.valueref().getText()
                       for assignment in ctx.assignment()}
        if 'src' in assignments and 'type' in assignments:
            src_path = assignments['src'].strip("'\"")
            convert_type = assignments['type'].strip("'\"")

            field_schema = self.get_schema_at_path(src_path)
            if not field_schema:
                self.errors.append(
                    AlignLintingError(
                        f"Invalid path for conversion: {src_path}",
                        ctx.start.line,
                        ctx.start.column
                    )
                )
                return

            schema_type = field_schema.get('type')
            if not schema_type:
                return

            type_map = {
                'int': 'integer',
                'float': 'number',
                'str': 'string',
                'bool': 'boolean'
            }

            expected_type = type_map.get(convert_type)
            if expected_type and expected_type != schema_type:
                self.errors.append(
                    AlignLintingError(
                        f"Converting to type '{convert_type}' but schema expects '{schema_type}' for path: {src_path}",
                        ctx.start.line,
                        ctx.start.column
                    )
                )

    def enterCommand(self, ctx):
        command_name = ctx.NAME().getText()
        logger.debug(f"Found command: {command_name}")

        match command_name:
            case 'convert':
                self.validate_convert(ctx)

        if command_name not in self.VALID_COMMANDS:
            self.errors.append(
                AlignLintingError(
                    f"Invalid command: {command_name}",
                    ctx.start.line,
                    ctx.start.column
                )
            )
            return

        assignments = {assignment.key().getText(): assignment.valueref().getText()
                       for assignment in ctx.assignment()}
        logger.debug(f"Command assignments: {assignments}")

        if 'dest' in assignments:
            dest_path = assignments['dest']
            if dest_path.startswith("'") or dest_path.startswith('"'):
                dest_path = dest_path[1:-1]
            self.defined_paths.add(dest_path)

            value = assignments.get('value')
            if not self.validate_path_and_value(dest_path, value, ctx):
                return


def lint_file(input_file, schema_file):
    logger.info(f"Loading schema from {schema_file}")
    with open(schema_file, 'r') as f:
        schema = json.load(f)

    logger.info(f"Processing input file {input_file}")
    input_stream = FileStream(input_file)
    lexer = AlignLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = AlignParser(stream)
    tree = parser.align()

    linter = AlignLogLinter(schema)
    walker = ParseTreeWalker()
    logger.info("Walking parse tree")
    walker.walk(linter, tree)

    return linter.errors


def main():
    parser = argparse.ArgumentParser(description='ALIGN Log Linter')
    parser.add_argument('files', nargs='+', help='Input ALIGN files to lint')
    parser.add_argument('--schema', required=True, help='JSON Schema file for validation')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    logger.info(f"Starting linter with args: {args}")

    if not os.path.exists(args.schema):
        logger.error(f"Schema file '{args.schema}' does not exist")
        sys.exit(1)

    exit_code = 0
    all_errors = []

    for input_file in args.files:
        if not os.path.exists(input_file):
            logger.error(f"Input file '{input_file}' does not exist")
            exit_code = 1
            continue

        try:
            errors = lint_file(input_file, args.schema)

            if errors:
                exit_code = 1
                all_errors.extend([{
                    "file": input_file,
                    "line": error.line,
                    "column": error.column,
                    "message": error.message,
                    "level": "error"
                } for error in errors])
            else:
                print(f"✓ {input_file} - No linting errors found")

        except Exception:
            logger.exception(f"Error processing file: {input_file}")
            exit_code = 1

    if all_errors:
        output = {"annotations": all_errors}
        print(f"::error::{json.dumps(output)}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
