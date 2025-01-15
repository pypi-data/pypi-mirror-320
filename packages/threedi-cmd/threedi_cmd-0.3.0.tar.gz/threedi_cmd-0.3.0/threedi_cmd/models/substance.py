from asyncio import Queue

from threedi_api_client.openapi.models import Simulation, Substance

from .base import EventWrapper


class SubstanceWrapper(EventWrapper):
    model = Substance
    api_path: str = "substance"
    scenario_name = model.__name__.lower()

    async def execute(self, queue: Queue, steps: list) -> list:
        """Create the substance and insert the id into the steps"""
        self.api_substance = self.save()
        return self.insert_substance_id_for_steps(steps)

    def save(self) -> Substance:
        """Create the substance"""
        assert isinstance(self.simulation, Simulation)
        return self._api_client.simulations_substances_create(
            self.simulation.id, self.instance
        )

    def insert_substance_id_for_steps(self, steps: list) -> list:
        """
        Substitute the substance id back into the steps.
        Loop over steps and find substance events with the same id as the instance
        """
        new_steps = []
        for sim_step in steps:
            if hasattr(sim_step.instance, "substances") and isinstance(
                sim_step.instance.substances, list
            ):
                for i, substance in enumerate(sim_step.instance.substances):
                    if substance["substance"] == self.instance.id:
                        sim_step.instance.substances[i]["substance"] = (
                            self.api_substance.id
                        )
            new_steps.append(sim_step)

        return new_steps


WRAPPERS = [SubstanceWrapper]
