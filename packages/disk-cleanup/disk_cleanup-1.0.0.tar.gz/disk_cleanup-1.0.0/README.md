# Disk-Cleanup

Disk-Cleanup monitors disk usage, sends alerts to a Discord webhook when the available disk space falls below a specified threshold, and performs cleanup operations to free up space.

## Features

- Checks the available disk space on the root directory.
- Sends alerts to a specified Discord webhook.
- Performs cleanup operations using Docker and journal logs.
- Provides updated free space information after cleanup.

## Requirements

- Python 3.6+
- `curl` installed on the system.
- Docker installed and running (for docker cleanup operations).
- Unix based environment

## Installation

You can install the package via pip:

```
pip install disk-cleanup
```

## Usage

Run the script with the following arguments:

### Arguments

| Argument            | Required | Description                                                         |
| ------------------- | -------- | ------------------------------------------------------------------- |
| `--discord-webhook` | Yes      | The Discord webhook URL to send alerts.                             |
| `--threshold`       | Yes      | Disk space threshold in GB (e.g., `1G` for 1 GB).                   |
| `--environment`     | No       | The environment name to include in alerts (default: `sandbox-ovh`). |

### Example Command

```bash
disk-cleanup --discord-webhook https://discord.com/api/webhooks/XXX --threshold 1G --environment production
```

or add to crontab

```bash
* * * * * disk-cleanup --discord-webhook https://discord.com/api/webhooks/XXX --threshold 1G --environment production
```

### What It Does

1. Checks the available disk space on the root directory.
2. If the free space is below the specified threshold:
   - Sends a "Low Disk Space Warning" to the Discord webhook.
   - Runs cleanup commands to remove unnecessary files:
     - Removes unused Docker objects.
     - Vacuums old journal logs older than 10 days.
   - Sends a "Free Space Update" with the new free space value to the Discord webhook.

## Example Output

When disk space is low:

```json
{
  "username": " Disk Cleanup",
  "embeds": [
    {
      "title": "Low Disk Space Warning: production",
      "color": 16711680,
      "description": "Low Disk Space Warning: production has 0.95 GB disk left"
    }
  ]
}
```

After cleanup:

```json
{
  "username": " Disk Cleanup",
  "embeds": [
    {
      "title": "Free Space Update: production",
      "color": 65280,
      "description": "Free Space Update: production has 5.12 GB disk left"
    }
  ]
}
```

## Cleanup Commands

The following commands are used for cleanup:

- **Docker Cleanup:**
  ```bash
  docker system prune --all -f
  ```
- **Journal Logs Cleanup:**
  ```bash
  journalctl --vacuum-time=10d
  ```

## License

This project is licensed under the MIT License.

## Contributing

Feel free to submit feature ideas, issues or pull requests to enhance this tool.

---

If you find this tool helpful, please consider starring the repository!
