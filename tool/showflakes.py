import time
import threading

class SnowflakeIdGenerator:
    def __init__(self, datacenter_id=1, worker_id=1):
        self.twepoch = 1288834974657
        self.datacenter_id_bits = 5
        self.worker_id_bits = 5
        self.sequence_bits = 12

        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        if not (0 <= datacenter_id <= self.max_datacenter_id):
            raise ValueError("datacenter_id can't be greater than %d or less than 0" % self.max_datacenter_id)
        if not (0 <= worker_id <= self.max_worker_id):
            raise ValueError("worker_id can't be greater than %d or less than 0" % self.max_worker_id)

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1

    def _til_next_millis(self, last_timestamp):
        timestamp = int(time.time() * 1000)
        while timestamp <= last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp

    def next_id(self):
        with threading.Lock():
            timestamp = int(time.time() * 1000)
            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate id for %d milliseconds" % (self.last_timestamp - timestamp))
            if self.last_timestamp == timestamp:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                if self.sequence == 0:
                    timestamp = self._til_next_millis(self.last_timestamp)
            else:
                self.sequence = 0
            self.last_timestamp = timestamp
            return ((timestamp - self.twepoch) << (self.datacenter_id_bits + self.worker_id_bits + self.sequence_bits)) | \
                   ((self.datacenter_id << (self.worker_id_bits + self.sequence_bits)) | \
                    (self.worker_id << self.sequence_bits) | self.sequence)
if __name__=="__mian__":
    # 使用示例
    generator = SnowflakeIdGenerator()
    snowflake_id = generator.next_id()
    print(snowflake_id)