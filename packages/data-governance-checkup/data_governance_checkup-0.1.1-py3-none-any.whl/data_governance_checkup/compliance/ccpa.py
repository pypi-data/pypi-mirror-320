class CCPACompliance:
    @staticmethod
    def check(data):
        """
        Example rules for CCPA:
        1. Consumers must have the right to request data deletion.
        2. Data cannot be sold without explicit consent.
        """
        violations = []
        if data.get("data_sold", False) and not data.get("consumer_consent", False):
            violations.append("Data cannot be sold without explicit consumer consent.")
        if not data.get("data_deletion_request_handled", True):
            violations.append("Consumer data deletion requests must be handled.")
        return violations
