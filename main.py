import subprocess
import re
import itertools

import matplotlib.pyplot as plt

from multiprocessing import Pool


def jar_wrapper(path, *args):
    process = subprocess.Popen(['java', '-jar', path] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != '' and line.endswith('\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += stdout.split('\n')
    if stderr != '':
        ret += stderr.split('\n')
    ret.remove('')
    return ret


def run_jar(arguments: list[str]) -> list[str]:
    jar_path = '/Users/matejc/Dev/IntelliJ/Heurističke metode optimizacije/Lab1_HMO/target/Lab1_HMO-1.0-SNAPSHOT.jar'
    return jar_wrapper(jar_path, *arguments)


def get_final_score(output: list[str]) -> int:
    for line in output:
        if line.startswith("Score = "):
            return int(line.removeprefix("Score = "))
    return -1


def get_scores_per_iter(output: list[str]) -> list[(int, int)]:
    result = []
    for line in output:
        if line.startswith("Iteration"):
            match = re.match('Iteration: (\\d+), score: (\\d+)', line)
            result.append(tuple(map(int, match.groups())))

    return result


def get_best_squad(output: list[str]) -> (list[int], list[int],):
    team1 = None
    team2 = None

    for line in output:
        first = re.match('(\\d+),(\\d+),(\\d+),(\\d+),(\\d+),(\\d+),(\\d+),(\\d+),(\\d+),(\\d+),(\\d+)', line)
        if first:
            team1 = map(int, first.groups())
            continue

        second = re.match('(\\d+),(\\d+),(\\d+),(\\d+)', line)
        if second:
            team2 = map(int, second.groups())
            break

    return list(team1), list(team2)


folder_path = '/Users/matejc/Dev/IntelliJ/Heurističke metode optimizacije/Lab1_HMO/src/main/resources/lab2/'

first_argument = [(folder_path + 'Lab2_inst1.csv', 'Instance 1'),
                  (folder_path + 'Lab2_inst2.csv', 'Instance 2')]
second_argument = [("1", "Tabu"), ("2", "Simulated Annealing")]
third_argument = [("1", "Greedy Initial"), ("2", "Random Initial")]

fourth_argument_tabu = list(map(lambda x: (str(x), "Tenure " + str(x)), range(5, 200, 25)))
fifth_argument_tabu = [("1", "Explicit Tabu List"), ("2", "Attributive Tabu List")]

fourth_argument_annealing = list(map(lambda x: (str(x), "Initial Temperature " + str(x)), range(10, 200, 40)))
fifth_argument_annealing = [("1", "Linear Strategy"), ("2", "Geometric Strategy")]

instance_alg_combination = [first_argument, second_argument, third_argument]
tabu_args_combination = [fourth_argument_tabu, fifth_argument_tabu]
annealing_args_combination = [fourth_argument_annealing, fifth_argument_annealing]


def loop_combinations_and_run(args_fixed, args_combination):
    for args in itertools.product(*args_combination):
        arguments, labels = zip(*args)

        arg_joined = args_fixed + arguments

        print("Running combination " + " ".join(labels))
        yield labels, run_jar(arg_joined)


def graph_instance(instance_arguments, label):
    print("Starting task " + label)

    plt.figure(figsize=(8, 6), dpi=80)
    plt.title(label)
    plt.ylabel("Score")
    plt.xlabel("Iteration")

    if instance_arguments[1] == "1":
        args_dynamic = tabu_args_combination
    elif instance_arguments[1] == "2":
        args_dynamic = annealing_args_combination
    else:
        raise Exception('No such algorithm')

    for labels, output in loop_combinations_and_run(instance_arguments, args_dynamic):
        final = get_final_score(output)

        combination_label = " ".join(labels)

        per_iter = get_scores_per_iter(output)

        x, y = zip(*per_iter)

        plt.plot(x, y, label=f'{combination_label}, best:{final}')

        squad = get_best_squad(output)
        print(f'Score: {final} of {label},{combination_label} with squad {squad}')

    plt.legend()

    plt.savefig(f'images/{label.replace(" ", "")}.png', bbox_inches='tight')
    plt.show()
    print('Finished task ' + label)


if __name__ == '__main__':

    pool = Pool()
    results = []

    for args in itertools.product(*instance_alg_combination):
        fixed_arguments, instance_labels = zip(*args)
        graph_label = " ".join(instance_labels)

        print(f'Starting task {graph_label}')
        results.append(pool.apply_async(graph_instance, [fixed_arguments, graph_label]))

    for result in results:
        result.get()

    print('Finished all tasks')
