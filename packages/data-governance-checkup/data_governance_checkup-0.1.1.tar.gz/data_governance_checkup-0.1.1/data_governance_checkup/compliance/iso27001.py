class ISO27001Compliance:
    @staticmethod
    def check(data):
        """
        Checks data for potential ISO 27001 violations.
        Example rules:
        1. Access to sensitive data must be logged.
        2. Backup processes must be in place.
        3. Roles must be defined and access control policies enforced.
        """
        violations = []
        if "sensitive_data_access" in data:
            for access in data["sensitive_data_access"]:
                if not access.get("logged", False):
                    violations.append(f"Sensitive data access by {access['user']} is not logged.")
        if not data.get("backup_enabled", False):
            violations.append("Backup processes must be enabled.")
        if "roles" in data:
            for user, permissions in data["roles"].items():
                if not permissions:
                    violations.append(f"Role for user {user} is not defined.")
        return violations
