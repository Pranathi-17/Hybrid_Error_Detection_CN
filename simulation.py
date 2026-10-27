import random
import time
from checksum import calculate_checksum, verify_checksum
from crc import calculate_crc, verify_crc
from wireless_channel import WirelessChannel

PACKET_COUNT = 1000
DEFAULT_ERROR_RATES = [0, 1, 5, 10, 20]
BASE_SEED = 20261025
REPEATED_RUNS = 5
SCHEMES = ["Checksum", "CRC-16", "Hybrid"]


class Packet:
    def __init__(self, packet_id, sensor_id, temperature, humidity, battery, payload):
        self.packet_id = packet_id
        self.sensor_id = sensor_id
        self.temperature = temperature
        self.humidity = humidity
        self.battery = battery
        self.payload = payload

    def to_bytes(self):
        text = (f"{self.packet_id}|{self.sensor_id}|{self.temperature:.2f}|"
                f"{self.humidity:.2f}|{self.battery:.2f}|{self.payload}")
        return text.encode("utf-8")


def generate_packets(count=PACKET_COUNT, seed=BASE_SEED):
    rng = random.Random(seed)
    packets = []
    for i in range(1, count + 1):
        packets.append(Packet(
            i, f"SENSOR-{rng.randint(1, 25):02d}",
            round(rng.uniform(18, 38), 2), round(rng.uniform(30, 90), 2),
            round(rng.uniform(20, 100), 2),
            f"TEMP={rng.randint(1800, 3800)};HUM={rng.randint(3000, 9000)}"
        ))
    return packets


def _create_transmissions(packets, error_rate, seed):
    channel = WirelessChannel(error_rate=error_rate, seed=seed)
    transmissions = []
    for packet in packets:
        original = packet.to_bytes()
        received, corrupted, error_type = channel.transmit(original)
        transmissions.append((original, received, corrupted, error_type))
    return transmissions


def _scheme_result(scheme, error_rate, transmissions, run_number):
    start = time.perf_counter()
    sent = len(transmissions)
    corrupted = detected = 0
    total_bytes = 0
    operations = 0
    for original, received, was_corrupted, _ in transmissions:
        total_bytes += len(original)
        corrupted += int(was_corrupted)
        if scheme == "Checksum":
            valid = verify_checksum(received, calculate_checksum(original))
            operations += len(original) * 2
            extra_bits = 16
        elif scheme == "CRC-16":
            valid = verify_crc(received, calculate_crc(original))
            operations += len(original) * 8
            extra_bits = 16
        else:
            valid = (verify_checksum(received, calculate_checksum(original)) and
                     verify_crc(received, calculate_crc(original)))
            operations += len(original) * 10
            extra_bits = 32
        if was_corrupted and not valid:
            detected += 1
    elapsed_ms = (time.perf_counter() - start) * 1000
    missed = corrupted - detected
    accuracy = (detected / corrupted * 100) if corrupted else None
    accepted = sent - detected
    avg_packet_bits = (total_bytes * 8 / sent) if sent else 0
    return {
        "scheme": scheme, "error_rate": error_rate, "run": run_number,
        "sent": sent, "corrupted": corrupted, "detected": detected,
        "missed": missed, "accuracy": accuracy, "accepted": accepted,
        "delivery_rate": accepted / sent * 100 if sent else 0,
        "extra_bits": extra_bits,
        "overhead_percent": extra_bits / avg_packet_bits * 100 if avg_packet_bits else 0,
        "processing_time_ms": elapsed_ms, "processing_operations": operations,
    }


def run_experiment(error_rates=None, packet_count=PACKET_COUNT, repeated_runs=REPEATED_RUNS):
    if error_rates is None:
        error_rates = DEFAULT_ERROR_RATES
    if repeated_runs < 1:
        raise ValueError("repeated_runs must be at least 1")
    print("\n[1] Packet Generation")
    print(f"Each trial uses {packet_count} packets; independent trials: {repeated_runs}.")
    all_rows = []
    for rate in error_rates:
        run_rows = []
        for run_number in range(1, repeated_runs + 1):
            seed = BASE_SEED + run_number * 100003 + int(rate * 1000)
            packets = generate_packets(packet_count, seed=seed)
            transmissions = _create_transmissions(packets, rate / 100, seed + 17)
            actual_corrupted = sum(int(row[2]) for row in transmissions)
            print(f"Error rate {rate:g}% | trial {run_number}/{repeated_runs}: "
                  f"{packet_count} sent, {actual_corrupted} corrupted")
            for scheme in SCHEMES:
                run_rows.append(_scheme_result(scheme, rate, transmissions, run_number))
        # Pool packet counts across independent trials; report weighted accuracy.
        for scheme in SCHEMES:
            rows = [r for r in run_rows if r["scheme"] == scheme]
            sent = sum(r["sent"] for r in rows)
            corrupted = sum(r["corrupted"] for r in rows)
            detected = sum(r["detected"] for r in rows)
            missed = corrupted - detected
            accuracy = detected / corrupted * 100 if corrupted else None
            all_rows.append({
                "scheme": scheme, "error_rate": rate, "runs": repeated_runs,
                "sent": sent, "corrupted": corrupted, "detected": detected,
                "missed": missed, "accuracy": accuracy,
                "accepted": sent - detected,
                "delivery_rate": (sent - detected) / sent * 100 if sent else 0,
                "extra_bits": rows[0]["extra_bits"],
                "overhead_percent": sum(r["overhead_percent"] for r in rows) / len(rows),
                "processing_time_ms": sum(r["processing_time_ms"] for r in rows) / len(rows),
                "processing_operations": sum(r["processing_operations"] for r in rows),
            })
    print("\n[Final comparison uses pooled counts across independent trials.]\n")
    return all_rows


def run_default_experiment():
    return run_experiment(DEFAULT_ERROR_RATES, PACKET_COUNT)


def run_custom_experiment(error_rate_percent):
    return run_experiment([error_rate_percent], PACKET_COUNT)
