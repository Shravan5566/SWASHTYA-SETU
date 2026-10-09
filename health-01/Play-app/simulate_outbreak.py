"""
simulate_outbreak.py — Interactive Disease Outbreak Simulator for Hackathon Demo

Usage in a separate terminal while your Flask app is running:
    python simulate_outbreak.py

Features:
1. Live Outbreak Simulation:
   - Starts at normal baseline (e.g. Katraj Dengue = 3 cases)
   - Rapidly climbs (12 -> 28 -> 55 cases) triggering a 2-sigma HIGH SEVERITY outbreak alert
   - Holds peak so you can refresh the Public Health Surveillance Dashboard
   - Simulates intervention & recovery (drops back down to normal: 24 -> 10 -> 4 cases)
2. Manual Spike Trigger:
   - Immediately sets an outbreak spike so judges can inspect the Trend Alerts panel
3. Reset to Baseline:
   - Restores the clean seed data instantly
"""

import sys
import time

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from app import create_app
from app.extensions import db
from app.models.stats import Stats

# Color formatting for terminal
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    print(f"\n{CYAN}{BOLD}" + "=" * 65)
    print("   [+] SWASTHYA SETU -- LIVE DISEASE OUTBREAK SIMULATOR")
    print("   Pune Municipal Epidemiological Surveillance Engine")
    print("=" * 65 + f"{RESET}\n")


def update_stat_count(app, area: str, condition: str, time_bucket: str, new_count: int):
    """Update or create a Stats row in the active database."""
    with app.app_context():
        stat = Stats.query.filter_by(
            area=area,
            condition=condition,
            time_bucket=time_bucket
        ).first()

        if stat:
            stat.count = new_count
        else:
            stat = Stats(area=area, condition=condition, time_bucket=time_bucket, count=new_count)
            db.session.add(stat)

        db.session.commit()


def run_live_simulation(app, area="Katraj (Ward C)", condition="Dengue", time_bucket="2026-W38"):
    """
    Run an animated live cycle:
    Normal -> Escalating Outbreak -> High Severity Peak -> Municipal Intervention -> Normalized
    """
    print(f"\n{BOLD}[*] Launching Live Outbreak Simulation for:{RESET}")
    print(f"    Region   : {YELLOW}{area}{RESET}")
    print(f"    Pathogen : {YELLOW}{condition}{RESET}")
    print(f"    Bucket   : {YELLOW}{time_bucket}{RESET}\n")

    # Simulation stages: (count, stage_name, color, sleep_seconds)
    stages = [
        (3,  "[NORMAL] Phase 1: Baseline Cohort (Suppressed Under MIN_GROUP_SIZE < 5)", GREEN, 3),
        (8,  "[ALERT]  Phase 2: Mild Influx Detected (Count = 8)", YELLOW, 3),
        (19, "[WARN]   Phase 3: Outbreak Threshold Breached (Count = 19, Alert Triggered)", YELLOW, 3),
        (37, "[SPIKE]  Phase 4: Rapid Outbreak Escalation (Count = 37 -- SEVERITY: HIGH)", RED, 3),
        (54, "[PEAK]   Phase 5: PEAK EPIDEMIC WAVE (Count = 54 -- 2-Sigma Outbreak Detected!)", RED, 7),
        (28, "[ACTION] Phase 6: PMC Municipal Intervention (Fogging & Medical Camps -> Count = 28)", CYAN, 4),
        (11, "[RECEDE] Phase 7: Outbreak Receding (Count = 11 cases)", GREEN, 3),
        (4,  "[SAFE]   Phase 8: Normalized to Safe Baseline (Count = 4)", GREEN, 1),
    ]

    print(f"{CYAN}>> TIP: Keep your browser open on the Public Health Dashboard:{RESET}")
    print(f"   URL: {BOLD}http://127.0.0.1:5000/public-health/trend-alerts{RESET}\n")
    print("Press Enter to begin the simulation cycle...")
    input()

    for count, name, color, delay in stages:
        update_stat_count(app, area, condition, time_bucket, count)
        print(f"{color}{BOLD}>> {name}{RESET}")
        print(f"   Database updated: {area} | {condition} = {BOLD}{count} cases{RESET}")
        if count >= 37:
            print(f"   {RED}** REFRESH BROWSER NOW: Trend Alert is active on dashboard! **{RESET}")
        print(f"   Waiting {delay} seconds...\n")
        time.sleep(delay)

    print(f"\n{GREEN}{BOLD}*** Simulation Completed! Disease counts returned to normal baseline. ***{RESET}\n")


def trigger_spike_only(app, area="Katraj (Ward C)", condition="Dengue", time_bucket="2026-W38", count=48):
    """Immediately set a high outbreak spike."""
    update_stat_count(app, area, condition, time_bucket, count)
    print(f"\n{RED}{BOLD}[!] High Outbreak Spike Activated!{RESET}")
    print(f"   {area} - {condition} set to {BOLD}{count} cases{RESET}.")
    print(f"   Check dashboard at: {CYAN}http://127.0.0.1:5000/public-health/trend-alerts{RESET}\n")


def reset_to_baseline(app):
    """Reset Katraj and Hadapsar stats back to default seed counts."""
    with app.app_context():
        # Reset Katraj
        s = Stats.query.filter_by(area="Katraj (Ward C)", condition="Dengue", time_bucket="2026-W38").first()
        if s:
            s.count = 3
        
        # Reset Kothrud
        s2 = Stats.query.filter_by(area="Kothrud (Ward B)", condition="Dengue", time_bucket="2026-W38").first()
        if s2:
            s2.count = 38
        
        db.session.commit()
    print(f"\n{GREEN}{BOLD}[OK] Database stats reset to standard seed baseline.{RESET}\n")


def main():
    app = create_app()
    print_banner()

    while True:
        print(f"{BOLD}Select an action:{RESET}")
        print(f"  {CYAN}[1]{RESET} Run Animated Outbreak Cycle (Increases -> Peaks -> Recedes to normal)")
        print(f"  {CYAN}[2]{RESET} Set Instant Outbreak Spike (Katraj Dengue = 52 cases)")
        print(f"  {CYAN}[3]{RESET} Reset Stats Back to Normal Seed Baseline")
        print(f"  {CYAN}[4]{RESET} Exit Simulator")
        
        choice = input(f"\nEnter choice [1-4]: ").strip()
        
        if choice == "1":
            run_live_simulation(app)
        elif choice == "2":
            trigger_spike_only(app)
        elif choice == "3":
            reset_to_baseline(app)
        elif choice == "4":
            print(f"\n{CYAN}Exiting simulator. Goodbye!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}Invalid option. Please enter 1, 2, 3, or 4.{RESET}\n")


if __name__ == "__main__":
    main()
