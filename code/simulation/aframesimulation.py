"""This is an A-frame simulation.
It takes all the orders for a specific day and the current A-frame allocation
and simulates it. If orders can be processed in the A-frame they will
and accompanying statistics will be logged during the process. When the
simulation is done it will write interesting data to file for future
data analysis.
"""
import os
import csv
import ast
import simpy
import arrow

RANDOM_SEED = 0
NUM_MACHINES = 1  # Number of aframes
PICKTIME = 3  # seconds it takes to pick an order
SIM_TIME = 86400  # max Simulation time in seconds (86400 seconds== 24 hours)
THRESHOLD_FOR_REFILL = (
    0.2  # percentage that the channel will be refilled after (here 20%)
)


class Aframe:
    """The main class for the entire simulation. It is the Aframe class
that keeps track of most things. The purpose of the simulation is to
simulate the A-frame. It inits with multiple statistical variables that generate
data that can be used for further data analysis.
"""

    def __init__(self, env, num_machines, picktime):
        self.env = env
        self.machine = simpy.Resource(env, num_machines)
        self.picktime = picktime

        ### integers that keep track of interesting info
        self.no_orders_picked = 0
        self.total_picking_time = 0
        self.total_refills = 0
        self.total_orders_that_were_stock_out = 0

        ### channel info
        self.allocation = {}
        self.channel_max_capacity = {}
        self.channel_refills = {}
        self.channel_refill_counter = {}
        self.sku_channels = {}
        self.total_picks_from_channel = {}

        ### interesting lists
        self.skus_in_aframe = []
        self.orders_picked = []
        self.stocked_out_orders = []

    def add_sku(self, sku):
        """ Takes in a sku id and adds it to skus_in_aframe, which
        keeps tracks of all the unique skus in the A-frame.
        Arguments:
            sku {int} -- A sku id
        """
        if sku not in self.skus_in_aframe and sku != -1:
            self.skus_in_aframe.append(sku)

    def allocate_channels(self, channel, sku, sku_max):
        """ This allocates the maximum number of skus in the channel at the start of the day.
        The max number of skus for a channel is also stored in channel_max_capacity
        for easy access for other methods.
        In the real system it is assume that before the machine is started
        all the channels are filled.

        The dictionary total_picks_from_channel is initialized to be zero for the
        specific channel.

        The dictionary channel_refills is also initalized to be zero for
        the specific channel.

        Lastly the method assigns which skus are stored in which channels
        as a helper variable for other methods.

        This is a setter method that is only run before the simulation starts.

        Arguments:
            channel {int} -- Channel id
            sku {int} -- sku id
            sku_max {int} -- max possible number of skus that can be stored in a channel
        """
        self.allocation[channel] = [sku, sku_max]
        self.channel_max_capacity[channel] = sku_max
        self.total_picks_from_channel[channel] = 0
        self.channel_refills[channel] = 0
        self.channel_refill_counter[channel] = 0
        if sku in self.sku_channels:
            self.sku_channels[sku].append(channel)
        else:
            self.sku_channels[sku] = []
            self.sku_channels[sku].append(channel)

    def return_channels_for_a_sku(self, sku):
        """Gets the channels that a sku is stored in.

        Arguments:
            sku {int} -- sku id

        Returns:
            list -- a list of the channels that the sku is in
        """
        return self.sku_channels[sku]

    def number_of_items_in_channels_for_sku(self, sku):
        """Gets the number of items that are in a channel for a specific sku

        Arguments:
            sku {int} -- sku id

        Returns:
            int -- The current number of items in the channel
        """
        quantity = 0
        for channel in self.sku_channels[sku]:
            quantity += self.allocation[channel][1]
        return quantity

    def pick_from_channel(self, channel, quantity):
        """Performs a pick on a specified channel.
        The method will decrease the
        specified quantity from the channel.
        A statistics (total_picks_from_channel) is updated that
        keeps track of how many times the channel was picked from.
        The fill_level is a percentage from 0-100%,
        calculated by dividing the current number of items
        by the maximum number of items possible in the channel.
        If the fill_level is lower than the THRESHOLD_FOR_REFILL
        a refill is performed on the channel.

        Arguments:
            channel {int} -- channel id
            quantity {int} -- number of items to pick
        """
        self.allocation[channel][1] -= quantity
        self.total_picks_from_channel[channel] += 1
        fill_level = self.allocation[channel][1] / self.get_channel_max_capacity(
            channel
        )
        if THRESHOLD_FOR_REFILL > fill_level:
            self.refill_channel(channel)

    def ok_to_pick_order(self, skus_in_order, sku_quantities_in_order):
        """Returns a Boolean that specifies if the order can be picked in
        the A-frame or not. The method checks if there are enough
        items for the skus stored when considerings the quantity that
        should be picked

        Arguments:
            skus_in_order {list} -- a list of the skus in the order
            sku_quantities_in_order {list} -- a list of the quantity for the skus in the order

        Returns:
            Boolean -- return True if the order can be picked in the A-frame, false otherwise
        """
        ok_to_pick = False

        for index, sku in enumerate(skus_in_order):
            if (
                self.number_of_items_in_channels_for_sku(sku)
                >= sku_quantities_in_order[index]
            ):
                ok_to_pick = True
            else:
                ok_to_pick = False
                return ok_to_pick
        return ok_to_pick

    def pick_from_channels(self, channels, quantity):
        """Since some skus are stored in multiple channels there
        needs to be logic to distribute the picks among the
        channels, picking the entire quantity from one might
        result in a stock out. This method will check the inputted channels,
        find the one with the max quantity in it, pick 1 item in it,
        then repeat until all items have been picked.

        Arguments:
            channels {list} -- a list of channel ids
            quantity {int} -- number of items that needs to be picked for a sku
        """
        for i in range(0, quantity):
            # loop through the channels, find which channel has the most quantities in it
            # set max_channel to 0. If this channel does not exist, will create errors if try
            # to pick from it
            max_channel = 0
            for channel in channels:
                if max_channel == 0:
                    # set first channel to be the max channel.
                    max_channel = channel
                elif self.allocation[channel][1] > self.allocation[max_channel][1]:
                    max_channel = channel
            # now has max channel, pick 1 from it and repeat
            if max_channel != 0:
                self.pick_from_channel(max_channel, 1)
            else:
                raise Exception(
                    "pick_from_channels function "
                    + "tried to pick from channel that does not exist"
                )

    def get_channel_max_capacity(self, channel):
        """Returns the max capacity for a channel

        Arguments:
            channel {int} -- channel id

        Returns:
            [int] -- sku max capacity for the channel
        """
        return self.channel_max_capacity[channel]

    def refill_channel(self, channel):
        """Refills a channel to max capacity
        saves the number of items that need to be refilled for the channel
        increments the channel refills for the channel as well
        as the total number of refills in the aframe

        Arguments:
            channel {int} -- channel id
        """
        current_quantity_in_channel = self.allocation[channel][1]
        max_capacity_for_channel = self.get_channel_max_capacity(channel)
        refill_with = max_capacity_for_channel - current_quantity_in_channel
        self.channel_refill_counter[channel] += refill_with
        self.allocation[channel][1] = max_capacity_for_channel
        self.channel_refills[channel] += 1
        self.total_refills += 1

    def pick(self, order_number, skus_in_order, sku_quantities_in_order):
        """The main pick process for the A-frame. It takes an order number,
        the skus and their respective quantities for an order.
        It first checks if there are enough stored items in the channels to
        successfully pick the order.
        If there are, continue with the picking process, perform the picks
        from the channels that the skus are in. When all the picks
        have commenced the A-frame time outs for the PICKTIME seconds,
        this blocks other orders from being able to be processed while the
        A-frame picks the order. If some orders arrive at the same time they
        will form a queue for and be picked when the A-frame is available again.
        If there are not enough skus in the A-frame to perform the order
        they are seen as a stockout order and will be added to a list,
        the order is not picked.

        Arguments:
            order_number {int} -- order number
            skus_in_order {list} -- list of skus
            sku_quantities_in_order {list} -- list of sku quantities
        """

        # first see if the entire order can be picked in the aframe
        # by looking at all the channels for that sku,
        # if there are enough ok_to_pick_order will return true
        # and the aframe will try to pick.
        if self.ok_to_pick_order(skus_in_order, sku_quantities_in_order):
            # print("order ok")
            for index, sku in enumerate(skus_in_order):
                quantity = sku_quantities_in_order[index]
                channels = self.return_channels_for_a_sku(sku)
                self.pick_from_channels(channels, quantity)

            yield self.env.timeout(PICKTIME)
            self.total_picking_time += PICKTIME
            self.no_orders_picked += 1
            self.orders_picked.append(order_number)
        else:
            self.total_orders_that_were_stock_out += 1
            self.stocked_out_orders.append(order_number)

    def standby(self, time):
        """When the A-frame is not performing a pick it is seen as standby
        this is to get information how much the A-frame is used in seconds.
        The A-frame is put into standby until the next order in the
        order list can be picked.

        Arguments:
            time {int} -- seconds to be standby for
        """
        yield self.env.timeout(time)


def order_handler(
    env, order_number, order_time, skus_in_order, sku_quantities_in_order, aframe
):
    """Handles the input orders to the A-frame. First checks if the input order
    has happened yet. The order data is loaded from a file and the orders should not be
    able to be picked before they have "happened" in the simulation.
    If the next order is in the future for the simulation the A-frame will standby
    until it has reached that time.
    When an order is picked the A-frame is locked to that order and no other order
    can be processed while the A-frame picks the order.

    Arguments:
        env {env} -- simpy environment
        order_number {int} -- order number
        order_time {datetime} -- order datetime
        skus_in_order {list} -- sku list
        sku_quantities_in_order {list} -- sku quantities
        aframe {Aframe} -- A-frame class
    """

    if arrow.get(order_time) > arrow.get(env.now):
        time_diff = arrow.get(order_time) - arrow.get(env.now)
        yield env.process(aframe.standby(time_diff.seconds))
    wait_start = env.now
    with aframe.machine.request() as request:
        yield request
        yield env.process(
            aframe.pick(order_number, skus_in_order, sku_quantities_in_order)
        )
        wait_end = env.now


def save_aframe_info_to_file(aframe, date):
    """When running the simulation data is generated and saved in the Aframe class
    this method takes the data and saves it to different csv files for later
    analysis.

    Arguments:
        aframe {Aframe} -- Aframe class
    """
    # start by creating the necessary directories if they dont exist:
    try:
        os.makedirs("../generated_data/aframe_info")
    except FileExistsError:
        # directory already exists
        pass
    try:
        os.makedirs("../generated_data/aframe_info/" + date)
    except FileExistsError:
        # directory already exists
        pass

    with open(
        "../generated_data/aframe_info/" + date + "/channels_after_day.csv",
        "w",
        newline="",
    ) as csvfile:
        channelwriter = csv.writer(csvfile, delimiter=",")
        for channels in aframe.allocation.items():
            channelwriter.writerow(channels)

    with open(
        "../generated_data/aframe_info/" + date + "/total_picks_per_channel.csv",
        "w",
        newline="",
    ) as csvfile:
        channelwriter = csv.writer(csvfile, delimiter=",")
        for channels in aframe.total_picks_from_channel.items():
            channelwriter.writerow(channels)

    with open(
        "../generated_data/aframe_info/" + date + "/refills_per_channel.csv",
        "w",
        newline="",
    ) as csvfile:
        channelwriter = csv.writer(csvfile, delimiter=",")
        channelwriter.writerow(["sku", "num_refills"])
        for channels in aframe.channel_refills.items():
            channelwriter.writerow(channels)

    with open(
        "../generated_data/aframe_info/" + date + "/channel_refill_counter.csv",
        "w",
        newline="",
    ) as csvfile:
        channelwriter = csv.writer(csvfile, delimiter=",")
        for channels in aframe.channel_refill_counter.items():
            channelwriter.writerow(channels)

    with open(
        "../generated_data/aframe_info/" + date + "/orders_picked_by_aframe.csv",
        "w",
        newline="",
    ) as csvfile:
        aframewriter = csv.writer(csvfile, delimiter=",")
        for row in aframe.orders_picked:
            aframewriter.writerow([row])

    with open(
        "../generated_data/aframe_info/"
        + date
        + "/orders_that_were_stocked_out_in_aframe.csv",
        "w",
        newline="",
    ) as csvfile:
        aframewriter = csv.writer(csvfile, delimiter=",")
        for row in aframe.stocked_out_orders:
            aframewriter.writerow([row])


def get_order_list_and_pick_start_from_file(file):
    """Opens the order data from file. Assigns the first pick of the day to
    pick_start to keep track of the time.
    All the orders are put into an order list that is then returned
    the order list are all the orders picked for day

    Returns:
        list, string-- returns order list as a list and pick start time as a string
    """
    order_list = []
    pick_start = ""

    with open(file) as csvfile:
        testreader = csv.reader(csvfile, delimiter=",")
        next(testreader)  # skip header row
        for row in testreader:
            if not pick_start:
                pick_start = row[0]
            order_list.append(row)

    return order_list, pick_start


def assign_current_allocation_to_aframe_object(aframe):
    """Assigns the generated aframe product allocation to the aframe class.
    Reads the allocation from a file,
    adds the skus to the aframe's sku list for easy checking if something is
    in the aframe or not.
    Then assigns the named channels to their respective sku.
    Also fully stocks the frame, the skus are filled to max capacity.

    Arguments:
        aframe {Aframe} -- The Aframe class
    """
    with open("../generated_data/new_aframe_allocation_with_dimensions.csv") as csvfile:

        aframereader = csv.reader(csvfile, delimiter=",")
        # skip header row
        next(aframereader)
        for row in aframereader:
            # eval the string to an int.
            # is it saved as integers or str in the database?
            # this can create weird errors if the raw data is bad.
            aframe.add_sku(int(row[1]))
            if row[8]:
                if row[8] != "inf" and float(row[8]) >= 0:
                    # because data for articles is bad, only add data is positive
                    # and is not infinity
                    aframe.allocate_channels(int(row[0]), int(row[1]), float(row[8]))
                else:
                    raise Exception(
                        "sku dimensions contain bad data. Check the aframe allocation with dimensions file"
                    )
            else:
                # Then there is no sku loaded in the channel.
                # do nothing
                pass


def get_all_maybe_ok_skus_from_file():
    """Gets all the skus that have not been found to not fit in A-frame. Then adds them
    to two dictionaries and then return them.

    Returns:
        dict, dict -- Returns two dictionaries where the skus are keys
    """
    all_skus_missing = {}
    one_sku_missing = {}
    with open("../generated_data/maybe_ok_skus.csv") as csvfile:
        articlereader = csv.reader(csvfile, delimiter=",")
        # skip header row
        next(articlereader)
        for row in articlereader:
            all_skus_missing[int(row[0])] = 0
            one_sku_missing[int(row[0])] = 0
    return all_skus_missing, one_sku_missing


def save_missing_sku_info_to_file(all_skus_missing, one_sku_missing, date):
    """Takes the two dicts that are skus missing and saves them to a file
    for later data analysis

    Arguments:
        all_skus_missing {dict} -- a dict with the skus that blocked an
                                   order from being picked in the A-frame
        one_sku_missing {dict} -- a dict when the order was blocked by only one sku
    """
    with open(
        "../generated_data/aframe_info/" + date + "/missing_skus.csv", "w", newline=""
    ) as csvfile:
        skuwriter = csv.writer(csvfile, delimiter=",")
        skuwriter.writerow(["sku", "quantity"])
        for sku, quantity in sorted(
            all_skus_missing.items(), key=lambda p: p[1], reverse=True
        ):
            skuwriter.writerow([sku, quantity])
    with open(
        "../generated_data/aframe_info/" + date + "/only_one_missing_skus.csv",
        "w",
        newline="",
    ) as csvfile:
        skuwriter = csv.writer(csvfile, delimiter=",")
        skuwriter.writerow(["sku", "quantity"])
        for sku, quantity in sorted(
            one_sku_missing.items(), key=lambda p: p[1], reverse=True
        ):
            skuwriter.writerow([sku, quantity])


def save_aframe_general_stats_to_file(aframe, date, manual_picks):
    """Saves the general info to a csv file, will only have two rows

    Arguments:
        aframe {Aframe} -- The A-frame class
        date {string} -- A date string with the ISO-standard format
        manual_picks {integer} -- an integer that counts the manual picks, i.e. items that
        could not be picked in the A-frame.
    """

    with open(
        "../generated_data/aframe_info/" + date + "/general_stats.csv", "w", newline=""
    ) as csvfile:
        generalwriter = csv.writer(csvfile, delimiter=",")
        generalwriter.writerow(
            [
                "date",
                "usetime",
                "num_picks",
                "num_stockouts",
                "manual_picks",
                "automation_level",
                "total_refills",
                "failed_picks",
            ]
        )
        generalwriter.writerow(
            [
                date,
                aframe.total_picking_time,
                aframe.no_orders_picked,
                aframe.total_orders_that_were_stock_out,
                manual_picks,
                aframe.no_orders_picked
                / (
                    aframe.no_orders_picked
                    + manual_picks
                    + aframe.total_orders_that_were_stock_out
                ),  # this is orders picked divided by total orders
                aframe.total_refills,
                aframe.stocked_out_orders,
            ]
        )
