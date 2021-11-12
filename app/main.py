import asyncio
import json
import websockets
import numpy as np


class Vwap:
    def __init__(self, feed_url: str, coin_pairs: list[str], window_size: int = 200) -> None:
        """
        Class' constructor.

        coins_dict is initialized with some default values. sizes and prices' lists length must always have the same
        size as the window_size.

        idx must point to the oldest data point in the list, which will be the first one to be updated.

        Data points in sizes and prices must be seen as a continuous circular series, in which the first index (0) comes
        right after the last index (window_size - 1). This is done so in order to reuse indexes instead of deleting and
        re-appending them.

        :param feed_url: Url for the feed which streams the data to be analyzed.
        :param coin_pairs: List of coin pairs which will be analyzed and calculated.
        :param window_size: Amount of data point to be kept in the list used to calculate VWAP.
        :param coins_dict: Dictionary containing data for VWAP calculation on each coin pair.
        :param sub_msg: Json data sent to the feed channel upon subscription.
        """
        self.feed_url = feed_url
        self.coin_pairs = coin_pairs
        self.window_size = window_size
        self.coins_dict = {
            coin_pair: {
                'idx': 0, 'sizes': [0] * self.window_size, 'prices': [0] * self.window_size
            } for coin_pair in self.coin_pairs
        }
        self.sub_msg = json.dumps({'type': 'subscribe', 'product_ids': self.coin_pairs, 'channels': ['matches']})

    def vwap_calc(self, coin_pair: str) -> float:
        """
        Calculates VWAP for a given pair of coins.

        :param coin_pair: String containing the coin pair: e.g. BTC-USD
        :return: Calculated VWAP
        """
        size_list = self.coins_dict[coin_pair]['sizes']
        price_list = self.coins_dict[coin_pair]['prices']
        products_summation = sum(np.multiply(price_list, size_list))
        return round(products_summation / sum(size_list), ndigits=2)

    def data_insert(self, coin_pair: str, data_size: float, data_price: float) -> None:
        """
        Inserts data in the coins_dict.

        In order to keep time complexity as low as possible, an index is kept for each coin pair, under the 'idx' key,
        which is meant to point to the oldest data point. This was made so that the data at such index can be updated,
        with time complexity of O(1), instead of deleting an item and having all items to the right of it being moved
        to the left, with time complexity of O(n), plus O(1) for appending the newest item.
        Reference: https://wiki.python.org/moin/TimeComplexity

        :param coin_pair: String containing the coin pair: BTC-USD.
        :param data_size: Size/amount of the trade for the given coin pair.
        :param data_price: How much was paid on the trade for the given coin pair.
        :return:
        """
        insert_index = self.coins_dict[coin_pair]['idx']
        self.coins_dict[coin_pair]['sizes'][insert_index] = data_size
        self.coins_dict[coin_pair]['prices'][insert_index] = data_price
        self.coins_dict[coin_pair]['idx'] = insert_index + 1 if insert_index < self.window_size - 1 else 0

    async def run(self) -> None:
        """
        Main entry point for running the VWAP calculation.

        :return:
        """
        websocket = await websockets.connect(self.feed_url)
        await websocket.send(self.sub_msg)
        while True:
            data = json.loads(await websocket.recv())
            coin_pair = data.get('product_id')
            if not coin_pair:
                continue

            self.data_insert(data['product_id'], float(data['size']), float(data['price']))
            vwap_value = self.vwap_calc(coin_pair)

            print(coin_pair, vwap_value)

        await websocket.close()


if __name__ == '__main__':
    vwap = Vwap('wss://ws-feed.exchange.coinbase.com', ['BTC-USD', 'ETH-USD', 'ETH-BTC'])
    asyncio.run(vwap.run())
