def sample_data():
    return {
        "personal_data": "John Doe",
        "access_logs": [
            {"user": "alice", "resource": "file1"},
            {"user": "bob", "resource": "file2"}
        ],
        "roles": {
            "alice": ["file1"],
            "bob": []
        },
    }
