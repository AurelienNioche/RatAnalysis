import csv
import xlsxwriter
from os import listdir, mkdir
from os.path import isfile, join, exists
from pylab import np, plt


class Cell:
    def __init__(self, content):
        self.content = content

    def is_date(self):
        return "/" in self.content and ":" in self.content

    def is_trial_number(self):
        return self.content[0] == 't'

    def is_empty(self):
        return len(self.content) == 0

    def is_not_a_star(self):
        return self.content != "*"


def extract_data(file_path):

    with open(file_path, 'rt') as file:

        reader = csv.reader(file, delimiter='\t')

        data = dict()  # or {}

        current_key = None

        for row in reader:

            try:
                first_cell = Cell(row[0] if len(row) >= 1 else '')
                second_cell = Cell(row[1] if len(row) >= 2 else '')

                if not first_cell.is_empty() and not first_cell.is_date():

                    if first_cell.is_trial_number():

                        if current_key is None:
                            raise Exception("I did not succeed finding the key.")

                        # Add the content of the second cell to the appropriate entry
                        value = int(second_cell.content) if second_cell.is_not_a_star() else 0
                        data[current_key].append(value)
                        print("A value has been extracted from row '{}'.".format(row))

                    else:
                        # Create a new entry in the dictionary containing data
                        current_key = first_cell.content
                        data[current_key] = []
                        print("A key has been extracted from row '{}'.".format(row))

                else:
                    print("Row '{}' will be ignored (either the first cell is empty or it is a date).".format(row))

            except Exception as e:
                print("Row '{}' will be ignored. It raised an exception ('{}')".format(row, e))

    # Add a column for trial number
    n_max = max([len(v) for v in data.values()])
    data["trial"] = list(range(n_max))

    # Remove keys without any value
    data = {key: value for key, value in data.items() if len(value)}

    # Complete missing values with zeros
    for key in data.keys():
        n_zeros_to_add = n_max - len(data[key])
        data[key] += [0, ] * n_zeros_to_add

    return data


def write_a_new_file(data, file_path):

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()

    # Sort column names by alphabetic order
    column_names = sorted(list(data.keys()))

    # Put trial as first column
    if "trial" in column_names:
        column_names.remove("trial")
        column_names = ["trial", ] + column_names

    # Start to fill beginning from the first column.
    col = 0

    # Write data column by column
    for c_name in column_names:

        row = 0

        # Write the column_name
        worksheet.write(row, col, c_name)
        row += 1

        # Fill the column with data
        for v in data[c_name]:
            worksheet.write(row, col, v)
            row += 1

        col += 1

    workbook.close()

    print("Xlsx file '{}' created with success.\n".format(file_path))


def short_analysis(data, analysis_file_path, fig_root_name):

    # Suppose there are two idx for rt
    for rt_idx in [1, 2]:

        # Convert your data in array for easier manipulation
        rt_column_name = "RT {}".format(rt_idx)
        rt = np.asarray(data[rt_column_name])
        rt_mt_column_name = "RT-MT {}".format(rt_idx)
        rt_mt = np.asarray(data[rt_mt_column_name])

        # Look where 'rt' and 'rt_mt' are different to zero
        cond0 = rt[:] != 0
        cond1 = rt_mt[:] != 0

        # Combine the two conditions
        idx = cond0 * cond1

        # Use the booleans as index and make a cut in your data
        rt = rt[idx]
        rt_mt = rt_mt[idx]

        # Compute 'mt'
        mt = rt_mt - rt

        print("Short analysis.")
        print("'mt {}' is: \n".format(rt_idx), mt)

        # Save this in a new 'xlsx' file
        new_data = dict()
        new_data["RT{}".format(rt_idx)] = rt
        new_data["MT{}".format(rt_idx)] = mt
        write_a_new_file(file_path=analysis_file_path, data=new_data)

        # Do some plots
        plt.scatter(mt, rt)
        plt.xlabel("mt")
        plt.ylabel("rt")
        plt.savefig("{}_scatter_rt{}.pdf".format(fig_root_name, rt_idx))
        plt.close()

        plt.hist(mt)
        plt.xlabel("mt")
        plt.savefig("{}_hist_mt{}.pdf".format(fig_root_name, rt_idx))
        plt.close()

        plt.hist(rt)
        plt.xlabel("rt")
        plt.savefig("{}_hist_rt{}.pdf".format(fig_root_name, rt_idx))
        plt.close()


def create_folder(folder_path):

    if not exists(folder_path):
        mkdir(folder_path)


def main():

    # Path of the folder where your raw data are
    data_folder = "data"

    # Paths of the folder where the outputs of this script will go
    new_data_folder = "new_data"
    figure_folder = "figures"
    analysis_folder = "analysis_results"

    # Create the 'outputs' folders
    create_folder(figure_folder)
    create_folder(new_data_folder)
    create_folder(analysis_folder)

    # List data files
    data_files = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]
    for file_path in data_files:

        extension = file_path.split('.')[-1]

        if extension in ("xls", "csv"):

            print("I will convert '{}'.\n".format(file_path))

            complete_file_path = data_folder + "/" + file_path

            file_path_without_extension = file_path.split(".")[0]

            new_file_path = "{}/new_{}.xlsx".format(new_data_folder, file_path_without_extension)
            analysis_file_path = "{}/analysis_{}.xlsx".format(analysis_folder, file_path_without_extension)
            fig_root_name = "{}/fig_{}".format(figure_folder, file_path_without_extension)

            data = extract_data(file_path=complete_file_path)
            write_a_new_file(data=data, file_path=new_file_path)
            short_analysis(data=data, analysis_file_path=analysis_file_path, fig_root_name=fig_root_name)

        else:

            print("I will ignore '{}' for conversion.".format(file_path))


if __name__ == "__main__":
    main()
