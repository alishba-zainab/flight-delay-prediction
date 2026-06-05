import csv
import traceback

def add_flight_number_column(input_filepath, output_filepath):
    try:
        with open(input_filepath, 'r', newline='', encoding='utf-8') as infile, \
             open(output_filepath, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            header = next(reader)
            writer.writerow(header + ['flight_number'])

            # Get column indices
            try:
                origin_idx = header.index('origin')
                fl_date_idx = header.index('fl_date')
            except ValueError as e:
                print(f"❌ Missing column: {e}")
                return

            # Process each row
            for i, row in enumerate(reader, start=1):
                if len(row) > max(origin_idx, fl_date_idx):
                    origin = row[origin_idx].strip()
                    fl_date = row[fl_date_idx].strip()
                    flight_number = f"{origin}-{fl_date}"
                    writer.writerow(row + [flight_number])
                else:
                    print(f"⚠️ Skipping row with missing data at line {i}: {row}")
                    writer.writerow(row + [''])

                if i % 100000 == 0:
                    print(f"✅ Processed {i:,} rows...")

            print(f"\n✅ Done! File saved to: {output_filepath}")

    except FileNotFoundError:
        print(f"❌ File not found: {input_filepath}")
    except Exception as e:
        print("❌ An unexpected error occurred:")
        traceback.print_exc()


# ✅ Set file paths
input_csv_path = r"C:\Users\user\OneDrive\Desktop\AI\flight_data_2024.csv"
output_csv_path = r"C:\Users\user\OneDrive\Desktop\AI\flight_data_with_flight_number.csv"

# 🚀 Run the function
add_flight_number_column(input_csv_path, output_csv_path)
