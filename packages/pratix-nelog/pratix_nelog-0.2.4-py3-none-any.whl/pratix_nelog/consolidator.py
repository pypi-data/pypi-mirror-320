import json

class LogConsolidator:
    @staticmethod
    def consolidate(log_data, log_type):
        consolidated = []
        for entry in log_data:
            if log_type == "csv":
                consolidated.append({
                    "timestamp": entry.get("timestamp", ""),
                    "ip_address": entry.get("ip", ""),
                    "action": entry.get("action", "")
                })
            elif log_type == "json":
                consolidated.append({
                    "timestamp": entry.get("time", ""),
                    "ip_address": entry.get("source_ip", ""),
                    "action": entry.get("event", "")
                })
        return consolidated

    @staticmethod
    def save_to_json(data, output_path):
        with open(output_path, 'w') as file:
            json.dump(data, file, indent=4)
