import subprocess
import re
import itertools

import matplotlib.pyplot as plt


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


folder_path = '/Users/matejc/Dev/IntelliJ/Heurističke metode optimizacije/Lab1_HMO/src/main/resources/'

first_argument = [(folder_path + '2022_instance1.csv', 'Instance 1'),
                  (folder_path + '2022_instance2.csv', 'Instance 2'),
                  (folder_path + '2022_instance3.csv', 'Instance 3')]
second_argument = [("1", "Tabu")]
third_argument = [("1", "Greedy Initial"), ("2", "Random Initial")]
# fourth_argument = map(lambda x: (str(x), "Tenure " + str(x)), range(5, 100, 5))
fourth_argument = list(map(lambda x: (str(x), "Tenure " + str(x)), range(5, 100, 25)))
fifth_argument = [("1", "Explicit Tabu List"), ("2", "Attributive Tabu List")]

instance_alg_combination = [first_argument, second_argument, third_argument]
tabu_args_combination = [fourth_argument, fifth_argument]


def loop_combinations_and_run(args_fixed, args_combination):
    for args in itertools.product(*args_combination):
        arguments, labels = zip(*args)

        arg_joined = args_fixed + arguments

        print("Running combination " + " ".join(labels))
        yield labels, run_jar(arg_joined)


if __name__ == '__main__':

    for args in itertools.product(*instance_alg_combination):
        fixed_arguments, instance_labels = zip(*args)

        graph_label = " ".join(instance_labels)

        print("Graphing " + graph_label)

        plt.figure(figsize=(8, 6), dpi=80)
        plt.title(graph_label)
        plt.ylabel("Score")
        plt.xlabel("Iteration")

        for labels, output in loop_combinations_and_run(fixed_arguments, tabu_args_combination):
            final = get_final_score(output)

            combination_label = " ".join(labels)

            per_iter = get_scores_per_iter(output)

            x, y = zip(*per_iter)

            plt.plot(x, y, label=f'{combination_label}, best:{final}')

            squad = get_best_squad(output)
            print(f'Score: {final} of {combination_label} with squad {squad}')

        plt.legend()
        plt.show()
