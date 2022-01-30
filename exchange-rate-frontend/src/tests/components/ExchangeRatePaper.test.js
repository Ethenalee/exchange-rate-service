import { render, screen, cleanup, waitForElement } from '@testing-library/react';
import { waitFor } from '@testing-library/dom';

import mockedAxios from 'axios';

import { CURRENCY_URL } from '../../constants/url';
import testData from '../api/testData';
import ExchangeRatePaper from '../../components/ExchangeRatePaper';

jest.mock('axios');
afterEach(() => cleanup)

test('render ExchangeRatePaper call axios', async () => {
	mockedAxios.get.mockResolvedValueOnce({data: testData});
	render(<ExchangeRatePaper />);
	expect(mockedAxios.get).toHaveBeenCalledWith(CURRENCY_URL);
	expect(mockedAxios.get).toHaveBeenCalledTimes(1);

});
