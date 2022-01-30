import axios from 'axios';
import { CURRENCY_URL } from '../constants/url';

const fetchCurrencyData = async (params) => {
	return axios
		.get(CURRENCY_URL)
		.then((res) => res.data)
		.catch((err) => err);
};

export default fetchCurrencyData;
