# Analysis and Evaluation of a Hybrid Error-Detection Scheme Combining CRC and Checksum for Low-Power IoT Links

## 1. Objective

This mini project simulates a small wireless IoT network in software. Sensor packets travel through an unreliable wireless channel where random transmission errors can occur.

The receiver tests three error-detection schemes:

1. 16-bit Checksum
2. CRC-16
3. Hybrid CRC-16 + Checksum

The project compares their error-detection accuracy, missed errors, processing time, and communication overhead.

No physical IoT hardware is required.

---

## 2. Problem Statement

Wireless IoT links can be affected by noise and interference. A corrupted sensor packet can contain incorrect temperature, humidity, battery, or payload information.

An error-detection mechanism allows the receiver to identify corrupted packets.

This project evaluates whether combining two different error-detection techniques, CRC and checksum, can provide stronger validation than using either one alone.

---

## 3. Technologies Used

- Python 3
- Python standard library
- Matplotlib for graphs
- Command Prompt on Windows
- Software-based wireless testbed simulation

---

## 4. System Architecture

```text
Simulated Sensor
      |
      v
Packet Generator
      |
      v
Checksum + CRC added
      |
      v
Simulated Wireless Channel
      |
      | Random transmission errors
      v
Possibly Corrupted Packet
      |
      v
Receiver
  /     |      \
Checksum CRC   Hybrid
  \     |      /
      v
Detection Results
      |
      v
Performance Analysis
      |
      v
Tables + CSV + Graphs
```

---

## 5. Sensor Packet

Each simulated packet contains:

- Packet ID
- Sensor ID
- Temperature
- Humidity
- Battery level
- Payload/data

The default experiment generates 1000 packets.

The simulator runs five trials with different seeds by default. This makes results reproducible as a group of trials while giving each trial different generated packets and channel errors.

---

## 6. Checksum

The project uses a 16-bit Internet-style one's-complement checksum.

At the sender:

```text
Packet data
    |
    v
16-bit checksum calculation
    |
    v
Checksum attached/transmitted
```

At the receiver:

```text
Received packet
    |
    v
Recalculate checksum
    |
    v
Compare with transmitted checksum
```

If the values differ, the packet is considered corrupted.

### Why checksum?

A checksum is simple and has low computational overhead. It is useful when a lightweight error-detection method is desired.

---

## 7. CRC-16

CRC stands for Cyclic Redundancy Check.

This project uses CRC-16-CCITT with polynomial:

```text
0x1021
```

The sender calculates a CRC value from the packet data.

The receiver calculates the CRC again from the received data.

If the values do not match, the receiver detects an error.

CRC is generally stronger than a simple checksum for many burst and bit-error patterns.

---

## 8. Hybrid CRC + Checksum

The Hybrid scheme calculates both:

```text
Checksum = Checksum(Packet)
CRC      = CRC-16(Packet)
```

The receiver accepts the packet as valid only when both checks pass.

Therefore:

```text
Checksum PASS + CRC PASS = Valid
Checksum FAIL or CRC FAIL = Corrupted/Rejected
```

The Hybrid scheme adds 32 error-detection bits:

```text
16 checksum bits + 16 CRC bits = 32 bits
```

This is more redundancy than either individual method.

---

## 9. Wireless Channel Simulation

The wireless channel is software only.

It does not model radio waves or physical RF behavior.

Instead, it randomly changes bits in packet data according to a selected error probability.

Default error rates:

- 0%
- 1%
- 5%
- 10%
- 20%

The simulator supports:

- Single-bit errors
- Multiple-bit errors
- Burst errors
- A checksum-cancelling stress pattern (the same bit is flipped in two 16-bit words with opposite bit values), designed to demonstrate a known limitation of a simple 16-bit one's-complement checksum.

Within each trial, the same corrupted transmissions are tested by all three schemes so the comparison is fair. The default experiment aggregates counts across five independently seeded trials. The checksum-cancelling stress pattern is deliberately included and clearly labeled because purely random errors may not expose checksum weaknesses in a small test.

---

## 10. Experimental Parameters

Default packet count:

```text
1000 packets
```

Error rates:

```text
0%, 1%, 5%, 10%, 20%
```

Schemes:

```text
Checksum
CRC-16
Hybrid CRC + Checksum
```

For every experiment the program calculates:

- Total packets sent
- Total packets corrupted
- Total corrupted packets detected
- Total corrupted packets missed
- Detection accuracy
- Packet acceptance/delivery rate
- Extra error-detection bits
- Percentage communication overhead
- Approximate processing time

---

## 11. Detection Accuracy

The program uses:

```text
Detection Accuracy =
Detected Corrupted Packets / Total Corrupted Packets × 100
```

At 0% error rate, no packets are corrupted, so detection accuracy is reported as N/A because there are no corrupted packets against which to measure detection. The graph may omit that point.

---

## 12. Low-Power IoT Overhead

The project intentionally uses a simple overhead model instead of complicated physical energy modelling.

### Extra transmitted bits

| Scheme | Extra Bits |
|---|---:|
| Checksum | 16 |
| CRC-16 | 16 |
| Hybrid | 32 |

The Hybrid scheme therefore sends twice as many error-detection bits as either individual scheme.

This is important for low-power IoT because additional bits require additional communication.

The project also measures processing time as a practical software-level indicator of computational overhead.

This is not a physical battery-energy measurement.

---

## 13. Output Files

After the default simulation, the `results` folder contains:

```text
accuracy_comparison.png
undetected_errors.png
scheme_comparison.png
processing_overhead.png
communication_overhead.png
simulation_results.csv
```

The CSV contains the actual calculated experimental results.

---

## 14. How to Run on Windows

### Step 1: Install Python

Install Python 3 from the official Python website if it is not already installed.

During installation, enable:

```text
Add Python to PATH
```

### Step 2: Open Command Prompt

Go to the project folder:

```bat
cd path\to\hybrid_error_detection_iot
```

For example:

```bat
cd Desktop\hybrid_error_detection_iot
```

### Step 3: Install the only external package

```bat
python -m pip install -r requirements.txt
```

### Step 4: Run

```bat
python main.py
```

### Step 5: Select option 1

```text
1. Run default simulation
```

The program automatically runs all five error rates and all three schemes.

---

## 15. Menu

```text
1. Run default simulation
2. Run simulation with custom error rate
3. Compare Checksum vs CRC vs Hybrid
4. Generate graphs
5. Exit
```

Option 1 is the recommended demonstration.

---

## 16. Example Terminal Flow

```text
[1] Packet Generation
Generated 1000 simulated sensor packets.

[2] Wireless Transmission - Error Rate: 5%
Packets transmitted: 1000
Packets corrupted by channel: ...

[3] Error Injection
[4] Checksum Verification
[5] CRC Verification
[6] Hybrid Verification
[7] Performance Analysis

[8] Final Comparison
```

The exact numerical values are generated by the program and are not hardcoded.

---

## 17. Important Note About "Packet Delivery"

This project does not implement a real retransmission protocol.

Therefore, packet acceptance rate means the percentage of packets that the receiver accepts after validation. It is not a physical wireless delivery probability.

If a corrupted packet is missed by an error-detection scheme, the receiver may accept it. This is intentionally useful for evaluating the error-detection technique.

---

## 18. Viva Questions and Answers

### Q1. What is the main objective of this project?

To compare Checksum, CRC-16, and a Hybrid CRC + Checksum error-detection scheme over a simulated unreliable wireless IoT channel.

### Q2. Is this a real wireless network?

No. It is a software simulation of a wireless IoT link.

### Q3. Why did you use simulation?

It allows the error-detection algorithms to be evaluated without requiring Arduino, Raspberry Pi, radio modules, or other hardware.

### Q4. What is a checksum?

A checksum is a value calculated from packet data and transmitted with the packet. The receiver recalculates it to identify possible corruption.

### Q5. What is CRC?

CRC stands for Cyclic Redundancy Check. It uses polynomial division over binary data to produce a check value.

### Q6. Which CRC is used?

CRC-16-CCITT using polynomial `0x1021`.

### Q7. What is the Hybrid scheme?

The sender calculates both checksum and CRC. The receiver accepts the packet only if both checks pass.

### Q8. Why use both?

They provide two different error-detection calculations. The hybrid approach adds another validation condition and can reduce the chance of an error pattern escaping detection.

### Q9. What is the disadvantage of the Hybrid method?

It adds more redundancy and requires more computation than using only one method.

### Q10. Why is overhead important in IoT?

IoT devices can have limited battery power and communication bandwidth. Sending extra bits consumes additional communication resources.

### Q11. What types of errors are simulated?

Single-bit, multiple-bit, and burst errors.

### Q12. What are the default error rates?

0%, 1%, 5%, 10%, and 20%.

### Q13. Why are the same corrupted packets tested by all schemes?

To make the comparison fair. Every scheme faces the same simulated transmission conditions.

### Q14. What does detection accuracy mean?

It is the percentage of corrupted packets correctly identified by an error-detection scheme.

### Q15. What does an undetected error mean?

It is a packet that was actually corrupted by the channel but passed the receiver's error-detection check.

### Q16. Why is CRC usually considered strong for burst errors?

CRC is designed using polynomial arithmetic and has strong properties for detecting many common burst-error patterns.

### Q17. Does this project perform encryption?

No. Error detection and encryption are different. This project only identifies accidental transmission corruption.

### Q18. Does the project correct errors?

No. It detects errors. Error correction or retransmission would be a separate feature.

### Q19. Why use a fixed random seed?

It makes the experiment reproducible. Running the same configuration can produce the same simulated packet/error sequence.

### Q20. What is the main trade-off?

Higher reliability can require more redundancy and processing. In low-power IoT systems, reliability must be balanced against communication and computation cost.

---

## 19. Files

```text
main.py
    Menu and program entry point.

crc.py
    CRC-16 calculation and verification.

checksum.py
    16-bit checksum calculation and verification.

wireless_channel.py
    Simulated unreliable wireless channel and error injection.

simulation.py
    Packet generation and experiments.

analysis.py
    Result tables, CSV output, calculations, and graphs.

requirements.txt
    Required external Python package.

README.md
    Project documentation and viva preparation.

results/
    Generated graphs and CSV results.
```

---

## 20. Conclusion

This project demonstrates that error-detection performance can be evaluated without physical IoT hardware.

Checksum provides a lightweight method with 16 bits of redundancy. CRC-16 also uses 16 bits but generally provides strong detection for common transmission-error patterns. The Hybrid scheme combines both methods and requires both validations to pass, providing additional validation at the cost of 32 redundancy bits and extra processing.

The final experimental conclusion should be based on the actual calculated results shown by the program rather than assumed numerical values.


## 13. Important interpretation and limitations

- This is a software simulation, not a physical wireless testbed.
- The configured error rate is the probability that a packet is corrupted, not the percentage of individual bits flipped.
- The checksum-cancelling pattern is a deliberate stress test, not a claim that 10% of real-world errors have this shape. Its purpose is to show why checksum alone can miss some patterns.
- The results depend on the generated packets, selected error patterns, and number of trials. Do not claim that any scheme detects every possible error.
- Processing time is measured by Python's timer and can vary by computer and run. It is not a direct measurement of battery power.
- Detection accuracy is calculated only over packets that were actually corrupted. If none were corrupted, the result is N/A.

## 14. Run the project

Install Python 3.10 or later, then from this folder run:

```bash
pip install -r requirements.txt
python main.py
```

Choose option 1 for the default multi-trial experiment. CSV results and graphs are saved in the `results` folder.


## Version note
This version includes independent repeated trials, a checksum-cancelling stress-error pattern, a correct N/A value when no corrupted packets occur, and fixes for the results-table formatting and results-path handling.


### CRC vs Hybrid stress test
This version includes a controlled CRC-cancelling error pattern. It creates a corruption that leaves CRC-16 unchanged while changing the checksum, allowing the Hybrid scheme to demonstrate an additional detection layer. This is a deliberate stress-test pattern, not a claim that CRC normally fails on random errors.
