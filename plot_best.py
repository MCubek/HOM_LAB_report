import re

import matplotlib.pyplot as plt

if __name__ == '__main__':
    results = []

    for line in open('images_backup/output.log', 'r'):
        if line.startswith("Score"):
            match = re.match('Score: (\\d+) of ([\\w ]+),([\\w ]+) with squad .*', line)
            results.append(match.groups())

    instances = {}
    for score, instance, params in results:
        score = int(score)

        if instance not in instances.keys():
            instances[instance] = []

        instances[instance].append((score, params))

    for instance, score_params_list in instances.items():
        plt.figure(constrained_layout=True)
        plt.autoscale()
        plt.title(instance)

        scores, params = zip(*score_params_list)

        bars = plt.barh(params, scores)
        plt.xlabel('Scores')

        plt.bar_label(bars)

        plt.savefig(f'images/final_{instance.replace(" ", "")}.png', bbox_inches='tight')
        plt.show()
