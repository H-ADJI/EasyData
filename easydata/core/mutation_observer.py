'''
File: mutation_observer.py
File Created: Wednesday, 16th November 2022 9:52:27 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from playwright.async_api import Locator
from typing import List
import asyncio
from easydata.services.aio_object import AioObject


class MutationObserver(AioObject):
    """Observes a DOM node for changes

        Currently only support nodes count changes ( detect changes in a node is added or removed )

        May handle text or attributes changes later
    """
    async def __init__(self, target_element: Locator, configuration: tuple = None) -> None:
        self.configuration = configuration
        self.target_element = target_element
        self.element_count = await self.target_element.count()

    async def scan(self) -> List[str]:
        """scan the DOM tree for any node mutation and changes (attribute changes, new nodes, text changes)

        Returns:
            List[str]: listing of mutations that where observed
        """
        mutations = []
        new_count = await self.target_element.count()
        if self.element_count != new_count:
            self.element_count = new_count
            mutations.append("ELEMENT_COUNT")
        return mutations

    async def resolve(self, mutations: list = None, repeat: int = 3, wait_time: float = 0.5) -> bool:
        """Determine whether or not a mutation has happened and returns if boolean value accordingly

        Args:
            mutations (list, optional): list of the mutations that were observed. Defaults to None.
            repeat (int, optional): number of repitions before resolving to False (Equivilent to TTL). Defaults to 3.
            wait_time (float, optional): delay that grows exponentially for each repetition to certain limit  `max_wait_time = wait_time*2^(repeat-1)` `Total_wait_time = wait_time*(2^repeat-1)` . Defaults to 0.5.

        Returns:
            bool: whether the observer detected changes on the DOM or not 
        """
        if not mutations:
            if repeat > 0:
                await asyncio.sleep(wait_time)
                # retrying with an exponential backoff with a repetition limit, could implement also a time limit
                resolved = await self.resolve(mutations=await self.scan(), repeat=repeat-1, wait_time=wait_time*2)
                if resolved:
                    return True
            else:
                return False
        elif mutations:
            return True

    @staticmethod
    async def get_all_attributes(element: Locator) -> dict:
        """Extract all attribute from an HTML node, since playwright only allow single attribute extraction 

        Args:
            element (Locator): targeted element

        Returns:
            dict: attributes dictionary  
        """
        element_attrs_names = await element.evaluate("el => el.getAttributeNames()")
        return {attr_name: await element.get_attribute(attr_name) for attr_name in element_attrs_names}
