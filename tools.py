from collections import Counter
from math import ceil

# now = datetime.now().strftime("%y%m%d-%H%M%S")  # current time, used for logs

# Generate string coloring functions using ANSI escape sequences
strr, strg, stry, strb, strm, strc = [lambda s, c=i: f"\033[{c}m{s}\033[0m" for i in range(91, 97)]

# Generate colored print functions syntactically compatible with print()
printr, printg, printy, printb, printm, printc = [lambda *args, c=i, **kwargs: print(*[f"\033[{c}m{s}\033[0m" for s in args], **kwargs) for i in range(91, 97)]


def bar(len):
    "Prints a bar of length len"
    return "█" * int(len / 8) + " ▏▎▍▌▋▊▉"[int(len) % 8]


def progress_bar(progress, length=1, total=8, color=lambda s: s):
    "Prints a progress bar"
    print("\r" + color(bar(8 * length * progress / total)) + "\r", end="", flush=True)


def histogram_vertical(A):
    "Prints a vertical histogram of the values in integer array A"
    for b, n in sorted(Counter(A).items()):
        print(f"{b:>2}: " + bar(n))


def histogram_horizontal(A):
    "Returns a horizontal histogram of the values in integer array A"
    c = Counter(A)
    return "".join([" ▁▂▃▄▅▆▇█"[int(ceil(8 * c[i] / (c.most_common(1)[0][1])))] for i in range(len(A) and int(max(A)) + 1)])


def writetsv(dict_list, filename="results.tsv"):
    if dict_list:
        with open(filename, "w") as f:
            f.write("\t".join(dict_list[0].keys()) + "\n")
            for row in dict_list:
                f.write("\t".join([str(i) for i in row.values()]) + "\n")
