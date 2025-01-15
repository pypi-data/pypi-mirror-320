class DataMasking:
    @staticmethod
    def mask_data(data, fields):
        for field in fields:
            if field in data:
                data[field] = "*****"
        return data
