import argparse
import glob
import json
import os
from itertools import chain

from sklearn.metrics import f1_score

EV_OUT = "evaluation.txt"

def read_solution_files(solutions_folder):
    """
    reads all solution files into dict
    :param solutions_folder: path to folder holding the solution files
    :return: dict of solution files with problem-id as key and file content as value
    """
    solutions = {}
    for solution_file in glob.glob(os.path.join(solutions_folder, 'solution-problem-*.json')):
        with open(solution_file, 'r') as fh:
            curr_solution = json.load(fh)
            solutions[os.path.basename(solution_file)[9:-5]] = curr_solution
    return solutions

def read_ground_truth_files(truth_folder):
    """
    reads ground truth files into dict
    :param truth_folder: path to folder holding ground truth files
    :return: dict of ground truth files with problem-id as key and file content as value
    """
    truth = {}
    for truth_file in glob.glob(os.path.join(truth_folder, 'truth-*.json')):
        with open(truth_file, 'r') as fh:
            curr_truth = json.load(fh)
            truth[os.path.basename(truth_file)[6:-5]] = curr_truth
    return truth

def extract_task_results(truth, solutions, task):
    """
    extracts truth and solution values for a given task
    :param truth: dict of all ground truth values with problem-id as key
    :param solutions: dict of all solution values with problem-id as key
    :param task: task for which values are extracted (string, e.g., 'multi-author' or 'changes')
    :return: list of all ground truth values, list of all solution values for given task
    """
    all_solutions = []
    all_truth = []
    for problem_id, truth_instance in truth.items():
        all_truth.append(truth_instance[task])
        try:
            all_solutions.append(solutions[problem_id][task])
        except KeyError as _:
            print("No solution file found for problem %s, exiting." % problem_id)
            exit(0)
    return all_truth, all_solutions

def compute_task1_f1_score(truth, solutions):
    """ compute f1 score for task 1
    :param truth: list of ground truth values for all problem-ids
    :param solutions: list of solutions for all problem-ids
    :return: f1 score
    """
    task1_truth, task1_solution = extract_task_results(truth, solutions, 'multi-author')
    return f1_score(task1_truth, task1_solution, average='micro')

def compute_task2_f1_score(truth, solutions):
    """ compute f1 score for task 2
    :param truth: list of ground truth values for all problem-ids
    :param solutions: list of solutions for all problem-ids
    :return: f1 score
    """
    task2_truth, task2_solution = extract_task_results(truth, solutions, 'changes')
    # task 2 - lists have to be flattened first
    return f1_score(list(chain.from_iterable(task2_truth)), list(chain.from_iterable(task2_solution)), average='micro', labels=[0, 1])

def write_output(filename, k, v):
    """
    print() and write a given measurement to the indicated output file
    :param filename: full path of the file, where to write to
    :param k: the name of the metric
    :param v: the value of the metric
    :return: None
    """
    line = 'measure{{\n  key: "{}"\n  value: "{}"\n}}\n'.format(k, str(v))
    print(line)
    open(filename, "a").write(line)


def main():
    parser = argparse.ArgumentParser(description='PAN20 Style Change Detection Task: Output Verifier')
    parser.add_argument("-p", "--predictions", help="path to the dir holding the predicted labels", required=True)
    parser.add_argument("-t", "--truth", help="path to the dir holding the true labels", required=True)
    parser.add_argument("-o", "--output", help="path to the dir to write the results to", required=True)
    args = parser.parse_args()

    solutions = read_solution_files(args.predictions)
    truth = read_ground_truth_files(args.truth)

    for k, v in {"task1_score": compute_task1_f1_score(truth, solutions),
     "task2_score": compute_task2_f1_score(truth, solutions)}.items():
        write_output(os.path.join(args.output, EV_OUT), k, v)

if __name__ == "__main__":
    main()
