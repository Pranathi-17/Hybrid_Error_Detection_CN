from pathlib import Path
from simulation import run_default_experiment, run_custom_experiment
from analysis import generate_all_graphs, print_results_table, save_results_csv, print_conclusion

def print_header():
    print("\n" + "=" * 72)
    print("  HYBRID ERROR-DETECTION SCHEME FOR LOW-POWER IoT LINKS")
    print("=" * 72)

def main():
    print_header()

    while True:
        print("\nMenu")
        print("1. Run default simulation")
        print("2. Run simulation with custom error rate")
        print("3. Compare Checksum vs CRC vs Hybrid")
        print("4. Generate graphs")
        print("5. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            results = run_default_experiment()
            print_results_table(results)
            save_results_csv(results)
            generate_all_graphs(results)
            print_conclusion(results)
            print("\nSimulation completed successfully.")
            print("Results saved in the results/ folder.")

        elif choice == "2":
            value = input("Enter error rate (0-100): ").strip()
            try:
                rate = float(value)
                if not 0 <= rate <= 100:
                    raise ValueError
                results = run_custom_experiment(rate)
                print_results_table(results)
                save_results_csv(results)
                generate_all_graphs(results)
                print("\nCustom simulation completed successfully.")
                print("Results saved in the results/ folder.")
            except ValueError:
                print("Please enter a valid error rate between 0 and 100.")

        elif choice == "3":
            results = run_default_experiment()
            print_results_table(results)
            save_results_csv(results)
            print("\nComparison completed.")
            print("Use option 4 to regenerate graphs if needed.")

        elif choice == "4":
            csv_path = Path(__file__).resolve().parent / "results" / "simulation_results.csv"
            if not csv_path.exists():
                print("No result data found. Run option 1 first.")
            else:
                from analysis import load_results_csv
                results = load_results_csv(csv_path)
                generate_all_graphs(results)
                print("\nGraphs generated successfully in the results/ folder.")

        elif choice == "5":
            print("Exiting. Thank you!")
            break

        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()
