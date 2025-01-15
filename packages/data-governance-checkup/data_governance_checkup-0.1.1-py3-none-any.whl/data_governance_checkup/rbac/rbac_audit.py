class RBACAudit:
    @staticmethod
    def audit(access_logs, roles):
        unauthorized_access = []
        for log in access_logs:
            user, resource = log['user'], log['resource']
            if resource not in roles.get(user, []):
                unauthorized_access.append(f"Unauthorized access by {user} to {resource}")
        return unauthorized_access
