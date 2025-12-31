from typing import List, Dict

class MitreService:
    def __init__(self):
        # Basic mapping of keywords/commands to MITRE TTPs
        self.signatures = {
            "wget": {"id": "T1105", "name": "Ingress Tool Transfer"},
            "curl": {"id": "T1105", "name": "Ingress Tool Transfer"},
            "base64": {"id": "T1027", "name": "Obfuscated Files or Information"},
            "rm -rf": {"id": "T1485", "name": "Data Destruction"},
            "cat /etc/passwd": {"id": "T1003.008", "name": "OS Credential Dumping: /etc/passwd and /etc/shadow"},
            "whoami": {"id": "T1033", "name": "System Owner/User Discovery"},
            "id": {"id": "T1033", "name": "System Owner/User Discovery"},
            "ssh": {"id": "T1021.004", "name": "Remote Services: SSH"},
            "nc": {"id": "T1095", "name": "Non-Application Layer Protocol"},
            "ncat": {"id": "T1095", "name": "Non-Application Layer Protocol"},
            "bash -i": {"id": "T1059.004", "name": "Command and Scripting Interpreter: Unix Shell"},
            "chmod +x": {"id": "T1222.002", "name": "File and Directory Permissions Modification: Linux and Mac File and Directory Permissions Modification"},
        }

    def map_command(self, command: str) -> List[Dict[str, str]]:
        """
        Analyze a command and return a list of matched MITRE techniques.
        """
        matches = []
        for keyword, technique in self.signatures.items():
            if keyword in command:
                matches.append(technique)
        
        # Deduplicate matches
        unique_matches = []
        seen_ids = set()
        for m in matches:
            if m["id"] not in seen_ids:
                unique_matches.append(m)
                seen_ids.add(m["id"])
                
        return unique_matches

mitre_service = MitreService()
