"""CLI for agent-output-schema-enforcer."""
import sys
import argparse
from .enforcer import OutputSchemaEnforcer


def main():
    parser = argparse.ArgumentParser(description="Agent Output Schema Enforcer CLI")
    parser.add_argument("--demo", action="store_true", help="Run schema repair demonstration")
    args = parser.parse_args()

    if args.demo:
        enforcer = OutputSchemaEnforcer()
        broken = "```json\n{\"task\": \"deploy_service\", \"retries\": 3,\n"
        print("Raw Malformed Text:\n", broken)

        res = enforcer.enforce_json(broken, required_fields=["task"])
        print(f"\nParse Result: Success={res.success} | Was Repaired={res.was_repaired}")
        print("Recovered JSON Data:", res.data)
    else:
        parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
