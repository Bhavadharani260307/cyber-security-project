"""
Sample Data Generator for AI-Based Network Intrusion Detection System
Generates synthetic CICIDS2017-style flow feature dataset for instant training & testing.
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

# Directory setup
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "ml" / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / "sample_traffic_dataset.csv"

# Label categories
LABEL_CATEGORIES = [
    "BENIGN",
    "DoS",
    "DDoS",
    "Port Scan",
    "Brute Force",
    "Web Attack",
    "Bot",
    "Infiltration",
]


def generate_synthetic_dataset(num_samples=2500, random_seed=42):
    """Generates synthetic network flow features matching CICIDS2017 schema"""
    np.random.seed(random_seed)
    samples_per_class = num_samples // len(LABEL_CATEGORIES)

    records = []

    for label in LABEL_CATEGORIES:
        for _ in range(samples_per_class):
            src_ip = f"192.168.1.{np.random.randint(2, 254)}"
            dest_ip = f"10.0.0.{np.random.randint(2, 254)}"
            protocol = np.random.choice([6, 17, 1], p=[0.75, 0.20, 0.05])  # TCP, UDP, ICMP

            if label == "BENIGN":
                dest_port = np.random.choice([80, 443, 53, 22, 8080])
                src_port = np.random.randint(1024, 65535)
                flow_duration = np.random.exponential(scale=50000)
                tot_fwd_pkts = np.random.randint(1, 30)
                tot_bwd_pkts = np.random.randint(1, 30)
                fwd_pkt_len_max = np.random.randint(40, 1500)
                bwd_pkt_len_mean = np.random.uniform(40, 1200)
                flow_bytes_s = np.random.uniform(100, 500000)
                flow_pkts_s = np.random.uniform(2, 1000)

            elif label == "DoS":
                dest_port = 80
                src_port = np.random.randint(1024, 65535)
                flow_duration = np.random.uniform(500, 5000)
                tot_fwd_pkts = np.random.randint(100, 2000)
                tot_bwd_pkts = np.random.randint(0, 5)
                fwd_pkt_len_max = np.random.randint(500, 1460)
                bwd_pkt_len_mean = np.random.uniform(0, 50)
                flow_bytes_s = np.random.uniform(500000, 5000000)
                flow_pkts_s = np.random.uniform(2000, 50000)

            elif label == "DDoS":
                dest_port = 80
                src_port = np.random.randint(1024, 65535)
                flow_duration = np.random.uniform(100, 2000)
                tot_fwd_pkts = np.random.randint(200, 5000)
                tot_bwd_pkts = 0
                fwd_pkt_len_max = np.random.randint(1000, 1460)
                bwd_pkt_len_mean = 0.0
                flow_bytes_s = np.random.uniform(1000000, 10000000)
                flow_pkts_s = np.random.uniform(5000, 100000)

            elif label == "Port Scan":
                dest_port = np.random.randint(1, 1024)
                src_port = np.random.randint(40000, 65535)
                flow_duration = np.random.uniform(10, 500)
                tot_fwd_pkts = np.random.randint(1, 3)
                tot_bwd_pkts = np.random.randint(0, 2)
                fwd_pkt_len_max = np.random.randint(40, 64)
                bwd_pkt_len_mean = np.random.uniform(0, 40)
                flow_bytes_s = np.random.uniform(10, 2000)
                flow_pkts_s = np.random.uniform(10, 500)

            elif label == "Brute Force":
                dest_port = np.random.choice([22, 21, 3389])
                src_port = np.random.randint(1024, 65535)
                flow_duration = np.random.uniform(1000, 10000)
                tot_fwd_pkts = np.random.randint(10, 100)
                tot_bwd_pkts = np.random.randint(10, 100)
                fwd_pkt_len_max = np.random.randint(100, 500)
                bwd_pkt_len_mean = np.random.uniform(100, 400)
                flow_bytes_s = np.random.uniform(5000, 100000)
                flow_pkts_s = np.random.uniform(50, 500)

            elif label == "Web Attack":
                dest_port = 80
                src_port = np.random.randint(1024, 65535)
                flow_duration = np.random.uniform(2000, 30000)
                tot_fwd_pkts = np.random.randint(5, 50)
                tot_bwd_pkts = np.random.randint(5, 50)
                fwd_pkt_len_max = np.random.randint(800, 1500)
                bwd_pkt_len_mean = np.random.uniform(200, 1000)
                flow_bytes_s = np.random.uniform(2000, 80000)
                flow_pkts_s = np.random.uniform(10, 200)

            elif label == "Bot":
                dest_port = np.random.choice([8080, 6667, 80])
                src_port = np.random.randint(1024, 65535)
                flow_duration = np.random.uniform(10000, 120000)
                tot_fwd_pkts = np.random.randint(20, 200)
                tot_bwd_pkts = np.random.randint(20, 200)
                fwd_pkt_len_max = np.random.randint(100, 600)
                bwd_pkt_len_mean = np.random.uniform(100, 500)
                flow_bytes_s = np.random.uniform(1000, 30000)
                flow_pkts_s = np.random.uniform(5, 50)

            else:  # Infiltration
                dest_port = np.random.choice([443, 80])
                src_port = np.random.randint(1024, 65535)
                flow_duration = np.random.uniform(50000, 300000)
                tot_fwd_pkts = np.random.randint(50, 500)
                tot_bwd_pkts = np.random.randint(50, 500)
                fwd_pkt_len_max = np.random.randint(500, 1400)
                bwd_pkt_len_mean = np.random.uniform(300, 1200)
                flow_bytes_s = np.random.uniform(5000, 100000)
                flow_pkts_s = np.random.uniform(1, 20)

            records.append(
                {
                    "Source IP": src_ip,
                    "Destination IP": dest_ip,
                    "Protocol": "TCP" if protocol == 6 else ("UDP" if protocol == 17 else "ICMP"),
                    "Source Port": src_port,
                    "Destination Port": dest_port,
                    "Flow Duration": max(1.0, flow_duration),
                    "Total Fwd Packets": max(1, tot_fwd_pkts),
                    "Total Backward Packets": max(0, tot_bwd_pkts),
                    "Fwd Packet Length Max": max(0.0, fwd_pkt_len_max),
                    "Bwd Packet Length Mean": max(0.0, bwd_pkt_len_mean),
                    "Flow Bytes/s": max(0.0, flow_bytes_s),
                    "Flow Packets/s": max(0.0, flow_pkts_s),
                    "Label": label,
                }
            )

    df = pd.DataFrame(records)
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[+] Successfully generated {len(df)} synthetic traffic flow samples at {OUTPUT_FILE}")
    return OUTPUT_FILE


if __name__ == "__main__":
    generate_synthetic_dataset()
