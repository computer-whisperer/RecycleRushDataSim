import csv
import sys

def_field = {"stack_height": 6, "stack_slots": 20, "totes": 65, "containers": 7, "litter": 10, "seconds": 135}
def_scenario = {"stack_height": 1, "stack_slots": 14, "totes": 65, "containers": 5, "litter": 5, "seconds": 135}
def_bot = {"add_tote_to_stack": 3, "add_container_to_stack": 4, "stick_litter_in_container": 4, "stack_score": 5}


def play_match(field, restrictions, bot):
    field["points"] = 0
    field["stacks"] = list()

    while field["seconds"] > 0:
        stack = dict()
        stack["points"] = 0
        stack["container"] = False
        stack["litter"] = False
        seconds_used = 0
        #Do stack

        #Containers and litter
        if field["containers"] > 0 and restrictions["containers"] > 0:
            stack["container"] = True
            seconds_used += bot["add_container_to_stack"]
            if field["litter"] > 0 and restrictions["litter"] > 0:
                stack["litter"] = True
                seconds_used += bot["stick_litter_in_container"]

        #Tote stacks
        stack["totes"] = min(field["stack_height"], field["totes"], restrictions["stack_height"], restrictions["totes"])
        seconds_used += bot["add_tote_to_stack"]*stack["totes"]

        #Score time
        seconds_used += bot["stack_score"]

        #Add up scores

        #Totes
        stack["points"] += 2 * min(stack["totes"], 6)
        #Containers
        if stack["container"]:
            stack["points"] += 4 * min(stack["totes"], 6)
        #Litter
        if stack["litter"]:
            stack["points"] += 6

        #Save stack
        if field["seconds"] - seconds_used >= 0 and field["stack_slots"] > 0 and restrictions["stack_slots"] > 0 and field["totes"] > 0 and restrictions["totes"] > 0:
            #Add stack object
            field["stacks"].append(stack)

            #Update stats
            field["stack_slots"] -= 1
            restrictions["stack_slots"] -= 1
            field["points"] += stack["points"]
            field["seconds"] -= seconds_used
            restrictions["seconds"] -= seconds_used

            #Deduct game pieces
            field["totes"] -= stack["totes"]
            restrictions["totes"] -= stack["totes"]

            if stack["container"]:
                field["containers"] -= 1
                restrictions["containers"] -= 1
            if stack["litter"]:
                field["litter"] -= 1
                restrictions["litter"] -= 1
        else:
            break


def print_field(field):
    print()
    print()
    open_text = "Possible Field:"
    print(open_text)
    print()
    print("Points scored: {}".format(field["points"]))
    print()
    print("Game Pieces:")
    print("Totes Left: {}".format(field["totes"]))
    print("Containers Left: {}".format(field["containers"]))
    print("Litter Left: {}".format(field["litter"]))
    print("Seconds Left: {}".format(field["seconds"]))
    print()
    print("{} Stacks Total:".format(len(field["stacks"])))

    #Compress stacks
    compressed_stacks = dedup_list(field["stacks"])

    #Print stacks
    for stack in compressed_stacks:
        print("{} Stacks: {} Totes, {} Container, {} Litter".format(stack["count"], stack["totes"], int(stack["container"]), int(stack["litter"])))

def dedup_list(ls):
    unique_vals = list()
    counts = list()
    for val in ls:
        for uval in unique_vals:
            if val == uval:
                counts[unique_vals.index(uval)] += 1
                break
        else:
            unique_vals.append(val)
            counts.append(1)
    for i in range(len(unique_vals)):
        unique_vals[i]["count"] = counts[i]
    return unique_vals

def multiply_dict(dictionary):
    compiled_dict = list()
    compiled_dict.append({})

    for key in dictionary:
        if isinstance(dictionary[key], int):
            for s in compiled_dict:
                s[key] = dictionary[key]
        if hasattr(dictionary[key], "__iter__"):
            prev_rest = compiled_dict[:]
            compiled_dict = list()
            for r in prev_rest:
                for v in dictionary[key]:
                    new_rest = r.copy()
                    new_rest[key] = v
                    compiled_dict.append(new_rest)
    return compiled_dict

def get_sorted_matches(field, restrictions, bot):
    results = list()
    for r in restrictions:
        new_field = field.copy()
        play_match(new_field, r, bot)
        results.append(new_field)
    cr = dedup_list(results)
    return sorted(cr, key=lambda d: d["points"])

def get_best_match(field, restrictions, bot):
    return get_sorted_matches(field, restrictions, bot)[:1][0]


def export_fields_csv(fields, rows, path):
    data = list()
    for row in rows:
        row_data = list()
        row_data.append(row)
        for f in fields:
            row_data.append(f[row])
        data.append(row_data)
    with open(path, "w", newline='') as f:
        f = csv.writer(f)
        f.writerows(data)


def get_robot():
    print()
    print("Enter Robot Statistics:")
    print()
    robot = {}
    robot["add_tote_to_stack"] = int(def_input("How long does it take your robot to add a Tote to it's stack?", 3))
    robot["add_container_to_stack"] = int(def_input("How long does it take your robot to Grab a Recycling Container?", 4))
    robot["stick_litter_in_container"] = int(def_input("How long does it take your robot to obtain and Insert a Litter into an obtained Recycling Container?", 4))
    robot["stack_score"] = int(def_input("How long does it take your robot to score a stack in it's possession?", 5))
    return robot


def def_input(prompt, default):
    val = input(prompt + " ({}): ".format(default))
    if val == "":
        val = default
    return val


if __name__ == "__main__":

    field = {"stack_height": 6, "stack_slots": 20, "totes": 70, "containers": 7, "litter": 10, "seconds": 135}
    restrictions = {"stack_height": [1, 2, 3, 4, 5, 6], "stack_slots": 14, "totes": 70, "containers": [0, 1, 2, 3, 4, 5, 6, 7], "litter": [0, 1, 2, 3, 4, 5, 6, 7], "seconds": 135}

    if sys.argv[1] == "top":
        bot = get_robot()
        count = 1
        if len(sys.argv) > 2:
            count = sys.argv[2]
        fields = get_sorted_matches(field, multiply_dict(restrictions), bot)
        print()
        print("TOP {} SCENARIOS:".format(count))
        print()
        for f in reversed(fields[len(fields)-count:]):
            print_field(f)

    elif sys.argv[1] == "export":
        bot_multi = {"add_tote_to_stack": [3, 4, 5, 6, 7], "add_container_to_stack": 4, "stick_litter_in_container": 4, "stack_score": 5}
        bots = multiply_dict(bot_multi)
        res = multiply_dict(restrictions)
        result = list()
        for bot in bots:
            res_field = get_best_match(field, res, bot)
            res_field.update(bot)
            result.append(res_field)
        export_fields_csv(result, ["add_tote_to_stack", "totes", "points"], "out.csv")


