import csv
import xlsxwriter
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

            first_cell = Cell(row[0])
            second_cell = Cell(row[1])

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
                print("Row '{}' will be ignored.".format(row))

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


def write_a_new_file(data, new_file_path):

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(new_file_path)
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

    print("Xlsx file '{}' created with success.".format(new_file_path))


def short_analysis(data, n_rt=2):

    rt = np.asarray(data["RT {}".format(n_rt)])
    rt_mt = np.asarray(data["RT-MT {}".format(n_rt)])

    cond0 = rt[:] != 0
    cond1 = rt_mt[:] != 0
    idx = cond0 * cond1

    rt = rt[idx]
    rt_mt = rt_mt[idx]

    mt = rt_mt - rt

    print("Short analysis.")
    print("mt is: \n", mt)

    new_data = dict()
    new_data["RT{}".format(n_rt)] = rt
    new_data["MT{}".format(n_rt)] = mt

    write_a_new_file(new_file_path="analysis.xlsx", data=new_data)

    plt.scatter(mt, rt)
    plt.xlabel("mt")
    plt.ylabel("rt")
    plt.savefig("scatter.pdf")
    plt.close()

    plt.hist(mt)
    plt.savefig("hist_mt.pdf")
    plt.close()

    plt.hist(rt)
    plt.savefig("hist_rt.pdf")
    plt.close()


def main():

    file_path = 'Rat_102_ChR2_MT-partial-5mW_21-07-2017.csv'
    new_file_path = 'NEW' + file_path.split(".")[0] + ".xlsx"

    data = extract_data(file_path=file_path)
    write_a_new_file(data=data, new_file_path=new_file_path)
    short_analysis(data)


if __name__ == "__main__":
    main()
