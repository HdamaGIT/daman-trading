#########################################################################################
#########################################################################################
#########################################################################################


# The save_data function takes four arguments:
    # data: a data object that can be converted to a CSV file
    # loc: a string representing the location where the CSV file should be saved
    # filename: a string representing the name of the file (without the '.csv' extension)
    # index: a boolean indicating whether to include the index column in the CSV file
    # The function converts data to a CSV file and saves it to the specified location with the given filename. If index is True, the index column will be included in the CSV file. The function prints a message indicating that the process was successful.


#########################################################################################
#########################################################################################
#########################################################################################


def save_data(data, loc, filename, index):
    """
    Saves the given data object as a CSV file to the specified location with the given filename.
    If index is True, the index column will be included in the CSV file.
    """

    data.to_csv(loc + filename + '.csv', index=index)
    print('Process: Historic data saved to ' + loc + filename + '.csv.')
