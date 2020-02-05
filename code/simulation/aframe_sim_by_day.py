from aframesimulation import *


date_list = [
    "2019-11-01",
    "2019-11-02",
    "2019-11-03",
    "2019-11-04",
    "2019-11-05",
    "2019-11-06",
    "2019-11-07",
    "2019-11-08",
    "2019-11-09",
    "2019-11-10",
    "2019-11-11",
    "2019-11-12",
    "2019-11-13",
    "2019-11-14",
    "2019-11-15",
]

for date in date_list:

    file = "../generated_data/picks_per_date/" + date + ".csv"
    order_list, pick_start = get_order_list_and_pick_start_from_file(file)

    print("Starting simulation for date: " + date)

    start = arrow.get(pick_start)
    manual_picks = 0

    env = simpy.Environment(initial_time=start.timestamp)
    aframe = Aframe(env, NUM_MACHINES, PICKTIME)
    assign_current_allocation_to_aframe_object(aframe)

    all_skus_missing, one_sku_missing = get_all_maybe_ok_skus_from_file()

    for i in range(len(order_list)):
        order_number = int(order_list[i][1])
        order_time = order_list[i][0]
        # ast.literal_eval is a safe eval for lists, tuples etc.
        skus_in_order = ast.literal_eval(order_list[i][2])
        sku_quantities_in_order = ast.literal_eval(order_list[i][3])
        if (set(skus_in_order)) <= set(aframe.skus_in_aframe):
            env.process(
                order_handler(
                    env,
                    order_number,
                    order_time,
                    skus_in_order,
                    sku_quantities_in_order,
                    aframe,
                )
            )
        else:
            missing_skus = set(skus_in_order) - set(aframe.skus_in_aframe)
            manual_picks += 1
            if missing_skus.issubset(set(all_skus_missing.keys())):
                for sku in missing_skus:
                    all_skus_missing[sku] += 1

                # this is when there is only one item missing!
                if len(missing_skus) == 1:
                    for sku in missing_skus:
                        one_sku_missing[sku] += 1
            else:
                pass

    env.run()

    save_aframe_info_to_file(aframe, date)
    save_missing_sku_info_to_file(all_skus_missing, one_sku_missing, date)
    save_aframe_general_stats_to_file(aframe, date, manual_picks)
    print("Ending simulation for date: " + date)
