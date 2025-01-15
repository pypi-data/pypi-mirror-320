import asyncio
from datasette_enrichments import Enrichment
from datasette import hookimpl
from wtforms import Form, FloatField
import random


@hookimpl
def register_enrichments():
    return [SlowEnrichment()]


class SlowEnrichment(Enrichment):
    name = "Slow"
    slug = "slow"
    description = "An enrichment on a slow loop to help debug progress bars"
    batch_size = 1

    async def initialize(self, datasette, db, table, config):
        pass

    async def get_config_form(self, db, table):
        class ConfigForm(Form):
            delay = FloatField(
                "Delay (seconds)",
                description="How many seconds to delay for each row",
                default=0.1,
            )
            error_rate = FloatField(
                "Error rate",
                description="What portion of rows should be errors? Between 0 and 1.0",
                default=0,
            )

        return ConfigForm

    async def enrich_batch(
        self,
        db,
        table,
        rows,
        pks,
        config,
    ):
        error_rate = config.get("error_rate") or 0
        for row in rows:
            if error_rate and random.random() < error_rate:
                raise ValueError("Error rate")
            await asyncio.sleep(config["delay"])
