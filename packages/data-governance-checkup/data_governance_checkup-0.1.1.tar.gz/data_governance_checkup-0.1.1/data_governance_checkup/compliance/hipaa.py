class HIPAACompliance:
    @staticmethod
    def check(data):
        """
        Checks data for potential HIPAA violations.
        Example rules:
        1. Protected Health Information (PHI) should not be in plain text.
        2. Access logs must include timestamps and user actions.
        """
        violations = []
        if "PHI" in data and not data.get("PHI_encrypted", False):
            violations.append("PHI must be encrypted.")
        if "access_logs" in data:
            for log in data["access_logs"]:
                if not log.get("timestamp"):
                    violations.append("Access logs must include timestamps.")
                if not log.get("action"):
                    violations.append("Access logs must include user actions.")
        return violations
