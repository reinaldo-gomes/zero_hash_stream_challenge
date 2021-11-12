import pytest

from app.main import Vwap
import websockets
from unittest.mock import AsyncMock
import json


def test_vwap_calc():
    vwap = Vwap('', [])
    vwap.coins_dict.update({'pair1': {'idx': 0, 'sizes': [1, 1.5, 2], 'prices': [1, 2, 3]}})
    vwap.coins_dict.update({'pair2': {'idx': 0, 'sizes': [2, 1.5, 1], 'prices': [1, 2, 3]}})

    assert vwap.vwap_calc('pair1') == 2.22
    assert vwap.vwap_calc('pair2') == 1.78


def test_data_insert():
    """
    Asserts that the newest entries in the lists are replacing the oldest ones, from left to right, then back from the
    first element again upon reaching the last element
    """
    vwap = Vwap('', ['pair1'], window_size=3)
    index_list = [0, 1, 2, 0]
    data_sizes = [1, 2, 3, 4]
    data_prices = [4, 3, 2, 1]
    data_list = zip(index_list, data_sizes, data_prices)

    for item in data_list:
        assert vwap.coins_dict['pair1']['idx'] == index_list[item[0]]
        vwap.data_insert('pair1', item[1], item[2])
    assert vwap.coins_dict['pair1']['sizes'] == [4, 2, 3]
    assert vwap.coins_dict['pair1']['prices'] == [1, 3, 2]


async def test_run(mocker, capfd):
    #mocked_recv = AsyncMock()
    #mocked_recv.recv.return_value = coin_data
    #mocked_wobsockets = asyncio.Future()
    #mocked_wobsockets.set_result(mocked_recv)
    mocker.patch.object(websockets, 'connect', side_effect=AsyncMock())
    coin_data = {'product_id': 'pair1', 'size': 1.5, 'price': '2.5'}
    mocker.patch.object(json, 'loads', side_effect=[{}, coin_data, StopAsyncIteration])
    mocker.patch.object(Vwap, 'data_insert')

    vwap = Vwap('fake_url', ['pair1'], window_size=3)
    with pytest.raises(StopAsyncIteration):
        await vwap.run()
    out, err = capfd.readouterr()

    assert vwap.sub_msg == json.dumps({'type': 'subscribe', 'product_ids': ['pair1'], 'channels': ['matches']})
    websockets.connect.assert_called_with('fake_url')
    vwap.data_insert.assert_called_with(coin_data['product_id'], float(coin_data['size']), float(coin_data['price']))
    assert out == 'pair1 nan\n'
