import json


def approval_request(tool, args, untrusted_sources):
    lines = [f"Action: {tool}", "Arguments:"]
    lines.append(json.dumps(args, indent="  ", ensure_ascii=False))
    lines.append("Untrusted content in context when this was proposed:")
    lines.extend(f"  - {src}" for src in untrusted_sources)
    lines.append("Approve? [y/N]")
    return "\n".join(lines)


print(approval_request(
    "record_assessment",
    {
        "case": "example-case",
        "position": "contest",
        "reasoning": "Brief objection; no detailed rebuttal.",
    },
    ["petition.pdf (party-submitted)"],
))
