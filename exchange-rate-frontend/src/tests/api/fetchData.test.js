import mockedAxios from 'axios';
import { cleanup } from '@testing-library/react';

import { CURRENCY_URL } from '../../constants/url';
import fetchCurrencyData from '../../api/fetchCurrencyData';
import testData from './testData';

jest.mock('axios');
afterEach(cleanup);

test('axios been called', async () => {
	mockedAxios.get.mockResolvedValueOnce(testData);
	const data = await fetchCurrencyData();
	expect(mockedAxios.get).toHaveBeenCalledWith(CURRENCY_URL);
	expect(data).toBe(testData['data']);
});
