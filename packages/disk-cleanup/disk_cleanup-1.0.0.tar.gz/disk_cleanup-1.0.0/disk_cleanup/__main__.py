import json
import subprocess
from argparse import ArgumentParser


def get_free_space():
    return (
        int(
            subprocess.check_output(
                "df --output=avail / | tail -n 1", shell=True
            )
            .decode()
            .strip()
        )
        / 1024
        / 1024
    )


def send_alert(
    webhook_url: str,
    environment: str,
    free_space: float,
    message_type: str,
    color: int,
):
    alert = {
        "username": "Disk Cleanup",
        "embeds": [
            {
                "title": f"{message_type}: {environment}",
                "color": color,
                "description": f"{message_type}: {environment} has {free_space:.2f} GB disk left",
            }
        ],
    }
    subprocess.run(
        f"curl -H 'Content-Type: application/json' -d '{json.dumps(alert)}' '{webhook_url}'",
        shell=True,
    )


def cleanup_disk():
    subprocess.run("docker system prune --all -f", shell=True)
    subprocess.run("journalctl --vacuum-time=10d", shell=True)


def main():
    parser = ArgumentParser(
        description="A cli utility that sends low disk warning notifications and cleanups."
    )
    parser.add_argument(
        "--discord-webhook",
        type=str,
        required=True,
        help="Discord webhook URL to send alerts.",
    )
    parser.add_argument(
        "--threshold",
        type=str,
        required=True,
        help="Disk space threshold in GB, e.g., '1G' for 1 GB.",
    )
    parser.add_argument(
        "--environment",
        type=str,
        default="sandbox-ovh",
        help="Environment name to include in alerts.",
    )

    args = parser.parse_args()

    webhook_url = args.discord_webhook
    environment = args.environment
    threshold = float(args.threshold.lower().rstrip("g"))

    initial_free_space = get_free_space()

    if initial_free_space < threshold:
        send_alert(
            webhook_url,
            environment,
            initial_free_space,
            "Low Disk Space Warning",
            16711680,
        )

        cleanup_disk()

        new_free_space = get_free_space()

        send_alert(
            webhook_url,
            environment,
            new_free_space,
            "Free Space Update",
            65280,
        )


if __name__ == "__main__":
    main()
