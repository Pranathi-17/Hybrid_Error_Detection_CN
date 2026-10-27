import csv
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _ensure_results_dir():
    RESULTS_DIR.mkdir(exist_ok=True)


def print_results_table(results):
    if not results:
        print("No results available.")
        return

    print("\n" + "=" * 118)
    print("FINAL RESULTS")
    print("=" * 118)
    header = (
        f"{'Scheme':<12}{'Error %':>10}{'Sent':>8}{'Corrupt':>10}"
        f"{'Detected':>10}{'Missed':>9}{'Accuracy':>12}"
        f"{'Accepted':>10}{'Time(ms)':>12}"
    )
    print(header)
    print("-" * 118)

    for r in results:
        accuracy_text = f"{r['accuracy']:.2f}%" if r["accuracy"] is not None else "N/A"
        print(
            f"{r['scheme']:<12}{r['error_rate']:>10.1f}"
            f"{r['sent']:>8}{r['corrupted']:>10}{r['detected']:>10}"
            f"{r['missed']:>9}{accuracy_text:>12}"
            f"{r['accepted']:>10}{r['processing_time_ms']:>11.3f}"
        )

    print("-" * 118)
    print("Detection accuracy = detected corrupted packets / total corrupted packets.")
    print("N/A means no corrupted packets occurred, so accuracy cannot be measured.")
    print("Accepted packets include both clean packets and corrupted packets not detected.")


def save_results_csv(results):
    _ensure_results_dir()
    path = RESULTS_DIR / "simulation_results.csv"

    fields = [
        "scheme", "error_rate", "runs", "sent", "corrupted", "detected", "missed",
        "accuracy", "accepted", "delivery_rate", "extra_bits",
        "overhead_percent", "processing_time_ms", "processing_operations"
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    return path


def load_results_csv(path):
    results = []
    with Path(path).open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in row:
                if key == "accuracy":
                    row[key] = float(row[key]) if row[key].strip() else None
                elif key in {
                    "error_rate", "delivery_rate",
                    "overhead_percent", "processing_time_ms"
                }:
                    row[key] = float(row[key])
                elif key in {
                    "runs", "sent", "corrupted", "detected", "missed",
                    "accepted", "extra_bits", "processing_operations"
                }:
                    row[key] = int(float(row[key]))
            results.append(row)
    return results


def _group(results, scheme):
    return [r for r in results if r["scheme"] == scheme]


def generate_all_graphs(results):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed. Run: pip install -r requirements.txt")
        return

    _ensure_results_dir()

    schemes = ["Checksum", "CRC-16", "Hybrid"]
    labels = ["Checksum", "CRC-16", "Hybrid"]

    # Graph 1: Accuracy
    plt.figure(figsize=(9, 5))
    for scheme, label in zip(schemes, labels):
        data = _group(results, scheme)
        plt.plot(
            [r["error_rate"] for r in data],
            [r["accuracy"] if r["accuracy"] is not None else float("nan") for r in data],
            marker="o",
            label=label
        )
    plt.xlabel("Wireless Error Rate (%)")
    plt.ylabel("Detection Accuracy (%)")
    plt.title("Error Rate vs Error Detection Accuracy")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "accuracy_comparison.png", dpi=150)
    plt.close()

    # Graph 2: Undetected errors
    plt.figure(figsize=(9, 5))
    for scheme, label in zip(schemes, labels):
        data = _group(results, scheme)
        plt.plot(
            [r["error_rate"] for r in data],
            [r["missed"] for r in data],
            marker="o",
            label=label
        )
    plt.xlabel("Wireless Error Rate (%)")
    plt.ylabel("Undetected Corrupted Packets")
    plt.title("Error Rate vs Undetected Errors")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "undetected_errors.png", dpi=150)
    plt.close()

    # Graph 3: Scheme comparison at each error rate
    error_rates = sorted(set(r["error_rate"] for r in results))
    x = list(range(len(error_rates)))
    width = 0.25

    plt.figure(figsize=(10, 5))
    for index, scheme in enumerate(schemes):
        values = []
        for rate in error_rates:
            match = next(
                r for r in results
                if r["scheme"] == scheme and r["error_rate"] == rate
            )
            values.append(match["accuracy"] if match["accuracy"] is not None else 0)
        positions = [p + (index - 1) * width for p in x]
        plt.bar(positions, values, width=width, label=scheme)

    plt.xticks(x, [f"{rate:g}%" for rate in error_rates])
    plt.xlabel("Wireless Error Rate")
    plt.ylabel("Detection Accuracy (%)")
    plt.title("Checksum vs CRC-16 vs Hybrid")
    plt.ylim(0, 105)
    plt.grid(True, axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "scheme_comparison.png", dpi=150)
    plt.close()

    # Graph 4: Processing overhead
    latest_rate = max(error_rates)
    latest = [
        next(
            r for r in results
            if r["scheme"] == scheme and r["error_rate"] == latest_rate
        )
        for scheme in schemes
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(
        [r["scheme"] for r in latest],
        [r["processing_time_ms"] for r in latest]
    )
    plt.xlabel("Scheme")
    plt.ylabel("Processing Time (ms)")
    plt.title(f"Processing Time at {latest_rate:g}% Error Rate")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "processing_overhead.png", dpi=150)
    plt.close()

    # Extra useful graph: redundancy
    plt.figure(figsize=(8, 5))
    plt.bar(
        [r["scheme"] for r in latest],
        [r["extra_bits"] for r in latest]
    )
    plt.xlabel("Scheme")
    plt.ylabel("Extra Error-Detection Bits")
    plt.title("Communication Redundancy")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "communication_overhead.png", dpi=150)
    plt.close()

    print("Generated:")
    print("  results/accuracy_comparison.png")
    print("  results/undetected_errors.png")
    print("  results/scheme_comparison.png")
    print("  results/processing_overhead.png")
    print("  results/communication_overhead.png")


def print_conclusion(results):
    if not results:
        return

    print("\nCONCLUSION")
    print("-" * 72)

    schemes = ["Checksum", "CRC-16", "Hybrid"]
    average_accuracy = {}

    for scheme in schemes:
        data = _group(results, scheme)
        measured = [r["accuracy"] for r in data if r["accuracy"] is not None]
        average_accuracy[scheme] = sum(measured) / len(measured) if measured else 0

    best = max(average_accuracy, key=average_accuracy.get)

    print(
        f"Across the tested error rates, {best} achieved the highest "
        f"average detection accuracy ({average_accuracy[best]:.2f}%)."
    )

    print(
        f"Checksum adds 16 detection bits, CRC-16 adds 16 bits, and "
        f"the Hybrid scheme adds 32 bits."
    )

    if best == "Hybrid":
        print(
            "The Hybrid scheme gave the strongest validation in this "
            "simulation because a packet must pass both checksum and CRC."
        )
    else:
        print(
            "The Hybrid scheme provides an additional independent validation "
            "check, although its measured advantage depends on the error patterns."
        )

    print(
        "The trade-off is that stronger validation increases redundancy and "
        "requires additional processing, which matters in low-power IoT devices."
    )
