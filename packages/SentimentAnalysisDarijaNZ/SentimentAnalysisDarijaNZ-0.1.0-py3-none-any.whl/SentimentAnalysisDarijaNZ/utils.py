def calul_moyen_scores(data):
    # Remplace les scores > 1 par 1
    scores_ajustes = [min(score, 1) for _, score in data]

    # Calcul de la moyenne des scores ajustés
    moyenne = sum(scores_ajustes) / len(scores_ajustes) if scores_ajustes else 0

    return moyenne

import csv

def csv_to_list(file_path: str) -> list:
  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      reader = csv.reader(file)
      data = list(reader)
      return data
  except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    return None
  except Exception as e:
    print(f"An error occurred: {e}")
    return None

"""## Reads a CSV file and returns a list of the first column's values."""

import csv

def get_first_column(file_path):
  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      reader = csv.reader(file)
      first_column_data = [row[0] for row in reader]  # Extract the first element of each row
      return first_column_data
  except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    return None
  except IndexError:
    print("Error: Some rows might be empty in the CSV file.")
    return None
  except Exception as e:
    print(f"An error occurred: {e}")
    return None
