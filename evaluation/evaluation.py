import pandas as pd
import numpy as np
import os
import csv
import os




def get_list_labeled_CSV(file_path):
    # Read the CSV file into a pandas DataFrame with 'latin1' encoding
    df = pd.read_csv(file_path, header=None, encoding='latin1')

    # Create a dictionary to store feature names and their corresponding lists
    feature_dict = {}

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Get the feature name from the first column (index 0)
        feature_name = row.iloc[0]
        feature_name = modify_feature_name(feature_name)


        # Get the data points for the current feature (from index 1 to the end)
        data_points = row.iloc[1:].tolist()

        # If the feature name is already in the dictionary, append the data points
        if feature_name in feature_dict:
            feature_dict[feature_name].extend(data_points)
        else:
            # Otherwise, add a new entry to the dictionary
            feature_dict[feature_name] = data_points

    # Prepare a list to store the results
    result_list = []

    # Iterate through the dictionary and append the results to the list
    for feature_name, data_points in feature_dict.items():
        total_data_points = len(data_points)
        result_list.append({
            'FeatureName': feature_name,
            'DataPoints': data_points,
            'TotalDataPoints': total_data_points
        })

    return result_list

# # Example usage:
# file_path = 'labeled.csv'
# result = get_list_labeled_CSV(file_path)

# # Print the results
# for entry in result:
#     print(entry)


def modify_feature_name(original_feature_name):
    # Add more if statements for additional conditions


    if any(word.lower() == "functievervulling" for word in original_feature_name.lower().split()):
        return "Aanvang en einde functievervulling in "    
    elif "Functie" in original_feature_name:
        return "Functiegegevens"    
    elif "bedragen" in original_feature_name:
        return "bedragen"     
    elif "dienstverband" in original_feature_name:
        return "Omvang dienstverband (als deeltijdfactor in fte)"   
    elif "Dienstbetrekking" in original_feature_name:
        return "Dienstbetrekking?"
    elif any(word.lower() == "Beloning" for word in original_feature_name.lower().split()):
        return "Beloning plus belastbare onkostenvergoedingen"   
    elif any(word.lower() == "Beloningen" for word in original_feature_name.lower().split()):
        return "Beloningen betaalbaar op termijn"
    elif "Subtotaal" in original_feature_name:
        return "Subtotaal"                  
    elif "bezoldigingsmaximum" in original_feature_name:
        return "Individueel toepasselijke bezoldigingsmaximum"
    elif "Bezoldiging" in original_feature_name:
        return "Bezoldiging"     
    elif "Onverschuldigd" in original_feature_name:
        return "-/- Onverschuldigd betaald en nog niet terugontvangen bedrag"   
    elif "overschrijding" in original_feature_name:
        return "Het bedrag van de overschrijding en de reden waarom de overschrijding al dan niet is toegestaan"       
    elif "onverschuldigde" in original_feature_name:
        return "Toelichting op de vordering wegens onverschuldigde betaling"   
    else:
        return original_feature_name

def get_list_predicted_csv(file_path):
    # Read the CSV file into a pandas DataFrame with 'latin1' encoding
    df = pd.read_csv(file_path, encoding='latin1')

    # Prepare a list to store the results
    result_list = []

    # Iterate through each column in the DataFrame
    for column in df.columns:
        # Get the feature name from the column header
        original_feature_name = column

        # Modify the feature name based on the conditions in the separate method
        feature_name = modify_feature_name(original_feature_name)

        # Get the data points for the current feature
        data_points = df[column].tolist()

        # Calculate the total number of data points
        total_data_points = len(data_points)

        # Append the results to the list
        result_list.append({
            'P FeatureName': feature_name,
            'P Data Points': data_points,
            'TotalDataPoints': total_data_points
        })

    return result_list


# # Example usage:
# file_path = 'output.csv'
# result = get_list_predicted_csv(file_path)

# # Print the results
# for entry in result:
#     print(entry)

def compare_csv_features(labeled_file_path, predicted_file_path):
    # Get labeled and predicted data
    labeled_data = get_list_labeled_CSV(labeled_file_path)
    predicted_data = get_list_predicted_csv(predicted_file_path)

    # Create dictionaries to store data by feature name
    labeled_dict = {entry['FeatureName']: entry for entry in labeled_data}
    predicted_dict = {entry['P FeatureName']: entry for entry in predicted_data}

    # Initialize counters
    true_positive_data_points_count = 0
    false_positive_data_points_count = 0
    false_negative_data_points_count = 0
    partially_true_data_points_count = 0
    total_data_points_in_labeled = 0

    # New lists for storing individual data points
    true_positive_data_points = []
    false_positive_data_points = []
    false_negative_data_points = []
    partially_true_data_points = []

    # Iterate through labeled features and compare with predicted features
    for labeled_feature in labeled_dict.values():
        feature_name = labeled_feature['FeatureName']

        if feature_name in predicted_dict:
            labeled_data_points = labeled_feature['DataPoints']
            predicted_feature = predicted_dict[feature_name]['P Data Points']

            # Update total data points in labeled
            total_data_points_in_labeled += len(labeled_data_points)

            # Compare data points
            for predicted_data_point, labeled_data_point in zip(predicted_feature, labeled_data_points):
                # Handle NaN values
                if pd.notna(predicted_data_point) and pd.notna(labeled_data_point):
                    # Convert to string for comparison
                    predicted_data_point_str = str(predicted_data_point)
                    labeled_data_point_str = str(labeled_data_point)

                    if predicted_data_point_str == labeled_data_point_str:
                        true_positive_data_points_count += 1
                        true_positive_data_points.append(predicted_data_point_str)
                    elif predicted_data_point_str in labeled_data_point_str or labeled_data_point_str in predicted_data_point_str:
                        partially_true_data_points_count += 1
                        partially_true_data_points.append(predicted_data_point_str)
                    else:
                        false_positive_data_points_count += 1
                        false_positive_data_points.append(predicted_data_point_str)
        else:
            print("")
            print("===================!!!!!!!!!!!!!=============================")
            print("FeatureName in Predicted CSV Not found in labeled CSV: ",feature_name)     
            print("Check the csv Please")     
            print("===================!!!!!!!!!!!!!=============================")    
            print("")     
    # Calculate false negative data points
    false_negative_data_points_count = total_data_points_in_labeled - true_positive_data_points_count - partially_true_data_points_count
    # New list for false negative data points
    labeled_data_point=zip(labeled_data_points)
    false_negative_data_points = list(set(labeled_data_point) - set(true_positive_data_points))

    # Calculate precision and recall
    precision = true_positive_data_points_count / (true_positive_data_points_count + false_positive_data_points_count) if (true_positive_data_points_count + false_positive_data_points_count) > 0 else 0
    recall = true_positive_data_points_count / (true_positive_data_points_count + false_negative_data_points_count) if (true_positive_data_points_count + false_negative_data_points_count) > 0 else 0

    # Print the comparison results
    print(f"Total Data Points in Labeled: {total_data_points_in_labeled}")
    print(f"True Predicted Data Points: {true_positive_data_points_count}")
    print(f"Partially True Data Points: {partially_true_data_points_count}")
    print(f"False Positive Data Points: {false_positive_data_points_count}")
    print(f"False Negative Data Points: {false_negative_data_points_count}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")

    # Print the lastly added lists
    print("\nTrue Positive Data Points:", true_positive_data_points)
    print("Partially True Data Points:", partially_true_data_points)
    print("False Positive Data Points:", false_positive_data_points)
    print("False Negative Data Points:", false_negative_data_points)

    # Instead of printing results, return a dictionary with metrics
    result = {
        'total_data_points_in_labeled': total_data_points_in_labeled,
        'true_positive': true_positive_data_points_count,
        'partially_true': partially_true_data_points_count,
        'false_positive': false_positive_data_points_count,
        'false_negative': false_negative_data_points_count,
        'precision': precision,
        'recall': recall,
        'true_positive_data_points': true_positive_data_points,
        'partially_true_data_points': partially_true_data_points,
        'false_positive_data_points': false_positive_data_points,
        'false_negative_data_points': false_negative_data_points
    }

    return result

# # Example usage:
# labeled_file_path = 'labeled1.csv'
# predicted_file_path = 'output1.csv'
# compare_csv_features(labeled_file_path, predicted_file_path)


def compare_csv_features_for_folders(folder1_path, folder2_path, output_csv_path='overall_metrics.csv'):
    # Get the list of file names in both folders
    folder1_files = os.listdir(folder1_path)
    folder2_files = os.listdir(folder2_path)

    # Initialize overall metrics
    overall_true_positive = 0
    overall_partially_true = 0
    overall_false_positive = 0
    overall_false_negative = 0
    overall_total_data_points_in_labeled = 0
    total_files = 0
    total_true_files = 0  # Counter for files with total_data_points_in_labeled == true_positive_data_points_count
    partially_predicted_files = 0
    false_predicted_files = 0
    total_files=len(folder2_files)

    # Iterate through files in the first folder
    for file1_name in folder1_files:
        # Check if the file exists in the second folder
        if file1_name in folder2_files:
            # Form the full file paths for comparison
            labeled_file_path = os.path.join(folder1_path, file1_name)
            predicted_file_path = os.path.join(folder2_path, file1_name)

            # Call the compare_csv_features method for the matched files
            print(f"Comparing {file1_name}:")
            metrics = compare_csv_features(predicted_file_path,labeled_file_path)
            print("\n" + "="*30 + "\n")

            # Accumulate metrics for overall summary
            overall_true_positive += metrics['true_positive']
            overall_partially_true += metrics['partially_true']
            overall_false_positive += metrics['false_positive']
            overall_false_negative += metrics['false_negative']
            overall_total_data_points_in_labeled += metrics['total_data_points_in_labeled']

            # Increment total files counter
            #total_files += 1

            # Check if total_data_points_in_labeled equals true_positive_data_points_count
            if metrics['total_data_points_in_labeled'] == metrics['true_positive']:
                total_true_files += 1

            # Check if length of true positive points is greater than 0 for partially predicted files
            if len(metrics['true_positive_data_points']) > 0:
                partially_predicted_files += 1

            # Check if false positive or false negative data points exist for false predicted files
            if metrics['total_data_points_in_labeled'] == metrics['false_positive'] or metrics['total_data_points_in_labeled'] == metrics['false_negative']:
                false_predicted_files += 1
        else:
            false_predicted_files += 1
            print("Table in labeled folder Not Found in output folder",file1_name)


    # Calculate overall precision and recall
    overall_precision = overall_true_positive / (overall_true_positive + overall_false_positive) if (overall_true_positive + overall_false_positive) > 0 else 0
    overall_recall = overall_true_positive / (overall_true_positive + overall_false_negative) if (overall_true_positive + overall_false_negative) > 0 else 0

    # Print the overall metrics
    print("\nOverall Metrics:")
    print(f"Total Labeled Tables: {total_files}")
    print(f"Total True Tables : {total_true_files}")
    print(f"Partially Predicted Tables: {partially_predicted_files}")
    print(f"False Predicted Tables: {false_predicted_files}")
    print(f"Total Data Points in Labeled: {overall_total_data_points_in_labeled}")
    print(f"Overall True Predicted Data Points: {overall_true_positive}")
    print(f"Overall Partially True Data Points: {overall_partially_true}")
    print(f"Overall False Positive Data Points: {overall_false_positive}")
    print(f"Overall False Negative Data Points: {overall_false_negative}")
    print(f"Overall Precision: {overall_precision}")
    print(f"Overall Recall: {overall_recall}")

        # Create a list to store overall metrics
    overall_metrics = [
        ["Total Tables", "Total True Tables", "Partially Predicted Tables",
         "False Predicted Tables", "Total Data Points in Labeled",
         "Overall True Predicted Data Points", "Overall Partially True Data Points",
         "Overall False Positive Data Points", "Overall False Negative Data Points",
         "Overall Precision", "Overall Recall"]
    ]

    # Add overall metrics to the list
    overall_metrics.append([
        total_files, total_true_files, partially_predicted_files,
        false_predicted_files, overall_total_data_points_in_labeled,
        overall_true_positive, overall_partially_true,
        overall_false_positive, overall_false_negative,
        overall_precision, overall_recall
    ])

    # Save overall metrics to CSV file
    with open(output_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(overall_metrics)

    print(f"\nOverall metrics saved to '{output_csv_path}'.")


#========================================================================================================

# TO USE HERE:
#folder1_path : is the folder with csv from the pipeline
#folder2_path = is the folder with csv from the labeled tables

#requirements
#1. features names in output folder in coulmns (each coulmn is a feature name)
#2. features names in labeled folder in rows (each row is a feature name)
#3. In order to compare 2 csv they has to have the SAME NAME otherwise it will be a False Table
#4. Files are in CSV format
#5. if something is missing (feature name or datapoint) it will be printed to make sure to check 


folder1_path = 'output' #the output folder
folder2_path = 'labeled' #the labeled folder
compare_csv_features_for_folders(folder1_path, folder2_path)


#========================================================================================================