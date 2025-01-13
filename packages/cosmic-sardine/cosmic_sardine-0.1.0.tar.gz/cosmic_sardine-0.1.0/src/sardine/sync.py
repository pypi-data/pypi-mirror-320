
from typing import List, Tuple
from ._sardine.sync import *
from ._sardine.managed import Managed

def create_barrier(managed: Managed, name: str, waiters_config: List[WaiterConfig], notifiers_config: List[NotifierConfig]) -> Tuple[Barrier, List[Waiter], List[Notifier]]:
    barrier = managed.force_create(Barrier, name, waiters_config, notifiers_config)

    waiters = list(map(lambda config: Waiter(barrier, config), waiters_config))

    notifiers = list(map(lambda config: Notifier(barrier, config), notifiers_config))

    return barrier, waiters, notifiers

def create_barrier_1_to_1(managed: Managed, name: str, sleep = False) -> Tuple[Barrier, Waiter, Notifier]:
    waiter_config = WaiterConfig(sleep = sleep)

    # Since it is alone, no need to wait
    notifier_config = NotifierConfig(sleep = False)

    res = create_barrier(managed, name, [waiter_config], [notifier_config])

    return res[0], res[1][0], res[2][0]
